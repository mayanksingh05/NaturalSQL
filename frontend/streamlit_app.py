import streamlit as st
import pandas as pd
from ui_components import apply_custom_css, render_header, chat_bubble, sql_preview_area
from api_client import NaturalSQLAPI
from charts import render_auto_chart

# Page Config
st.set_page_config(
    page_title="NaturalSQL | AI Data Analyst",
    page_icon="🪄",
    layout="wide"
)

apply_custom_css()

# Session State
if "messages" not in st.session_state:
    st.session_state.messages = []

if "last_sql" not in st.session_state:
    st.session_state.last_sql = ""

if "query_results" not in st.session_state:
    st.session_state.query_results = None

if "error_message" not in st.session_state:
    st.session_state.error_message = None

# --- SIDEBAR ---
with st.sidebar:
    st.image(
        "https://cdn-icons-png.flaticon.com/512/4248/4248443.png",
        width=50
    )

    st.title("Settings")

    st.subheader("📁 Data Source")

    uploaded_file = st.file_uploader(
        "Upload CSV, Excel or SQLite DB",
        type=["csv", "xlsx", "db"]
    )

    if uploaded_file:
        st.session_state.uploaded_file = uploaded_file

        st.success(
            f"Loaded: {uploaded_file.name}"
        )
    else:
        st.session_state.uploaded_file = None

    st.subheader("🧠 Model")

    st.selectbox(
        "Provider",
        ["Ollama (Llama 3)", "Gemini 1.5 Pro"]
    )

    st.divider()

    if st.button("Clear Chat", use_container_width=True):
        st.session_state.messages = []
        st.session_state.last_sql = ""
        st.session_state.query_results = None
        st.session_state.error_message = None
        st.rerun()

# --- MAIN UI ---
render_header()

# Display chat history
for message in st.session_state.messages:

    if message["role"] != "sql":
        chat_bubble(
            message["role"],
            message["content"]
        )

# --- CHAT INPUT ---
prompt = st.chat_input(
    "Ask your data anything..."
)

if prompt and not st.session_state.uploaded_file:
    st.warning(
        "Please upload a CSV, Excel or SQLite database first."
    )

elif prompt:
    # User Message
    st.session_state.messages.append({
        "role": "user",
        "content": prompt
    })

    chat_bubble("user", prompt)

    # SQL Generation
    with st.spinner("Generating SQL query..."):

        # response = NaturalSQLAPI.ask_question(prompt, schema_info)

        response = NaturalSQLAPI.ask_question(prompt)
        generated_sql = response["sql"]
        st.session_state.last_sql = generated_sql

        st.session_state.messages.append({
            "role": "sql",
            "content": generated_sql
        })

        st.rerun()

# --- ACTION AREA ---
if st.session_state.last_sql:

    if sql_preview_area(st.session_state.last_sql):

        with st.spinner("Executing query..."):

            # result = NaturalSQLAPI.execute_sql(
            #     st.session_state.last_sql
            # )

            mock_df = pd.DataFrame({
                "product_name": [
                    "Laptop",
                    "Mouse",
                    "Monitor",
                    "Keyboard",
                    "Desk"
                ],
                "sales": [
                    12000,
                    1500,
                    4500,
                    2000,
                    7000
                ]
            })

            st.session_state.query_results = mock_df

# --- RESULTS ---
if st.session_state.query_results is not None:

    render_auto_chart(
        st.session_state.query_results
    )

    with st.expander("View Raw Data"):
        st.dataframe(
            st.session_state.query_results,
            use_container_width=True
        )

# Footer
st.markdown("<br><br>", unsafe_allow_html=True)

st.caption(
    "Powered by NaturalSQL Engine • v1.0.2"
)