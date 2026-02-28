
from langchain.agents import create_agent
from langchain_openai import ChatOpenAI
from langchain_core.runnables import RunnableConfig


from dotenv import load_dotenv

from src.agent.prompt import apply_prompt_template
from src.community.tools import web_search_tool, web_fetch_tool
from src.tools.builtins.clarification_tool import ask_clarification_tool

load_dotenv()
model = ChatOpenAI(
    model="gpt-4o-mini",
    base_url='https://ai.keep.fm/v1/',
    temperature=0.1,
    max_tokens=1000,
    timeout=30
    # ... (other params)
)


# Define the graph
def make_lead_agent(config: RunnableConfig):
    return create_agent(
        model,
        tools=[web_search_tool, web_fetch_tool, ask_clarification_tool],
        system_prompt=apply_prompt_template()
    )
