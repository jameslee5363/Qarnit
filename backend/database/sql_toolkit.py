from config.db_config import db
from config.llm_config import llm
from langchain_community.agent_toolkits import SQLDatabaseToolkit


def make_sql_tools():
    """
    Instantiate and return the list of SQLDatabaseToolkit tools bound to db and llm.
    """
    toolkit = SQLDatabaseToolkit(db=db, llm=llm)
    return toolkit.get_tools()