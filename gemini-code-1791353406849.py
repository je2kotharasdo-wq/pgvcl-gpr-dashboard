import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

# Set Page Config
st.set_page_config(
    page_title="PGVCL Bhuj Circle - GPR Dashboard",
    page_icon="⚡",
    layout="wide"
)

st.title("⚡ PGVCL - Bhuj Circle GPR Analytics Dashboard")
st.markdown("Upload your daily updated GPR Report below to analyze new applications across divisions, sub-divisions, and categories.")

# --- File Uploader ---
uploaded_file = st.file_uploader("Upload GPR Report (.xls, .xlsx)", type=["xls", "xlsx"])

@st.cache_data
def load_data(file):
    try:
        # Read excel file (handles both xls via xlrd and xlsx via openpyxl)
        df = pd.read_excel(file)
        # Clean column names (strip spaces, uppercase)
        df.columns = df.columns.astype(str).str.strip()
        return df
    except Exception as e:
        st.error(f"Error loading file: {e}")
        return None

if uploaded_file is not None:
    df = load_data(uploaded_file)
    
    if df is not None:
        st.sidebar.header("🔍 Filter Controls")
        
        # Identify columns dynamically or via common naming conventions
        cols = df.columns.tolist()
        
        # Helper function to find matching columns
        def find_col(keywords):
            for col in cols:
                if any(kw.lower() in col.lower() for kw in keywords):
                    return col
            return cols[0] if cols else None

        div_col = find_col(['division', 'div'])
        sub_div_col = find_col(['sub_div', 'subdivision', 'sub division', 's/d'])
        cat_col = find_col(['category', 'cat', 'tariff'])
        status_col = find_col(['status', 'type', 'stage', 'pending'])

        # --- Sidebar Filters ---
        selected_divisions = []
        if div_col:
            divisions = sorted(df[div_col].dropna().unique().tolist())
            selected_divisions = st.sidebar.multiselect("Select Division(s)", divisions, default=divisions)

        selected_sub_divs = []
        if sub_div_col:
            # Filter sub-divisions based on selected divisions if division column exists
            temp_df = df[df[div_col].isin(selected_divisions)] if div_col and selected_divisions else df
            sub_divs = sorted(temp_df[sub_div_col].dropna().unique().tolist())
            selected_sub_divs = st.sidebar.multiselect("Select Sub-Division(s)", sub_divs, default=sub_divs)

        selected_categories = []
        if cat_col:
            categories = sorted(df[cat_col].dropna().unique().tolist())
            selected_categories = st.sidebar.multiselect("Select Category / Tariff", categories, default=categories)

        selected_statuses = []
        if status_col:
            statuses = sorted(df[status_col].dropna().unique().tolist())
            selected_statuses = st.sidebar.multiselect("Select Application Type / Status", statuses, default=statuses)

        # --- Apply Filters ---
        filtered_df = df.copy()
        if div_col and selected_divisions:
            filtered_df = filtered_df[filtered_df[div_col].isin(selected_divisions)]
        if sub_div_col and selected_sub_divs:
            filtered_df = filtered_df[filtered_df[sub_div_col].isin(selected_sub_divs)]
        if cat_col and selected_categories:
            filtered_df = filtered_df[filtered_df[cat_col].isin(selected_categories)]
        if status_col and selected_statuses:
            filtered_df = filtered_df[filtered_df[status_col].isin(selected_statuses)]

        # --- KPI Overview Metrics ---
        st.markdown("---")
        st.subheader("📊 Overview Summary")
        
        col1, col2, col3, col4 = st.columns(4)
        with col1:
            st.metric(label="Total Applications", value=f"{len(filtered_df):,}")
        with col2:
            if sub_div_col:
                st.metric(label="Sub-Divisions Covered", value=filtered_df[sub_div_col].nunique())
            else:
                st.metric(label="Sub-Divisions Covered", value="N/A")
        with col3:
            if cat_col:
                st.metric(label="Categories", value=filtered_df[cat_col].nunique())
            else:
                st.metric(label="Categories", value="N/A")
        with col4:
            if div_col:
                st.metric(label="Divisions", value=filtered_df[div_col].nunique())
            else:
                st.metric(label="Divisions", value="N/A")

        # --- Visualizations ---
        st.markdown("---")
        c1, c2 = st.columns(2)

        with c1:
            if sub_div_col:
                st.subheader("Applications by Sub-Division")
                sub_div_counts = filtered_df[sub_div_col].value_counts().reset_index()
                sub_div_counts.columns = ['Sub-Division', 'Count']
                fig_sub = px.bar(sub_div_counts, x='Sub-Division', y='Count', color='Count', 
                                 color_continuousscale='Blues', template='plotly_white')
                fig_sub.update_layout(xaxis_tickangle=-45)
                st.plotly_chart(fig_sub, use_container_width=True)
            else:
                st.info("Sub-division column not detected automatically.")

        with c2:
            if cat_col:
                st.subheader("Applications by Category")
                cat_counts = filtered_df[cat_col].value_counts().reset_index()
                cat_counts.columns = ['Category', 'Count']
                fig_cat = px.pie(cat_counts, names='Category', values='Count', hole=0.4, template='plotly_white')
                st.plotly_chart(fig_cat, use_container_width=True)
            else:
                st.info("Category column not detected automatically.")

        if status_col and div_col:
            st.markdown("---")
            st.subheader("Status / Application Type Breakdown per Division")
            status_div = filtered_df.groupby([div_col, status_col]).size().reset_index(name='Count')
            fig_stack = px.bar(status_div, x=div_col, y='Count', color=status_col, barmode='group', template='plotly_white')
            st.plotly_chart(fig_stack, use_container_width=True)

        # --- Detailed Data View & Download ---
        st.markdown("---")
        st.subheader("📋 Detailed Application Records")
        st.dataframe(filtered_df, use_container_width=True)

        # Download CSV button
        csv = filtered_df.to_csv(index=False).encode('utf-8')
        st.download_button(
            label="📥 Download Filtered Data as CSV",
            data=csv,
            file_name="filtered_gpr_report.csv",
            mime="text/csv",
        )
else:
    st.info("👆 Please upload a daily GPR report Excel file (`.xls` or `.xlsx`) to launch the dashboard.")