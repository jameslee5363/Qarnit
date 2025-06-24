import os
from dotenv import load_dotenv
from langchain_openai import AzureChatOpenAI
from pydantic import SecretStr

load_dotenv()

api_key = os.getenv("AZURE_OPENAI_API_KEY")
azure_endpoint = os.getenv("AZURE_OPENAI_ENDPOINT")
model = os.getenv("AZURE_OPENAI_DEPLOYMENT_NAME")
api_version = os.getenv("AZURE_OPENAI_API_VERSION")

if api_key is None:
    raise ValueError("AZURE_OPENAI_API_KEY environment variable is not set")
    
llm = AzureChatOpenAI(
    azure_endpoint = azure_endpoint,
    api_key = SecretStr(api_key),
    model = model,
    api_version = api_version
)
