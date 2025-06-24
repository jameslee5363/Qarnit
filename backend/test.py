from agents.retriever_agent import RetrieverAgent
from agents.state import AgentState
from database_manager import DatabaseManager


# Helper to run questions
def ask(question: str):
    agent = RetrieverAgent()
    state = AgentState(question=question)
    state = agent.run(state)

    print("🗣️  Question :", question)
    print("✅ Relevant  :", state.is_relevant)
    print("📝 SQL       :\n", state.sql_query)

    if state.retrieved_df is not None:
        state.retrieved_df.head()
    else:
        print("⚠️  No rows returned.")
 

# Example 1
ask("Which POs have distribution lines exceeding $10,000 USD, and who approved them?")








