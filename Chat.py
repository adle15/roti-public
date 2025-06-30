import streamlit as st

from app.chatbot import generate_content
import asyncio
import os
import time

api_key = os.getenv('GEMINI_API_KEY')

st.set_page_config(page_title="Roti🍞")

st.title("💬 Chat With Roti🍞")

"""
Welcome! In this platform you can chat with Roti🍞 — A personal assistant powered by Gemini.
Roti has in-depth knowledge of Adli Farhan Ibrahim’s professional experiences and can also help with general topics.
Feel free to ask Roti🍞 anything!
"""

with st.sidebar:
    st.markdown("Connect With Me!")
    "[Go to My Website](https://adli-portfolio.web.id)"
    "[My Github](https://github.com/adle15)"
    "[LinkedIn](https://linkedin.com/in/adlifarhan)"

def stream_data(string):
    for word in string.split(" "):
        yield word + " "
        time.sleep(0.02)


# --- Set current page id manually ---
CURRENT_PAGE = "Chat"

# --- Clear chat_message if page changed ---
if 'last_page' not in st.session_state:
    st.session_state.last_page = CURRENT_PAGE

if st.session_state.last_page != CURRENT_PAGE:
    st.session_state.pop('messages', None)
    st.session_state.last_page = CURRENT_PAGE

# Initialize chat history
if "messages" not in st.session_state:
    st.session_state.messages = []

# Display chat messages from history on app rerun
for message in st.session_state.messages:
    avatar = "🧑‍💻" if message["role"] == "user" else "🍞"
    with st.chat_message(message["role"], avatar=avatar):
        st.markdown(message["content"])

# Accept user input
if prompt := st.chat_input():
    # Add user message to chat history
    st.session_state.messages.append({"role": "user", "content": prompt})
    # Display user message in chat message container
    with st.chat_message("user", avatar="🧑‍💻"):
        st.markdown(prompt)

    # Display assistant response in chat message container
    with st.chat_message("assistant", avatar="🍞"):
        answer = asyncio.run(generate_content(api_key,prompt,st.session_state.messages))
        response = st.write_stream(stream_data(answer))
    # Add assistant response to chat history
    st.session_state.messages.append({"role": "assistant", "content": answer})