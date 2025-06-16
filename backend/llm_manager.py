from langchain_core.prompts import ChatPromptTemplate
from langchain_openai import AzureChatOpenAI

class LLMManager:
    def __init__(self):
        self.llm = AzureChatOpenAI(
            azure_endpoint="...",
            api_key="...",
            api_version="..."
        )

    def invoke(self, prompt, **kwargs) -> str:
        if hasattr(prompt, "format_messages"):
            messages = prompt.format_messages(**kwargs)
        else:
            messages = [{"role": "user", "content": prompt}]
            
        response = self.llm.invoke(messages)
        return response.content
