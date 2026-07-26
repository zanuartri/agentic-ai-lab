import os
import sqlite3

from dotenv import load_dotenv
from langchain_openai import ChatOpenAI
from langchain.agents import create_agent
from langgraph.checkpoint.sqlite import SqliteSaver

from tools import get_top_yields

load_dotenv()

llm = ChatOpenAI(
    model=os.environ.get("LLM_MODEL", "deepseek-v4-flash"),
    base_url=os.environ.get("LLM_BASE_URL", "https://opencode.ai/zen/go/v1"),
    api_key=os.environ.get("LLM_API_KEY")
)

conn = sqlite3.connect("checkpoints.db", check_same_thread=False)
checkpointer = SqliteSaver(conn)
checkpointer.setup()

executor = create_agent(
    model=llm,
    tools=[get_top_yields],
    system_prompt="You are a DeFi yield research assistant with memory of the current conversation. Use the get_top_yields tool to answer questions about pool APYs, TVL, and chains. Always call the tool rather than guessing numbers.",
    checkpointer=checkpointer,
)
