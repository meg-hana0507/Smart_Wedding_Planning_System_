
import streamlit as st
import pandas as pd
from database.database import SessionLocal

from services.budget_management_services import (
    get_budget_summary,
    set_overall_budget,
    add_category,
    get_all_categories,
    update_category,
    delete_category,
    add_expense,
    get_all_expenses,
    update_expense,
    delete_expense,
    get_category_wise_summary,
    get_overspending_categories
)


def show_budget_management(wedding_id: int):

    st.title("💰 Budget & Expense Management")
    st.caption(
        "Plan your wedding budget, manage expenses "
        "and monitor your spending."
    )

    db = SessionLocal()

    try:

        # ------------------------------------------------
        # 1. BUDGET DASHBOARD
        # ------------------------------------------------

        tab1, tab2, tab3, tab4 = st.tabs([
            "📊 Dashboard",
            "📁 Categories",
            "💵 Expenses",
            "📈 Analytics"
        ])

        # ================================================
        # TAB 1 - BUDGET DASHBOARD
        # ================================================

        with tab1:

            st.subheader("Wedding Budget Overview")

            summary = get_budget_summary(db, wedding_id)

            col1, col2, col3 = st.columns(3)

            col1.metric(
                "Total Budget",
                f"₹{summary['overall_budget']:,.2f}"
            )

            col2.metric(
                "Total Spending",
                f"₹{summary['total_spending']:,.2f}"
            )

            col3.metric(
                "Remaining Balance",
                f"₹{summary['remaining_balance']:,.2f}"
            )

            st.write("### Budget Utilization")

            st.progress(
                min(summary["percentage_spent"] / 100, 1.0)
            )

            st.write(
                f"{summary['percentage_spent']}% of your budget used"
            )

            st.divider()

            st.subheader("Set Overall Wedding Budget")

            with st.form("overall_budget_form"):

                new_budget = st.number_input(
                    "Enter Total Budget (₹)",
                    min_value=1.0,
                    value=max(
                        summary["overall_budget"], 1.0
                    ),
                    step=10000.0
                )

                submitted = st.form_submit_button(
                    "Update Budget"
                )

                if submitted:

                    set_overall_budget(
                        db,
                        wedding_id,
                        new_budget
                    )

                    st.success("Wedding budget updated!")
                    st.rerun()

        # ================================================
        # TAB 2 - BUDGET CATEGORIES
        # ================================================

        with tab2:

            st.subheader("Manage Budget Categories")

            with st.expander("➕ Add New Category", expanded=True):

                with st.form("add_category_form"):

                    category_name = st.text_input(
                        "Category Name"
                    )

                    allocated_amount = st.number_input(
                        "Allocated Amount (₹)",
                        min_value=0.0,
                        step=1000.0
                    )

                    submitted = st.form_submit_button(
                        "Add Category"
                    )

                    if submitted:

                        try:

                            add_category(
                                db,
                                wedding_id,
                                category_name,
                                allocated_amount
                            )

                            st.success(
                                "Category added successfully!"
                            )

                            st.rerun()

                        except Exception as error:
                            st.error(str(error))

            st.divider()

            categories = get_all_categories(
                db,
                wedding_id
            )

            st.subheader("Existing Categories")

            if not categories:

                st.info("No categories created yet.")

            else:

                for category in categories:

                    with st.expander(
                        f"{category.category_name} - "
                        f"₹{category.allocated_amount:,.2f}"
                    ):

                        with st.form(
                            f"edit_category_{category.id}"
                        ):

                            new_name = st.text_input(
                                "Category Name",
                                value=category.category_name
                            )

                            new_amount = st.number_input(
                                "Allocated Amount (₹)",
                                min_value=0.0,
                                value=float(
                                    category.allocated_amount or 0
                                ),
                                step=1000.0
                            )

                            submitted = st.form_submit_button(
                                "Update Category"
                            )

                            if submitted:

                                try:

                                    update_category(
                                        db,
                                        wedding_id,
                                        category.id,
                                        new_name,
                                        new_amount
                                    )

                                    st.success(
                                        "Category updated!"
                                    )

                                    st.rerun()

                                except Exception as error:
                                    st.error(str(error))

                        if st.button(
                            "Delete Category",
                            key=f"delete_category_{category.id}"
                        ):

                            try:

                                delete_category(
                                    db,
                                    wedding_id,
                                    category.id
                                )

                                st.success(
                                    "Category deleted!"
                                )

                                st.rerun()

                            except Exception as error:
                                st.error(str(error))

        # ================================================
        # TAB 3 - EXPENSE MANAGEMENT
        # ================================================

        with tab3:

            st.subheader("Manage Wedding Expenses")

            categories = get_all_categories(
                db,
                wedding_id
            )

            if not categories:

                st.warning(
                    "Please create a budget category first."
                )

            else:

                category_options = {
                    category.category_name: category.id
                    for category in categories
                }

                with st.expander(
                    "➕ Add New Expense",
                    expanded=True
                ):

                    with st.form("add_expense_form"):

                        expense_name = st.text_input(
                            "Expense Name"
                        )

                        selected_category = st.selectbox(
                            "Select Category",
                            list(category_options.keys())
                        )

                        amount = st.number_input(
                            "Expense Amount (₹)",
                            min_value=0.0,
                            step=500.0
                        )

                        expense_date = st.date_input(
                            "Expense Date"
                        )

                        submitted = st.form_submit_button(
                            "Add Expense"
                        )

                        if submitted:

                            try:

                                add_expense(
                                    db,
                                    wedding_id,
                                    category_options[
                                        selected_category
                                    ],
                                    expense_name,
                                    amount,
                                    expense_date
                                )

                                st.success(
                                    "Expense added successfully!"
                                )

                                st.rerun()

                            except Exception as error:
                                st.error(str(error))

            st.divider()

            st.subheader("Existing Expenses")

            expenses = get_all_expenses(
                db,
                wedding_id
            )

            if not expenses:

                st.info("No expenses recorded yet.")

            else:

                for expense in expenses:

                    category_name = expense.category.category_name

                    with st.expander(
                        f"{expense.description} - "
                        f"₹{expense.amount:,.2f}"
                    ):

                        with st.form(
                            f"edit_expense_{expense.id}"
                        ):

                            new_name = st.text_input(
                                "Expense Name",
                                value=expense.description
                            )

                            category_names = list(
                                category_options.keys()
                            )

                            current_index = (
                                category_names.index(category_name)
                                if category_name in category_names
                                else 0
                            )

                            new_category = st.selectbox(
                                "Category",
                                category_names,
                                index=current_index
                            )

                            new_amount = st.number_input(
                                "Expense Amount (₹)",
                                min_value=0.0,
                                value=float(expense.amount),
                                step=500.0
                            )

                            new_date = st.date_input(
                                "Expense Date",
                                value=expense.expense_date
                            )

                            submitted = st.form_submit_button(
                                "Update Expense"
                            )

                            if submitted:

                                try:

                                    update_expense(
                                        db,
                                        wedding_id,
                                        expense.id,
                                        new_name,
                                        category_options[new_category],
                                        new_amount,
                                        new_date
                                    )

                                    st.success(
                                        "Expense updated!"
                                    )

                                    st.rerun()

                                except Exception as error:
                                    st.error(str(error))

                        if st.button(
                            "Delete Expense",
                            key=f"delete_expense_{expense.id}"
                        ):

                            try:

                                delete_expense(
                                    db,
                                    wedding_id,
                                    expense.id
                                )

                                st.success(
                                    "Expense deleted!"
                                )

                                st.rerun()

                            except Exception as error:
                                st.error(str(error))

        # ================================================
        # TAB 4 - BUDGET ANALYTICS
        # ================================================

        with tab4:

            st.subheader("Budget Analytics")

            summary_data = get_category_wise_summary(
                db,
                wedding_id
            )

            alerts = get_overspending_categories(
                db,
                wedding_id
            )

            if not summary_data:

                st.info(
                    "Create categories and add expenses "
                    "to view analytics."
                )

            else:

                df = pd.DataFrame(summary_data)

                st.write("### Category-wise Spending")

                display_df = df[
                    [
                        "category_name",
                        "allocated_amount",
                        "actual_amount",
                        "remaining_amount"
                    ]
                ].copy()

                display_df.columns = [
                    "Category",
                    "Allocated Amount (₹)",
                    "Actual Spending (₹)",
                    "Remaining Amount (₹)"
                ]

                st.dataframe(
                    display_df,
                    use_container_width=True,
                    hide_index=True
                )

                st.divider()

                st.write("### Allocated vs Actual Spending")

                chart_data = df.set_index(
                    "category_name"
                )[
                    [
                        "allocated_amount",
                        "actual_amount"
                    ]
                ]

                st.bar_chart(chart_data)

                st.divider()

                st.write("### Overspending Alerts")

                if alerts:

                    for item in alerts:

                        difference = (
                            item["actual_amount"]
                            - item["allocated_amount"]
                        )

                        st.error(
                            f"{item['category_name']} is "
                            f"overspent by ₹{difference:,.2f}"
                        )

                else:

                    st.success(
                        "No overspending detected!"
                    )

    except Exception as error:

        st.error(f"Budget Management Error: {error}")

    finally:

        db.close()


