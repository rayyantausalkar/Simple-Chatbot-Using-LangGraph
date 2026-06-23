from langgraph.graph import StateGraph, START, END
from langgraph.graph.message import BaseMessage, add_messages
from langgraph.checkpoint.memory import InMemorySaver
from langchain_google_genai import ChatGoogleGenerativeAI
from typing import TypedDict, Annotated

from dotenv import load_dotenv
load_dotenv()

# model
model = ChatGoogleGenerativeAI(
    model='gemini-3.1-flash-lite',
    temperature='0.5'
)

# state
class ChatbotState(TypedDict):
    messages: Annotated[list[BaseMessage], add_messages]

# graph
graph = StateGraph(ChatbotState)
checkpointer = InMemorySaver()

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
chatbot = graph.compile(checkpointer=checkpointer)
