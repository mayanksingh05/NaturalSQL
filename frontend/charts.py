import plotly.express as px
import streamlit as st
import pandas as pd
import numpy as np

def render_auto_chart(df: pd.DataFrame):
    """Automatically determines the best chart type based on dataframe structure (Phase 3)."""
    if df.empty:
        st.info("The query executed successfully, but returned no data.")
        return
    
    st.markdown("#### 📊 Data Visualization")
    
    # Attempt to convert any string columns that look like dates into actual datetime objects
    for col in df.columns:
        if df[col].dtype == 'object':
            try:
                # errors='ignore' prevents crashing if it's just regular text
                converted = pd.to_datetime(df[col], format='mixed', errors='ignore')
                if pd.api.types.is_datetime64_any_dtype(converted):
                    df[col] = converted
            except Exception:
                pass

    # Categorize columns by data type
    numeric_cols = df.select_dtypes(include=[np.number]).columns.tolist()
    date_cols = df.select_dtypes(include=['datetime', 'datetimetz']).columns.tolist()
    categorical_cols = df.select_dtypes(include=['object', 'category', 'string']).columns.tolist()

    # Logic 1: Text-heavy data (No numbers to plot) -> Table only
    if not numeric_cols:
        st.dataframe(df, use_container_width=True)
        return

    # Logic 2: Date + Numeric -> Line chart
    if date_cols and numeric_cols:
        # Sort by date so the line chart flows correctly left to right
        plot_df = df.sort_values(by=date_cols[0])
        fig = px.line(
            plot_df, 
            x=date_cols[0], 
            y=numeric_cols[0], 
            template="plotly_dark",
            markers=True,
            color_discrete_sequence=['#58a6ff']
        )
        fig.update_layout(plot_bgcolor='rgba(0,0,0,0)', paper_bgcolor='rgba(0,0,0,0)')
        st.plotly_chart(fig, use_container_width=True)

    # Logic 3: Category + Numeric -> Bar chart
    elif categorical_cols and numeric_cols:
        # Limit to top 30 to avoid an unreadable, crowded bar chart
        plot_df = df.head(30)
        fig = px.bar(
            plot_df, 
            x=categorical_cols[0], 
            y=numeric_cols[0], 
            template="plotly_dark", 
            color_discrete_sequence=['#58a6ff']
        )
        fig.update_layout(plot_bgcolor='rgba(0,0,0,0)', paper_bgcolor='rgba(0,0,0,0)')
        st.plotly_chart(fig, use_container_width=True)
        
        if len(df) > 30:
            st.caption("Chart limited to top 30 results for readability. View all data below.")

    # Fallback: Just display the table if it's a weird shape (like a single number)
    else:
        st.dataframe(df, use_container_width=True)