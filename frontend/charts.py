import plotly.express as px
import streamlit as st
import pandas as pd

def render_auto_chart(df):
    """Automatically determines the best chart type based on dataframe structure."""
    if df.empty:
        return
    
    cols = df.columns
    st.markdown("#### 📊 Data Visualization")
    
    # If we have a categorical and a numerical column
    if len(cols) >= 2:
        numeric_cols = df.select_dtypes(include=['number']).columns.tolist()
        categorical_cols = df.select_dtypes(exclude=['number']).columns.tolist()
        
        if numeric_cols and categorical_cols:
            tab1, tab2 = st.tabs(["Bar Chart", "Line Chart"])
            
            with tab1:
                fig = px.bar(df, x=categorical_cols[0], y=numeric_cols[0], 
                             template="plotly_dark", color_discrete_sequence=['#58a6ff'])
                fig.update_layout(plot_bgcolor='rgba(0,0,0,0)', paper_bgcolor='rgba(0,0,0,0)')
                st.plotly_chart(fig, use_container_width=True)
            
            with tab2:
                fig = px.line(df, x=categorical_cols[0], y=numeric_cols[0], 
                              template="plotly_dark")
                st.plotly_chart(fig, use_container_width=True)
        else:
            st.dataframe(df, use_container_width=True)
    else:
        st.dataframe(df, use_container_width=True)