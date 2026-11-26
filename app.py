
import streamlit as st
import pandas as pd

from sqlalchemy import inspect

from database.initialize_db import engine
from database.database import SessionLocal
from database.models import WeddingProfile

from modules.expenses.budget_management import show_budget_management


# ---------------------------------------------------------
# 1. PAGE CONFIGURATION
# ---------------------------------------------------------

st.set_page_config(
    page_title="Smart Wedding Planning System",
    page_icon="💍",
    layout="wide"
)


# ---------------------------------------------------------
# 2. SIDEBAR NAVIGATION
# ---------------------------------------------------------

st.sidebar.title("💍 Wedding Planner")
st.sidebar.caption("Smart Wedding Planning System")

selected_module = st.sidebar.radio(
    "Select Module",
    [
        "Database Explorer",
        "Budget Management"
    ]
)


# ---------------------------------------------------------
# 3. WEDDING SELECTION FOR MODULE 3
# ---------------------------------------------------------

wedding_id = None

if selected_module == "Budget Management":

    db = SessionLocal()

    try:
        weddings = db.query(WeddingProfile).order_by(
            WeddingProfile.id
        ).all()

        if not weddings:
            st.warning("No wedding profiles found.")
            st.stop()

        wedding_options = {
            f"{w.id} - {w.bride_name} & {w.groom_name}": w.id
            for w in weddings
        }

        selected_wedding = st.sidebar.selectbox(
            "Select Wedding",
            list(wedding_options.keys())
        )

        wedding_id = wedding_options[selected_wedding]

    finally:
        db.close()


# ---------------------------------------------------------
# 4. DATABASE EXPLORER
# ---------------------------------------------------------

if selected_module == "Database Explorer":

    st.title("💍 Smart Wedding Planning System")

    st.caption(
        "A centralized platform to plan, organize, "
        "and manage wedding activities with clarity and control."
    )

    st.markdown("---")

    # TOP SUMMARY METRICS

    col1, col2, col3, col4, col5 = st.columns(5)

    with engine.connect() as conn:

        total_users = pd.read_sql_query(
            "SELECT COUNT(*) AS count FROM users", conn
        ).iloc[0]["count"]

        total_venues = pd.read_sql_query(
            "SELECT COUNT(*) AS count FROM venues", conn
        ).iloc[0]["count"]

        total_vendors = pd.read_sql_query(
            "SELECT COUNT(*) AS count FROM vendors", conn
        ).iloc[0]["count"]

        total_guests = pd.read_sql_query(
            "SELECT COUNT(*) AS count FROM guests", conn
        ).iloc[0]["count"]

        total_tasks = pd.read_sql_query(
            "SELECT COUNT(*) AS count FROM tasks", conn
        ).iloc[0]["count"]

    col1.metric("👥 Users", f"{total_users}")
    col2.metric("🏰 Venues", f"{total_venues}")
    col3.metric("🤝 Vendors", f"{total_vendors}")
    col4.metric("💌 Guests", f"{total_guests}")
    col5.metric("✅ Tasks", f"{total_tasks}")

    st.markdown("---")

    # TABLE SELECTION

    st.sidebar.header("📁 Database Explorer")

    inspector = inspect(engine)
    table_list = inspector.get_table_names()

    if not table_list:
        st.warning("No database tables found.")
        st.stop()

    default_index = (
        table_list.index("guests")
        if "guests" in table_list
        else 0
    )

    selected_table = st.sidebar.selectbox(
        "Select Table to View:",
        table_list,
        index=default_index
    )

    st.sidebar.info(f"Viewing: **{selected_table}**")

    # MAIN TABLE DISPLAY

    st.subheader(f"📋 Table: `{selected_table}`")

    with engine.connect() as conn:

        df = pd.read_sql_query(
            f'SELECT * FROM "{selected_table}"',
            conn
        )

    search_query = st.text_input(
        f"🔍 Search within `{selected_table}`:",
        ""
    )

    if search_query:

        mask = df.astype(str).apply(
            lambda row: row.str.contains(
                search_query,
                case=False,
                na=False
            ).any(),
            axis=1
        )

        filtered_df = df[mask]

        st.write(
            f"Showing **{len(filtered_df)}** matching rows "
            f"(out of {len(df)} total)."
        )

        st.dataframe(
            filtered_df,
            use_container_width=True
        )

    else:

        st.write(f"Total Records: **{len(df)} rows**")

        st.dataframe(
            df,
            use_container_width=True
        )

    # DOWNLOAD DATA

    csv = df.to_csv(index=False).encode("utf-8")

    st.download_button(
        label=f"📥 Download `{selected_table}` as CSV",
        data=csv,
        file_name=f"{selected_table}.csv",
        mime="text/csv"
    )

    # SCHEMA DETAILS

    with st.expander(
        f"ℹ️ View Column Schema for `{selected_table}`"
    ):

        with engine.connect() as conn:

            schema_df = pd.read_sql_query(
                f'PRAGMA table_info("{selected_table}")',
                conn
            )

        st.dataframe(
            schema_df[
                ["cid", "name", "type", "notnull", "pk"]
            ].rename(
                columns={
                    "cid": "Index",
                    "name": "Column Name",
                    "type": "Data Type",
                    "notnull": "Required (Not Null)",
                    "pk": "Primary Key"
                }
            ),
            use_container_width=True
        )

    # QUICK VISUAL CHARTS

    st.markdown("---")

    st.subheader("📊 Quick Live Insights from Database")

    chart_col1, chart_col2 = st.columns(2)

    with chart_col1:

        st.write("##### 💌 Guest RSVP Breakdown")

        with engine.connect() as conn:

            rsvp_df = pd.read_sql_query(
                """
                SELECT rsvp_status, COUNT(*) AS count
                FROM invitations
                GROUP BY rsvp_status
                """,
                conn
            )

        if not rsvp_df.empty:

            st.bar_chart(
                rsvp_df.set_index("rsvp_status")
            )

        else:

            st.info("No RSVP data available.")

    with chart_col2:

        st.write("##### 💰 Budget Allocation by Category")

        with engine.connect() as conn:

            budget_df = pd.read_sql_query(
                """
                SELECT category_name, allocated_amount
                FROM budget_categories
                LIMIT 6
                """,
                conn
            )

        if not budget_df.empty:

            st.bar_chart(
                budget_df.set_index("category_name")
            )

        else:

            st.info("No budget category data available.")


# ---------------------------------------------------------
# 5. MODULE 3 - BUDGET MANAGEMENT
# ---------------------------------------------------------

elif selected_module == "Budget Management":

    show_budget_management(wedding_id)
