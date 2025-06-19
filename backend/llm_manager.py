from langchain_core.prompts import ChatPromptTemplate
from langchain_openai import AzureChatOpenAI
from pydantic import SecretStr

class LLMManager:
    def __init__(self):
        self.llm = AzureChatOpenAI(
            azure_endpoint="https://qarnit-lucia-demo.openai.azure.com/openai/deployments/gpt-4.1-nano/chat/completions?api-version=2025-01-01-preview",
            api_key=SecretStr("xfnUma2MdNuO3HlkjbtxVTurM7aTzIzJqZFs7EuwOA7EYzuMDps0JQQJ99BFACHYHv6XJ3w3AAABACOGeyWV"),
            api_version="2025-04-14"
        )

    def invoke(self, prompt, **kwargs) -> str:
        if hasattr(prompt, "format_messages"):
            messages = prompt.format_messages(**kwargs)
        else:
            messages = [{"role": "user", "content": prompt}]
            
        response = self.llm.invoke(messages)
        content = response.content
        
        # Handle case where content might be a list
        if isinstance(content, list):
            return " ".join(str(item) for item in content)
        return str(content)
