import streamlit as st
from chatbot import chatbot
from langchain_core.messages import HumanMessage

CONFIG = {'configurable': {'thread_id': '1'}}

if 'messages' not in st.session_state:
    st.session_state.messages = []

for chat in st.session_state.messages:
    with st.chat_message(chat['role']):
        st.markdown(chat['content'])


if user_input := st.chat_input('Type here'):

    with st.chat_message('user'):
        st.markdown(user_input)
    st.session_state.messages.append({'role': 'user', 'content': user_input})

    response = chatbot.invoke({'messages': [HumanMessage(content=user_input)]}, config=CONFIG)
    model_response = response['messages'][-1].content

    with st.chat_message('assistant'):
        st.markdown(model_response)
    st.session_state.messages.append({'role': 'assistant', 'content': model_response})

