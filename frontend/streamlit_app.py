import streamlit as st
import pandas as pd
import uuid
from ui_components import apply_custom_css, render_header, chat_bubble, sql_preview_area
from api_client import NaturalSQLAPI
from charts import render_auto_chart

# Page Config
st.set_page_config(
    page_title="NaturalSQL | AI Data Analyst",
    page_icon="⚡",
    layout="wide"
)

apply_custom_css()

# --- ISOLATED SESSION STATE ---
if "session_id" not in st.session_state:
    st.session_state.session_id = str(uuid.uuid4())
if "messages" not in st.session_state:
    st.session_state.messages = []
if "schema_data" not in st.session_state:
    st.session_state.schema_data = []
if "last_sql" not in st.session_state:
    st.session_state.last_sql = ""
if "query_results" not in st.session_state:
    st.session_state.query_results = None
if "error_message" not in st.session_state:
    st.session_state.error_message = None
if "is_sql_valid" not in st.session_state:
    st.session_state.is_sql_valid = True
if "validation_message" not in st.session_state:
    st.session_state.validation_message = ""

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
        type=["csv", "xlsx", "xls", "db", "sqlite"]
    )

    if uploaded_file:
        if "uploaded_file_name" not in st.session_state or st.session_state.uploaded_file_name != uploaded_file.name:
            with st.spinner("Processing securely..."):
                try:
                    upload_res = NaturalSQLAPI.upload_file(uploaded_file, st.session_state.session_id)
                    st.session_state.schema_data = upload_res.get("schema", [])
                    st.session_state.uploaded_file_name = uploaded_file.name
                    st.session_state.uploaded_file = True
                    st.success(f"Loaded: {uploaded_file.name}")
                except Exception as e:
                    st.error(f"Failed to upload file: {str(e)}")
                    st.session_state.uploaded_file = False
        else:
            st.success(f"Loaded: {uploaded_file.name}")
            
        # Display schema overview so users know available tables and columns
        if st.session_state.schema_data:
            with st.expander("📋 View Tables & Columns", expanded=False):
                tables = {}
                for col in st.session_state.schema_data:
                    tables.setdefault(col.get("table", "data"), []).append(col["name"])
                for t_name, cols in tables.items():
                    st.markdown(f"**Table: `{t_name}`**")
                    st.caption(", ".join(cols))
    else:
        st.session_state.uploaded_file = False
        st.session_state.pop("uploaded_file_name", None)
        st.session_state.schema_data = []

    st.subheader("🔑 Gemini API Key")
    gemini_key = st.text_input(
        "Enter your Gemini API Key",
        type="password",
        placeholder="AIzaSy...",
        help="Get a free key at https://aistudio.google.com/app/apikey"
    )
    st.caption("🔒 Key stays in memory only and is never stored on the server. [Get free Gemini key →](https://aistudio.google.com/app/apikey)")

    st.divider()

    if st.button("Clear Chat", use_container_width=True):
        st.session_state.messages = []
        st.session_state.last_sql = ""
        st.session_state.query_results = None
        st.session_state.error_message = None
        st.rerun()

# --- MAIN UI ---
st.markdown("## ⚡ NaturalSQL")
st.caption("Your data. Plain English. Instant insights.")
st.divider()

# Display chat history
for message in st.session_state.messages:
    if message["role"] != "sql":
        chat_bubble(
            message["role"],
            message["content"]
        )

# --- CHAT INPUT ---
prompt = st.chat_input("Ask your data anything...")

# --- CUSTOM FOOTER INJECTION ---
st.markdown(
    """
    <style>
    .custom-footer {
        position: fixed;
        bottom: 5px;
        left: 0;
        width: 100%;
        text-align: center;
        color: #888888;
        font-size: 0.75rem;
        z-index: 999999;
        pointer-events: none;
    }
    [data-testid="stChatInput"] {
        padding-bottom: 25px;
    }
    </style>
    <div class='custom-footer'>Powered by NaturalSQL Engine • Bring Your Own Key • Session Secured</div>
    """, 
    unsafe_allow_html=True
)

if prompt and not st.session_state.uploaded_file:
    st.warning("Please upload a CSV, Excel or SQLite database in the sidebar first.")

elif prompt:
    if not gemini_key or not gemini_key.strip():
        st.error("⚠️ Please enter your Gemini API Key in the sidebar. [Get a free key from Google AI Studio →](https://aistudio.google.com/app/apikey)")
    else:
        st.session_state.messages.append({
            "role": "user",
            "content": prompt
        })
        chat_bubble("user", prompt)

        with st.spinner("Analyzing data with Gemini..."):
            try:
                response = NaturalSQLAPI.ask_question(
                    prompt, 
                    gemini_key.strip(), 
                    st.session_state.session_id, 
                    st.session_state.schema_data
                )
                
                generated_sql = response.get("sql", "")
                st.session_state.last_sql = generated_sql
                st.session_state.is_sql_valid = response.get("is_valid", False)
                st.session_state.validation_message = response.get("validation_message", "")
                
                st.session_state.query_results = None 
                st.session_state.error_message = None

                if not st.session_state.is_sql_valid and not generated_sql:
                     st.error(f"Error: {st.session_state.validation_message}")
                else:
                    st.session_state.messages.append({
                        "role": "sql",
                        "content": generated_sql
                    })
                    st.rerun()
                    
            except Exception as e:
                st.error(f"Error: {str(e)}")

# --- ACTION AREA ---
if st.session_state.last_sql:
    if not st.session_state.is_sql_valid:
        st.error(f"⚠️ **Issue Detected:** {st.session_state.validation_message}")
        if st.session_state.last_sql:
            st.code(st.session_state.last_sql, language="sql")
    else:
        if sql_preview_area(st.session_state.last_sql):
            with st.spinner("Executing query..."):
                try:
                    result = NaturalSQLAPI.execute_sql(st.session_state.last_sql, st.session_state.session_id)
                    df = pd.DataFrame(result["data"])
                    st.session_state.query_results = df
                    st.session_state.error_message = None
                except Exception as e:
                    st.session_state.error_message = str(e)

# --- RESULTS ---
if st.session_state.error_message:
    st.error(f"SQL Execution Error: {st.session_state.error_message}")

elif st.session_state.query_results is not None:
    render_auto_chart(st.session_state.query_results)

    col1, col2 = st.columns([1, 4])
    with col1:
        csv_data = st.session_state.query_results.to_csv(index=False).encode('utf-8')
        st.download_button(
            label="📥 Download CSV",
            data=csv_data,
            file_name="query_results.csv",
            mime="text/csv",
            use_container_width=True
        )

    with st.expander("View Raw Data", expanded=True):
        st.dataframe(
            st.session_state.query_results,
            use_container_width=True
        )