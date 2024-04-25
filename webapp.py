import random
from step_one.find import find_posts
from step_one.openAI import generate_random_need
import streamlit as st


INITIAL_NEED = "Forming new habits is hard"


# Allow the user to quickly see responses for different needs
def randomize_activity():
    st.session_state["need"] = generate_random_need()


if "need" not in st.session_state:
    st.session_state["need"] = INITIAL_NEED

st.title("Step One")


@st.cache_data
def get_posts(need):
    return find_posts(need, st.write)


need = st.text_input(
    "User problem", key="need", label_visibility="visible", placeholder=INITIAL_NEED
)

randomize_need_button = st.button(
    "Randomize need", on_click=randomize_activity, type="secondary"
)

st.header("Results")

# Explain that we are generating the results if we haven't already
st.write("Finding matching posts...")
posts = get_posts(need)
st.write(f"Found {len(posts)} matching posts:")


for post in posts:
    with st.container():
        st.subheader(post["title"])
        st.write(f"https://reddit.com{post['permalink']}")
        st.write(post["summary"])
        st.write(post["full_answer"])
        st.write("\n\n\n\n")
