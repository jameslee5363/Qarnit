from state import AgentState
from llm_manager import LLMManager
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import JsonOutputParser
import pandas as pd

class PreprocessorAgent(Agent):
    """
    The PreprocessorAgent handles:
      1) Suggesting generic preprocessing steps for a loaded DataFrame
      2) Taking a user instruction, checking relevance, generating Pandas code,
         executing it, and updating the DataFrame in state.
    """

    def __init__(self):
        super().__init__()
        self.llm_manager = LLMManager()

    def run(self, state: AgentState) -> AgentState:
        # Retrieve DataFrame from state
        df: pd.DataFrame = state.retrieved_df or pd.DataFrame()
        if df is None:
            state.add_message("⚠️ No DataFrame found to preprocess. Please load or retrieve a DataFrame first.")
            return state

        # Get the latest user input
        user_instr: str = state.latest_user_input.strip()
        lower = user_instr.lower()

        # If user is asking for suggestions
        if any(keyword in lower for keyword in ("suggest", "what preprocessing", "help", "recommend")):
            suggestions = self.suggest_preprocessing_methods(df)
            state.add_message(suggestions)
            return state

        # Otherwise treat input as a preprocessing instruction
        result = self.parse_preprocessing_instructions(user_instr, df)

        # Check relevance
        if not result.get("is_relevant", False):
            issues = result.get("issues") or "Instruction deemed not relevant to the DataFrame."
            state.add_message(f"❌ Instruction not relevant: {issues}")
            return state

        code = result.get("python_code")
        if not code:
            state.add_message("⚠️ No code was generated for the instruction.")
            return state

        # Execute generated code
        try:
            new_df = self.apply_preprocessing_code(code, df)
            state.data["df"] = new_df
            state.add_message(f"✅ Preprocessing applied successfully.\n```python{code}```")
        except Exception as e:
            state.add_message(f"❌ Error executing generated code: {e}")

        return state


    ##== Helper Methods

    def suggest_preprocessing_methods(self, df: pd.DataFrame) -> str:
        """
        Ask the LLM to look at the DataFrame schema/stats and suggest possible transformations.
        Return a short string with suggestions.
        """
        # Convert DataFrame info (like dtypes, sample rows, etc.) into a concise string
        # CHANGED: Convert dictionary to string and escape curly braces to avoid format errors.
        dtypes_str = str(df.dtypes.to_dict()).replace("{", "{{").replace("}", "}}")  # CHANGED
        sample_data_str = str(df.head(5).to_dict(orient="records")).replace("{", "{{").replace("}", "}}")  # CHANGED

        # For big DataFrames, you might want to sample fewer rows
        info_for_prompt = f"""
        DataFrame columns and types: {dtypes_str}
        First 5 rows:
        {sample_data_str}
        """

        # Build a prompt
        prompt = ChatPromptTemplate.from_messages([
            (
                "system",
                """You are a data-cleaning and preprocessing expert. 
                   The user has a Pandas DataFrame loaded in memory.
                   Your job is to suggest potentially useful data cleaning or preprocessing steps.
                   Look at the columns, data types, and sample rows. 
                   Summarize what might be done, such as dropping nulls, normalizing columns, 
                   removing outliers, encoding categorical variables, etc.
                   Return a concise text message with your suggestions. 
                   Do NOT generate code here—just a short summary of suggestions.
                """
            ),
            ("human", f"DataFrame info:\n{info_for_prompt}\n\nWhat preprocessing steps do you suggest?")
        ])

        suggestions = self.llm_manager.invoke(prompt)
        return suggestions.strip()


    def parse_preprocessing_instructions(self, user_instructions: str, df: pd.DataFrame) -> dict:
        """
        Sends the user's instructions to the LLM to produce *Python code* that modifies the DataFrame.
        - If the user instructions are not relevant or not feasible, set \"is_relevant\" to false.
        - If there's a potential error or you can't fulfill the request, set \"issues\" with an explanation.
        We ask for a JSON structure with fields:

            Provide your answer in JSON. For example:
            {{
              "is_relevant": true,
              "issues": null,
              "python_code": "df['mycol'] = df['mycol'].fillna(0)"
            }}

        Enhancements:
        - Passes the list of DataFrame columns to the LLM.
        - Reformats ambiguous instructions by matching natural language to actual column names.
        """
        # List and format the DataFrame columns
        columns = df.columns.tolist()
        columns_str = ", ".join(columns)

        # Simple reformat: normalize instruction to match column names
        instr_clean = user_instructions.strip()
        # Attempt to match any column by removing spaces/underscores
        for col in columns:
            norm_col = col.replace('_', '').lower()
            if norm_col in instr_clean.replace(' ', '').lower():
                instr_clean = instr_clean.replace(col, col)  # ensure exact match if present
        # Build the prompt with columns context
        prompt = ChatPromptTemplate.from_messages([
            ("system", f"""
            You are a data preprocessing agent. The user will give you instructions
            on how to transform or clean a Pandas DataFrame already loaded in memory as `df`.
            The DataFrame has the following columns: {columns_str}.
            - You must return valid Python code that modifies the DataFrame in place OR
              returns a new DataFrame, if needed.
            - If the user instructions are not relevant or not feasible, set \"is_relevant\" to false.
            - If there's a potential error or you can't fulfill the request, set \"issues\" with an explanation.
            - Otherwise, return \"python_code\" that can be executed safely.

            Provide your answer in JSON. For example:
            {{{{ 
            "is_relevant": true,
            "issues": null,
            "python_code": "df['mycol'] = df['mycol'].fillna(0)"
            }}}}

            The code MUST assume `df` is already in scope as a Pandas DataFrame.
            If user wants to drop rows, check they exist. If you see potential errors, handle them or note them.

            Do NOT access any SQL or database. Only manipulate the DataFrame `df`.
            """),
            ("human", f"Columns: {columns_str}\nUser instructions: {instr_clean}")
        ])

        output_parser = JsonOutputParser()
        llm_response = self.llm_manager.invoke(prompt)

        try:
            parsed = output_parser.parse(llm_response)
        except Exception as e:
            parsed = {
                "is_relevant": False,
                "issues": f"Could not parse LLM JSON: {str(e)}",
                "python_code": None
            }

        return {
            "is_relevant": parsed.get("is_relevant", False),
            "issues": parsed.get("issues"),
            "python_code": parsed.get("python_code")
        }

    def apply_preprocessing_code(self, code_str: str, df: pd.DataFrame) -> pd.DataFrame:
        """
        Actually run the Python code from the LLM in a controlled environment.
        We'll do a simple `exec` in Python. 
        """
        local_env = {"df": df}
        exec(code_str, {}, local_env)

        new_df = local_env.get("df")
        if not isinstance(new_df, pd.DataFrame):
            raise RuntimeError("LLM code did not produce a valid DataFrame named `df`.")

        return new_df