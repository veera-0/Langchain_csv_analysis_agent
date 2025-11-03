import asyncio
import os
from dotenv import load_dotenv

from langchain_mcp_adapters.tools import load_mcp_tools
from langchain_openai import AzureChatOpenAI
from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client
from langchain.agents import create_agent
from langchain_core.messages import SystemMessage, HumanMessage

load_dotenv()

SYSTEM_PROMPT = (
    "You are an expert data analyst working with a CSV dataset. "
    "You have access to various tools to analyze and summarize the data. "
    "Use the tools as needed to answer questions about the dataset."
)

User_PROMPT = (
    "Analyze the provided CSV data and answer the following question:\n"
    "{question}\n"
    "Use the available tools to gather information and provide a detailed response."
)

class CsvAgent:
    def __init__(self):
        self.model = self._initialize_model()
        self.server_params = self._initialize_server_params()
    
    def _initialize_model(self) -> AzureChatOpenAI:
        """inititlizing the model and returning it"""
        azure_endpoint = os.getenv("API_BASE")
        api_key = os.getenv("API_KEY")
        api_version = os.getenv("API_VERSION", "2023-03-15-preview")
        deployment_name = os.getenv("DEPLOYMENT_NAME", "gpt-4o")

        return AzureChatOpenAI(
            azure_endpoint=azure_endpoint,
            api_version=api_version,
            api_key=api_key,
            azure_deployment=deployment_name,
            temperature=0,
        )

    def _initialize_server_params(self) -> StdioServerParameters:
        """initializing the server parameters and returning them"""
        server_script_path = r"..\mcp_server\csv.server.py"
        return StdioServerParameters(
            command="python",
            args=[server_script_path]
        )
    
    async def _initialize_tools(self, session: ClientSession) -> list:
        await session.initialize()
        tools = await load_mcp_tools(session)
        return tools
    
    async def analyze_csv(self, question: str) -> str:
        async with stdio_client(self.server_params) as (read, write):
            async with ClientSession(read,write) as client_session:
                tools = await self._initialize_tools(client_session)
                
                agent = create_agent(
                    llm=self.model,
                    tools=tools,
                )
                
                response = await agent.ainvoke(
                    {
                        "messages": [
                            SystemMessage(content=SYSTEM_PROMPT),
                            HumanMessage(content=User_PROMPT.format(question=question))
                        ]
                    }
                )
                return response

async def main():
    analyst = CsvAgent()
    question = "What is the average age of passengers grouped by their passenger class?"
    response = await analyst.analyze_csv(question)
    print("Response from CSV Agent:")
    print(response)

if __name__ == "__main__":
    asyncio.run(main())

    
