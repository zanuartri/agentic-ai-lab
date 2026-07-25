import os

from dotenv import load_dotenv
from langchain_openai import ChatOpenAI
from langchain.agents import create_agent

from tools import get_top_yields

load_dotenv()

llm = ChatOpenAI(
    model=os.environ.get("LLM_MODEL", "deepseek-v4-flash"),
    base_url=os.environ.get("LLM_BASE_URL", "https://opencode.ai/zen/go/v1"),
    api_key=os.environ.get("LLM_API_KEY")
)

tools = [get_top_yields]

executor = create_agent(
    model=llm,
    tools=tools,
    system_prompt="You are a DeFi yield research assistant. Use the get_top_yields tool to answer questions about pool APYs, TVL, and chains. Always call the tool rather than guessing numbers.",
)