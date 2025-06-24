from agent import Agent
from state import AgentState
from database_manager import DatabaseManager
from llm_manager import LLMManager
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import JsonOutputParser
import pandas as pd
import re

class RetrieverAgent(Agent):
    def __init__(self):
        super().__init__()
        self.db_manager  = DatabaseManager()
        self.llm_manager = LLMManager()
        self.schema = self.db_manager.get_schema()   # Since our database is static

    def run(self, state: AgentState) -> AgentState:
        # 1) Intent & relevance
        state.is_relevant = self._assess_relevance(state.question, self.schema)
        if not state.is_relevant:
            return state

        # 2) Parse question → identify tables & columns
        state.parsed_question = self._extract_relevant_tables(
            state.question,
            schema=self.schema
        )

        # 3–5) Build & validate SQL in a loop, up to MAX_SQL_ATTEMPTS times
        MAX_SQL_ATTEMPTS = 3
        attempt = 0

        # initialize issues to None for the first build
        issues = None

        while attempt < MAX_SQL_ATTEMPTS:
            # build SQL (on retry, pass any validation issues back into the builder)
            state.sql_query = self._build_sql(
                schema=self.schema,
                parsed=state.parsed_question,
                question=state.question,
                issues=issues or ""
            )

            state.sql_query = self._strip_markdown_fences(state.sql_query)

            # validate
            state.sql_query, state.sql_valid, state.sql_issues = self._validate_sql(
                sql_query=state.sql_query,
                schema=self.schema
            )

            # if valid, exit loop
            if state.sql_valid:
                break

            # otherwise, capture issues and retry
            issues = state.sql_issues
            attempt += 1


        # 6) Execute & load when valid
        if state.sql_valid:
            result = self.db_manager.execute_query(state.sql_query or "")
            if "error" in result:
                state.raw_results  = []
                state.retrieved_df = pd.DataFrame()
            else:
                cols = result["columns"]
                rows = result["rows"]
                state.raw_results  = [dict(zip(cols, row)) for row in rows]
                state.retrieved_df = pd.DataFrame(state.raw_results)
        else:
            state.raw_results  = []
            state.retrieved_df = pd.DataFrame()

        return state

    ##== Helper Methods
    def _strip_markdown_fences(self, sql: str) -> str:
        """
        If `sql` is wrapped in ``` or ```sql fences, remove those fences;
        otherwise return it unchanged.  Backticks around identifiers are preserved.
        """
        pattern = r"^\s*```(?:sql)?\s*([\s\S]*?)\s*```\s*$"
        m = re.match(pattern, sql.strip(), flags=re.IGNORECASE)
        return m.group(1) if m else sql
    
    def _assess_relevance(self, question: str, schema: str) -> bool:
        prompt = ChatPromptTemplate.from_messages([
        ("system", '''
        You are an AI assistant that decides whether a user's question is answerable using this SQL database.
        Given only the database schema and the user's question, respond with exactly one word:  
        - "true" if the question is relevant to the schema and can be answered with SQL  
        - "false" otherwise
        '''),
                ("human", '''
        Database schema:
        {schema}

        User question:
        {question}

        Is this question answerable using the database?  
        '''),
            ])
        resp = self.llm_manager.invoke(prompt, schema=schema, question=question)
        return resp.strip().lower() == "true"
    
    def _extract_relevant_tables(self, question: str, schema: str) -> dict:
        prompt = ChatPromptTemplate.from_messages([
        ("system", '''
        You are an AI assistant that identifies which tables and columns are required to answer a user's question.
        Given the database schema and the user's question, return a JSON object with exactly this shape:
        
        {{
            "relevant_tables": [
                {{
                "table_name": string,
                "columns": [ string, ... ]
                }},
                …
            ]
        }}
         
        - Only include tables/columns directly needed to answer the question.  
        - Do NOT include any extra keys.  
        - If no tables apply, return {{ "relevant_tables": [] }}.
        '''),
                ("human", '''
        ===Database schema:
        {schema}

        ===User question:
        {question}

        Identify relevant tables and columns:
        '''),
            ])
        resp = self.llm_manager.invoke(prompt, question=question, schema=schema)
        return JsonOutputParser().parse(resp)

    def _build_sql(self, schema: str, parsed: dict, question: str, issues: str) -> str:
        """
        If `issues` is None: generate fresh SQL from question + parsed.
        If `issues` is nonempty: ask the LLM to correct the prior SQL
        by including the reported issues.
        """

        prompt = ChatPromptTemplate.from_messages([
        ("system", '''
        You are an AI assistant that generates SQL queries based on user questions, database schema, and extracted relevant tables and columns. 
        Generate a valid SQL query to answer the user's question. If there is not enough information to write a SQL query, respond with "NOT_ENOUGH_INFO".
        - Only use the tables and columns listed in the extracted relevant tables and columns.
        - Enclose all identifiers (table & column names) in backticks if they contain spaces or special characters.
        - Do not include explanatory text—return *only* the SQL.
         
        Here are some examples:

        1. What is the most recent transaction?
        Answer: SELECT * FROM `procurement_orders` WHERE `Created on` = MIN(`Created on`)

        2. Who is the supplier of any transaction that is greater than 1000 USD. 
        Answer: SELECT * FROM procurement_orders WHERE `Amount, USD` > 1000.

        3. Who are the most frequent initiator of the transaction and what is the total amount they have initiated?
        Answer: SELECT `Created by`, SUM(`Amount, USD`) AS total_amount_usd, SUM(`Amount, Local`) AS total_amount_local, COUNT(`Created by`) AS num_transaction FROM procurement_orders GROUP BY `Created by`ORDER BY num_transaction DESC;

        4. Do you find any relationship between approver and creator?
        Answer: SELECT `Approved by`, `Created by`, COUNT(`PO Name`) AS app_crt_pair_count FROM procurement_orders GROUP BY `Approved by`, `Created by`
        '''),
                ("human", '''
        ===Database schema:
        {schema}

        ===User question:
        {question}
                 
        ===SQL validation issues:
        {issues}

        If there is SQl validation issues, generate a corrected SQL query.
        If not, generate the SQL query:
        '''),
            ])

        raw_sql = self.llm_manager.invoke(
            prompt,
            schema=schema,
            parsed=parsed,
            question=question,
            issues=issues or ""
        )
        return raw_sql.strip()
    
    def _validate_sql(self, sql_query: str, schema: str) -> tuple[str,bool,str]:
        prompt = ChatPromptTemplate.from_messages([
        ("system", '''
        You are an AI assistant that checks and, if needed, corrects SQL queries against a given database schema.
        Return a JSON object with exactly these fields:
         
        {{
            "valid": boolean,
            "issues": string or null,
            "corrected_query": string or null
        }}
         
        - Ensure all table and column names are correctly spelled and exist in the schema. All the table and column names should be enclosed in backticks.
        - If the SQL is valid, set "valid": true and both other fields null.
        - If it's invalid, set "valid": false, explain the issues in "issues", and supply a fixed SQL in "corrected_query".
        
        For example:
        1. {{
            "valid": true,
            "issues": null,
            "corrected_query": null
        }}
                    
        2. {{
            "valid": false,
            "issues": "Column random does not exist",
            "corrected_query": "SELECT * FROM `procurement_orders` WHERE random > '08-01-2023'"
        }}
        '''),
                ("human", '''
        ===Database schema:
        {schema}
        
        ===SQL to validate:
        {sql_query}

        Respond with the JSON:
        '''),
            ])
         
        raw = self.llm_manager.invoke(prompt, sql_query=sql_query, schema=schema)
        result = JsonOutputParser().parse(raw)
        
        valid = result.get("valid", False)
        issues = result.get("issues") or ""
        corrected = result.get("corrected_query") or sql_query

        return corrected, valid, issues