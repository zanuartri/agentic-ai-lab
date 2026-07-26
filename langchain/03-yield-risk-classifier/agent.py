import os

from dotenv import load_dotenv
from langchain_openai import ChatOpenAI
from langchain.agents import create_agent
from langchain.agents.structured_output import ToolStrategy

from tools import get_top_yields
from schema import PoolRiskAssessments

load_dotenv()

llm = ChatOpenAI(
    model=os.environ.get("LLM_MODEL"),
    base_url=os.environ.get("LLM_BASE_URL"),
    api_key=os.environ.get("LLM_API_KEY"),
)

executor = create_agent(
    model=llm,
    tools=[get_top_yields],
    system_prompt=(
        "You are a DeFi risk analyst. Use get_top_yields to fetch pool data, "
        "then assess the risk of the pool the user asks about. Consider APY "
        "magnitude (extremely high APY is a red flag, not a bonus), TVL "
        "(low TVL means low liquidity/higher risk), and stability signals."
        "For pool_name, use the project name and symbol together" 
        "(e.g. 'saturn SUSDAT'), not the raw pool ID."
    ),
    response_format=ToolStrategy(PoolRiskAssessments)
)