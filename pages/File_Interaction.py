import streamlit as st

from app.chatbot import document_analysis, image_analysis, image_generation
import asyncio
from google import genai
from pathlib import Path
import os
import time

api_key = os.getenv('GEMINI_API_KEY')

def stream_data(string):
    for word in string.split(" "):
        yield word + " "
        time.sleep(0.02)

st.set_page_config(page_title="Roti🍞 - File Interaction")

"""
Welcome!
In this section, you can interact with Roti🍞 along with file support.
You can upload documents (PDF, TXT, MD) and images (JPG, JPEG, PNG).
You can also generate images.
"""

with st.sidebar:
    st.markdown("Connect With Me!")
    "[Go to My Website](https://adli-portfolio.web.id)"
    "[My Github](https://github.com/adle15)"
    "[LinkedIn](https://linkedin.com/in/adlifarhan)"

mode = st.selectbox(label="Choose What you want to do!", options=[
    "Chat with Document", 
    "Chat with Image", 
    "Generate Image"])

if mode == "Chat with Document":
    
    CURRENT_SESSION = "chat_with_document"

    if 'last_page' not in st.session_state:
        st.session_state.last_page = CURRENT_SESSION

    if st.session_state.last_page != CURRENT_SESSION:
        st.session_state.pop('messages', None)
        st.session_state.last_page = CURRENT_SESSION
        
    saved_file = []

    st.title("📝 Chat with Document")
    uploaded_file = st.file_uploader("Upload files (multiple files allowed)", type=("pdf","txt","md"),accept_multiple_files=True)
    question = st.chat_input(
        placeholder="Can you give me a short summary?",
        disabled=not uploaded_file,
    )

    if "messages" not in st.session_state:
        st.session_state.messages = []

    # Display chat messages from history on app rerun
    for message in st.session_state.messages:
        avatar = "🧑‍💻" if message["role"] == "user" else "🍞"
        with st.chat_message(message["role"], avatar=avatar):
            st.markdown(message["content"])

    if uploaded_file and question:

        st.session_state.messages.append({"role": "user", "content": question})
        # Display user message in chat message container
        with st.chat_message("user", avatar="🧑‍💻"):
            st.markdown(question)

        with st.chat_message("assistant", avatar="🍞"):
            answer = asyncio.run(document_analysis(
                api_key=api_key,
                files=uploaded_file,
                prompt=question,
                history=st.session_state.messages
            ))
            response = st.write_stream(stream_data(answer))

        st.session_state.messages.append({"role": "assistant", "content": answer})


elif mode == "Chat with Image":

    CURRENT_SESSION = "chat_with_image"

    if 'last_page' not in st.session_state:
        st.session_state.last_page = CURRENT_SESSION

    if st.session_state.last_page != CURRENT_SESSION:
        st.session_state.pop('messages', None)
        st.session_state.last_page = CURRENT_SESSION

    saved_file = []

    st.title("🖼️ Chat with Images")
    uploaded_file = st.file_uploader("Upload image", type=("jpg","jpeg","png"),accept_multiple_files=False)
    question = st.chat_input(
        placeholder="What is this image about?",
        disabled=not uploaded_file,
    )

    if "messages" not in st.session_state:
        st.session_state.messages = []

    # Display chat messages from history on app rerun
    for message in st.session_state.messages:
        avatar = "🧑‍💻" if message["role"] == "user" else "🍞"
        with st.chat_message(message["role"], avatar=avatar):
            st.markdown(message["content"])

    if uploaded_file and question:

        st.markdown("**🖼️ Image Preview**")
        st.image(uploaded_file, caption=uploaded_file.name, use_container_width=True)
        st.session_state.messages.append({"role": "user", "content": question})
        # Display user message in chat message container
        with st.chat_message("user", avatar="🧑‍💻"):
            st.markdown(question)

        with st.chat_message("assistant", avatar="🍞"):
            answer = asyncio.run(image_analysis(
                api_key=api_key,
                files=uploaded_file,
                prompt=question,
                history=st.session_state.messages
            ))
            response = st.write_stream(stream_data(answer))

        st.session_state.messages.append({"role": "assistant", "content": answer})

elif mode == "Generate Image":

    saved_file = []

    st.title("🖼️ Generate Images")
    uploaded_file = st.file_uploader("Upload image (optional)", type=("jpg","jpeg","png"),accept_multiple_files=False)
    question = st.text_input(
        "Enter the prompt for generate image:"
    )

    if question and uploaded_file:
        st.markdown("**🖼️ Image Preview**")
        st.image(uploaded_file, caption=uploaded_file.name, use_container_width=True)
        answer, image = asyncio.run(image_generation(
            api_key=api_key,
            files=uploaded_file,
            prompt=question
        ))
        if image is not None:
            st.write_stream(stream_data(answer))
            st.image(image)
        else:
            st.write_stream(stream_data(answer))
            st.info("No image was generated.")

    elif question:
        answer, image = asyncio.run(image_generation(
            api_key=api_key,
            files=uploaded_file,
            prompt=question
        ))
        if image:
            st.write_stream(stream_data(answer))
            st.image(image)
        else:
            st.write_stream(stream_data(answer))
            st.info("No image was generated.")