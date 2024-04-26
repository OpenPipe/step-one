import random
from step_one.find import find_posts
from step_one.openAI import generate_random_need
import streamlit as st
import os


INITIAL_NEED = "Forming new habits is hard "


# Allow the user to quickly see responses for different needs
def feeling_lucky():
    st.session_state["need"] = generate_random_need(wonky=True)


def serious_need():
    st.session_state["need"] = generate_random_need(wonky=False)


if "need" not in st.session_state:
    st.session_state["need"] = INITIAL_NEED

st.title("Step One")
st.write("Step One is a tool that helps you find your first users on reddit.")

st.write(
    "WARNING: Reddit is touchy about web scraping, and likes to throw 403s when too many people use this app at once."
)

with st.sidebar:
    st.write("To use the OpenAI API, provide your api key.")
    openai_api_key = st.text_input(
        "OpenAI API Key",
        key="openai_api_key",
        label_visibility="visible",
        placeholder="sk-...",
        type="password",
        value=os.environ.get("DEFAULT_OPENAI_API_KEY"),
    )
    st.write(
        "If you don't have an API key, you can still use the fine-tuned models (the results are better anyway)."
    )
    available_modes = (
        ("OpenAI", "Fine-tuned models") if openai_api_key else ("Fine-tuned models",)
    )
    mode = st.radio("Select mode", available_modes)

    st.write("Link to project and models: https://app.openpipe.ai/p/ft1b4KYFoq")
    st.write("Link to GitHub: https://github.com/openpipe/step-one")


@st.cache_data
def get_posts(need, use_fine_tuned=False):
    if need.strip() == "":
        return []
    return find_posts(need, st.write, use_fine_tuned, openai_api_key)


need = st.text_area(
    "Problem statement",
    key="need",
    label_visibility="visible",
    placeholder=INITIAL_NEED,
)

col1, col2, col3 = st.columns([1, 2, 3])
serious_need_button = col1.button("Real need", on_click=serious_need, type="primary")
feeling_lucky_button = col2.button(
    "I'm feeling lucky", on_click=feeling_lucky, type="secondary"
)

st.header("Results")

# Explain that we are generating the results if we haven't already
st.write("Finding matching posts...")
posts = get_posts(
    need,
    use_fine_tuned=mode == "Fine-tuned models",
)
st.write(f"Found {len(posts)} matching posts:")


for post in posts:
    with st.container():
        st.subheader(post["title"])
        st.write(f"https://reddit.com{post['permalink']}")
        st.write(post["summary"])
        st.write(post["full_answer"])
        st.write("\n\n\n\n")
