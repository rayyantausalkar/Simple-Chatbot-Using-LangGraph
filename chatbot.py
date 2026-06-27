from langgraph.graph import StateGraph, START, END
from langgraph.prebuilt import create_react_agent
from langgraph.graph.message import BaseMessage, add_messages
from langgraph.checkpoint.sqlite import SqliteSaver
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_openai import ChatOpenAI
from langchain_core.tools import tool

from langchain_community.tools import DuckDuckGoSearchRun
from langchain_community.utilities.alpha_vantage import AlphaVantageAPIWrapper

from typing import TypedDict, Annotated
import sqlite3

from dotenv import load_dotenv
load_dotenv()

# tools

@tool
def calculator(expression: str) -> str:
    """Useful for evaluating mathematical expressions. Input must be a valid python math string."""
    try:
        allowed_names = {"__builtins__": None, "abs": abs, "round": round}
        return str(eval(expression, allowed_names, {}))
    except Exception as e:
        return f"Error evaluating expression: {str(e)}"

web_search = DuckDuckGoSearchRun()

@tool
def stock_price(ticker: str) -> str:
    """Useful for fetching the current stock price or financial data for a given equity ticker symbol."""
    alpha_vantage = AlphaVantageAPIWrapper()
    try:
        result = alpha_vantage._execute_quote(ticker)
        return str(result)
    except Exception as e:
        return f"Error fetching stock data: {str(e)}"

tools = [calculator, web_search, stock_price]

# model
model = ChatOpenAI(
    base_url="http://localhost:1234/v1",
    api_key="lm-studio",
    model="google/gemma-4-e4b",
    temperature=0.5
)

# state
class ChatbotState(TypedDict):
    messages: Annotated[list[BaseMessage], add_messages]

# graph
graph = StateGraph(ChatbotState)

conn = sqlite3.connect(database='chatbot.db', check_same_thread=False)
checkpointer = SqliteSaver(conn=conn)

# functions
def chat_feature(state: ChatbotState) -> ChatbotState:
    messages = state['messages']
    response = model.invoke(messages)
    return {'messages': [response]}

# nodes
graph.add_node('chat_feature', chat_feature)

# edges
graph.add_edge(START, 'chat_feature')
graph.add_edge('chat_feature', END)

# compile the graph
# chatbot = graph.compile(checkpointer=checkpointer)

chatbot = create_react_agent(model, tools=tools, checkpointer=checkpointer)

def retrieve_all_threads():
    all_threads = set()
    for checkpoint in checkpointer.list(None):
        all_threads.add(checkpoint.config['configurable']['thread_id'])
    return list(all_threads)
