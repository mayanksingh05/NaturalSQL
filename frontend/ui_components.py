import streamlit as st


def apply_custom_css():
    st.markdown("""
        <style>
        @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600&display=swap');

        html, body, [class*="css"] {
            font-family: 'Inter', sans-serif;
        }

        /* Main Layout */
        .main .block-container {
            max-width: 1000px;
            padding-top: 2rem;
            padding-bottom: 2rem;
        }

        /* Chat Messages */
        .stChatMessage {
            border-radius: 14px;
            margin-bottom: 12px;
        }

        /* Smooth Animation */
        @keyframes fadeIn {
            from {
                opacity: 0;
                transform: translateY(8px);
            }
            to {
                opacity: 1;
                transform: translateY(0);
            }
        }

        .stChatMessage {
            animation: fadeIn 0.25s ease-in-out;
        }

        /* Buttons */
        .stButton > button {
            border-radius: 10px;
            font-weight: 600;
            transition: 0.2s ease;
        }

        .stButton > button:hover {
            transform: translateY(-1px);
        }

        /* Code Block */
        pre {
            border-radius: 12px !important;
        }

        /* Remove forced sidebar theme */
        [data-testid="stSidebar"] {
            border-right: 1px solid rgba(128,128,128,0.2);
        }
        </style>
    """, unsafe_allow_html=True)


def render_header():
    st.markdown("## ✨ NaturalSQL")
    st.caption("Ask questions. Get SQL. Run insights.")
    st.divider()


def chat_bubble(role, text):
    with st.chat_message(role):
        st.markdown(text)


def sql_preview_area(query):
    st.markdown("### Generated SQL")
    st.code(query, language="sql")

    return st.button(
        "▶ Run Query",
        use_container_width=False
    )