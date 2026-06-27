import streamlit as st
from chatbot import chatbot, retrieve_all_threads
from langchain_core.messages import HumanMessage, ToolMessage, AIMessage
import uuid

def generate_thread_id():
    return uuid.uuid4()

def reset_chat():
    thread_id = generate_thread_id()
    st.session_state.thread_id = thread_id
    add_thread(thread_id)
    st.session_state.messages = []

def add_thread(thread_id):
    if thread_id not in st.session_state.chat_threads:
        st.session_state.chat_threads.append(thread_id)

def load_conversations(thread_id):
    return chatbot.get_state(config={
        'configurable': {
            'thread_id': thread_id
        }
    }).values.get('messages', [])

if 'messages' not in st.session_state:
    st.session_state.messages = []

if 'thread_id' not in st.session_state:
    st.session_state.thread_id = generate_thread_id()

if 'chat_threads' not in st.session_state:
    st.session_state.chat_threads = retrieve_all_threads()

add_thread(st.session_state.thread_id)

st.sidebar.title('LangGraph Chatbot')
st.sidebar.header('Conversations')

if st.sidebar.button('New Chat'):
    reset_chat()

for thread_id in st.session_state.chat_threads:
    if st.sidebar.button(str(thread_id)):
        st.session_state.thread_id = thread_id
        messages = load_conversations(thread_id)

        temp = []
        for message in messages:
            if isinstance(message, HumanMessage): role = 'user'
            else: role = 'assistant'
            temp.append({'role': role, 'content': message.content if hasattr(message, 'content') else str(message)})

        st.session_state.messages = temp

for chat in st.session_state.messages:
    with st.chat_message(chat['role']):
        st.markdown(chat['content'])

if user_input := st.chat_input('Type here'):

    with st.chat_message('user'):
        st.markdown(user_input)
    st.session_state.messages.append({'role': 'user', 'content': user_input})

    CONFIG = {'configurable': {
        'thread_id': st.session_state.thread_id
    }}

    with st.chat_message('assistant'):
        with st.status("Thinking...", expanded=True) as status:
            stream = chatbot.stream(
                {'messages': [HumanMessage(content=user_input)]},
                config=CONFIG,
                stream_mode="updates"
            )
            
            assistant_message = ""
            
            for chunk in stream:
                if "tools" in chunk:
                    tool_messages = chunk["tools"].get("messages", [])
                    for msg in tool_messages:
                        # Log the tool name and input to the status container
                        status.write(f"🛠️ **Tool Used:** {msg.name}")
                
                if "agent" in chunk:
                    agent_messages = chunk["agent"].get("messages", [])
                    if agent_messages:
                        assistant_message = agent_messages[-1].content
            
            status.update(label="Response generated!", state="complete", expanded=False)
        
        st.markdown(assistant_message)

    st.session_state.messages.append({'role': 'assistant', 'content': assistant_message})

