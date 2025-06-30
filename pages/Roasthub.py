import streamlit as st
import asyncio
import os
from app.chatbot import roast_github_profile

#gemini api key
api_key=os.getenv('GEMINI_API_KEY')

st.set_page_config(page_title="Roti🍞 - RoastHub🔥")
st.title("RoastHub🔥")

"""
Brace yourself.
\nRoti🍞 is about to roast your GitHub profile into a smoldering pile of commit ashes.
\nNo repo is safe. Let the burn begin.🔥🔥🔥
"""

with st.sidebar:
    st.markdown("Connect With Me!")
    "[Go to My Website](https://adli-portfolio.web.id)"
    "[My Github](https://github.com/adle15)"
    "[LinkedIn](https://linkedin.com/in/adlifarhan)"

language = st.selectbox(label="Select Languages", options=[
    "English", 
    "Bahasa"])

username = st.text_input(
    "Input your github username"
)

if not username:
    st.info("Please input your github username")

if username:
    answer = asyncio.run(roast_github_profile(api_key, username, language))
    st.markdown(answer)