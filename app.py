import streamlit as st
import pandas as pd
from database.initialize_db import engine
# pyrefly: ignore[missing-import]
from sqlalchemy import inspect

# Page Configuration
st.set_page_config(
    page_title="Smart Wedding Planning - Database Explorer",
    page_icon="💍",
    layout="wide"
)

# App Title & Subtitle
st.title("💍 Smart Wedding Planning System")
st.caption("A centralized platform to plan, organize, and manage wedding activities with clarity and control.")
st.markdown("---")

# -----------------------------------------------------------------------------
# 1. TOP SUMMARY METRICS
# -----------------------------------------------------------------------------
col1, col2, col3, col4, col5 = st.columns(5)

with engine.connect() as conn:
    total_users = pd.read_sql_query("SELECT COUNT(*) AS count FROM users", conn).iloc[0]["count"]
    total_venues = pd.read_sql_query("SELECT COUNT(*) AS count FROM venues", conn).iloc[0]["count"]
    total_vendors = pd.read_sql_query("SELECT COUNT(*) AS count FROM vendors", conn).iloc[0]["count"]
    total_guests = pd.read_sql_query("SELECT COUNT(*) AS count FROM guests", conn).iloc[0]["count"]
    total_tasks = pd.read_sql_query("SELECT COUNT(*) AS count FROM tasks", conn).iloc[0]["count"]

col1.metric("👥 Users", f"{total_users}")
col2.metric("🏰 Venues", f"{total_venues}")
col3.metric("🤝 Vendors", f"{total_vendors}")
col4.metric("💌 Guests", f"{total_guests}")
col5.metric("✅ Tasks", f"{total_tasks}")

st.markdown("---")

# -----------------------------------------------------------------------------
# 2. SIDEBAR - TABLE SELECTION & FILTERS
# -----------------------------------------------------------------------------
st.sidebar.header("📁 Database Explorer")

# Get all 11 table names dynamically
inspector = inspect(engine)
table_list = inspector.get_table_names()

selected_table = st.sidebar.selectbox(
    "Select Table to View:",
    table_list,
    index=table_list.index("guests") if "guests" in table_list else 0
)

st.sidebar.info(f"Viewing: **{selected_table}**")

# -----------------------------------------------------------------------------
# 3. MAIN TABLE DISPLAY
# -----------------------------------------------------------------------------
st.subheader(f"📋 Table: `{selected_table}`")

with engine.connect() as conn:
    df = pd.read_sql_query(f"SELECT * FROM {selected_table}", conn)

# Search Bar for Table
search_query = st.text_input(f"🔍 Search within `{selected_table}` (matches any text):", "")

if search_query:
    # Filter rows that contain the search term in any text column
    mask = df.astype(str).apply(lambda row: row.str.contains(search_query, case=False).any(), axis=1)
    filtered_df = df[mask]
    st.write(f"Showing **{len(filtered_df)}** matching rows (out of {len(df)} total):")
    st.dataframe(filtered_df, use_container_width=True)
else:
    st.write(f"Total Records: **{len(df)} rows**")
    st.dataframe(df, use_container_width=True)

# -----------------------------------------------------------------------------
# 4. DOWNLOAD DATA BUTTON
# -----------------------------------------------------------------------------
csv = df.to_csv(index=False).encode('utf-8')
st.download_button(
    label=f"📥 Download `{selected_table}` as CSV",
    data=csv,
    file_name=f"{selected_table}.csv",
    mime="text/csv",
)

# -----------------------------------------------------------------------------
# 5. SCHEMA DETAILS EXPANDER
# -----------------------------------------------------------------------------
with st.expander(f"ℹ️ View Column Schema for `{selected_table}`"):
    with engine.connect() as conn:
        schema_df = pd.read_sql_query(f"PRAGMA table_info({selected_table})", conn)
        st.dataframe(
            schema_df[["cid", "name", "type", "notnull", "pk"]].rename(
                columns={"cid": "Index", "name": "Column Name", "type": "Data Type", "notnull": "Required (Not Null)", "pk": "Primary Key"}
            ),
            use_container_width=True
        )

# -----------------------------------------------------------------------------
# 6. QUICK VISUAL CHARTS (Module 3 & Module 4 Preview)
# -----------------------------------------------------------------------------
st.markdown("---")
st.subheader("📊 Quick Live Insights from Database")

chart_col1, chart_col2 = st.columns(2)

with chart_col1:
    st.write("##### 💌 Guest RSVP Breakdown")
    with engine.connect() as conn:
        rsvp_df = pd.read_sql_query(
            "SELECT rsvp_status, COUNT(*) AS count FROM invitations GROUP BY rsvp_status",
            conn
        )
    st.bar_chart(rsvp_df.set_index("rsvp_status"))

with chart_col2:
    st.write("##### 💰 Budget Allocation by Category")
    with engine.connect() as conn:
        budget_df = pd.read_sql_query(
            "SELECT category_name, allocated_amount FROM budget_categories LIMIT 6",
            conn
        )
    st.bar_chart(budget_df.set_index("category_name"))