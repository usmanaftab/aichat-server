from langchain.chat_models import init_chat_model
from typing import Annotated

from typing_extensions import TypedDict

from langgraph.graph import StateGraph, START
from langgraph.graph.message import add_messages
from langchain_tavily import TavilySearch
from langgraph.prebuilt import ToolNode, tools_condition

from app.utils.logger import get_logger

logger = get_logger(__name__)


class State(TypedDict):
    # Messages have the type "list". The `add_messages` function
    # in the annotation defines how this state key should be updated
    # (in this case, it appends messages to the list, rather than overwriting them)
    messages: Annotated[list, add_messages]


def chatbot(state: State):
    return {"messages": [llm_with_tools.invoke(state["messages"])]}


logger.info("Initializing TavilySearch tool")

tool = TavilySearch(max_results=2)
tools = [tool]

logger.info("Initializing chat model")
llm = init_chat_model(
    "eu.amazon.nova-micro-v1:0",
    model_provider="bedrock",
    region_name="eu-west-1",
)

logger.info("Binding tools to the chat model")
llm_with_tools = llm.bind_tools(tools)

logger.info("Creating chatbot node")
graph_builder = StateGraph(State)
graph_builder.add_node("chatbot", chatbot)

tool_node = ToolNode(tools=[tool])
graph_builder.add_node("tools", tool_node)
graph_builder.add_conditional_edges(
    "chatbot",
    tools_condition,
)
graph_builder.add_edge("tools", "chatbot")

graph_builder.add_edge(START, "chatbot")
graph = graph_builder.compile()
logger.info("Chatbot graph created successfully")
