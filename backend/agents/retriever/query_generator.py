from config.db_config import db
from config.db_config import DB_PATH
from langchain_core.messages import AIMessage
from database.sql_toolkit import make_sql_tools
from config.llm_config import llm

# prompt for generating queries
_generate_query_system_prompt = """
You are an agent designed to interact with a SQL database.
Given an input question, create a syntactically correct {dialect} query to run,
then look at the results of the query and return the answer. Unless the user
specifies a specific number of examples they wish to obtain, always limit your
query to at most {top_k} results.

Never query all columns; only select relevant ones.
Do NOT perform any DML statements (INSERT/UPDATE/DELETE/DROP).
""".format(
    dialect=db.dialect,
    top_k=5,
)

# pull in the run_query tool
_tools = make_sql_tools()
_run_query_tool = next(t for t in _tools if t.name == "sql_db_query")

def generate_query(state):
    """
    Sub-agent: constructs and executes a SQL query from user intent.
    """
    system_message = {
        "role": "system", 
        "content": _generate_query_system_prompt
    }
    
    llm_with_tools = llm.bind_tools([_run_query_tool])
    # feed system + conversation messages
    response = llm_with_tools.invoke([system_message] + state["messages"])
    return {"messages": [response]}