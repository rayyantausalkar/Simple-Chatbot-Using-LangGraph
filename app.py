import streamlit as st
from chatbot import chatbot
from langchain_core.messages import HumanMessage

CONFIG = {'configurable': {'thread_id': '2'}}

if 'messages' not in st.session_state:
    st.session_state.messages = []

for chat in st.session_state.messages:
    with st.chat_message(chat['role']):
        st.markdown(chat['content'])


if user_input := st.chat_input('Type here'):

    with st.chat_message('user'):
        st.markdown(user_input)
    st.session_state.messages.append({'role': 'user', 'content': user_input})

    def generate_response():
        stream = chatbot.stream(
            {'messages': [HumanMessage(content=user_input)]},
            config=CONFIG,
            stream_mode='messages'
        )

        for message_chunk, metadata in stream:
            if message_chunk.content:
                yield message_chunk.content

    with st.chat_message('assistant'):
        assistant_message = st.write_stream(generate_response())

    st.session_state.messages.append({'role': 'assistant', 'content': assistant_message})
