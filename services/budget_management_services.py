
from sqlalchemy.orm import Session
from sqlalchemy import func
import pandas as pd
from database.models import WeddingProfile, BudgetCategory, Expense


# ==========================================
# 1. OVERALL BUDGET MANAGEMENT
# ==========================================

def set_overall_budget(db: Session, wedding_id: int, amount: float):
    if amount <= 0:
        raise ValueError("Budget must be greater than zero.")

    wedding = db.query(WeddingProfile).filter(
        WeddingProfile.id == wedding_id
    ).first()

    if not wedding:
        raise ValueError("Wedding profile not found.")

    wedding.total_budget = amount
    db.commit()
    db.refresh(wedding)

    return wedding


def get_overall_budget(db: Session, wedding_id: int):
    wedding = db.query(WeddingProfile).filter(
        WeddingProfile.id == wedding_id
    ).first()

    if not wedding:
        raise ValueError("Wedding profile not found.")

    return float(wedding.total_budget or 0)


def get_total_spending(db: Session, wedding_id: int):
    total = db.query(func.sum(Expense.amount)).filter(
        Expense.wedding_id == wedding_id
    ).scalar()

    return float(total or 0)


def get_remaining_balance(db: Session, wedding_id: int):
    return (
        get_overall_budget(db, wedding_id)
        - get_total_spending(db, wedding_id)
    )


def get_budget_summary(db: Session, wedding_id: int):
    budget = get_overall_budget(db, wedding_id)
    spending = get_total_spending(db, wedding_id)

    return {
        "overall_budget": budget,
        "total_spending": spending,
        "remaining_balance": budget - spending,
        "percentage_spent": round(
            (spending / budget) * 100, 2
        ) if budget > 0 else 0
    }


# ==========================================
# 2. CATEGORY MANAGEMENT
# ==========================================

def add_category(
    db: Session,
    wedding_id: int,
    category_name: str,
    allocated_amount: float
):
    if allocated_amount < 0:
        raise ValueError("Allocated amount cannot be negative.")

    category = BudgetCategory(
        wedding_id=wedding_id,
        category_name=category_name,
        allocated_amount=allocated_amount
    )

    db.add(category)
    db.commit()
    db.refresh(category)

    return category


def get_all_categories(db: Session, wedding_id: int):
    return db.query(BudgetCategory).filter(
        BudgetCategory.wedding_id == wedding_id
    ).all()


def get_category_by_id(
    db: Session,
    wedding_id: int,
    category_id: int
):
    return db.query(BudgetCategory).filter(
        BudgetCategory.id == category_id,
        BudgetCategory.wedding_id == wedding_id
    ).first()


def update_category(
    db: Session,
    wedding_id: int,
    category_id: int,
    category_name: str,
    allocated_amount: float
):
    if allocated_amount < 0:
        raise ValueError("Allocated amount cannot be negative.")

    category = get_category_by_id(
        db, wedding_id, category_id
    )

    if not category:
        raise ValueError("Category not found.")

    category.category_name = category_name
    category.allocated_amount = allocated_amount

    db.commit()
    db.refresh(category)

    return category


def delete_category(
    db: Session,
    wedding_id: int,
    category_id: int
):
    category = get_category_by_id(
        db, wedding_id, category_id
    )

    if not category:
        raise ValueError("Category not found.")

    linked_expense = db.query(Expense).filter(
        Expense.category_id == category_id,
        Expense.wedding_id == wedding_id
    ).first()

    if linked_expense:
        raise ValueError(
            "Cannot delete this category because expenses are linked to it."
        )

    db.delete(category)
    db.commit()

    return True


# ==========================================
# 3. EXPENSE MANAGEMENT
# ==========================================

def add_expense(
    db: Session,
    wedding_id: int,
    category_id: int,
    expense_name: str,
    amount: float,
    expense_date=None
):
    if amount < 0:
        raise ValueError("Expense amount cannot be negative.")

    category = get_category_by_id(
        db, wedding_id, category_id
    )

    if not category:
        raise ValueError("Category not found.")

    expense = Expense(
        wedding_id=wedding_id,
        category_id=category_id,
        description=expense_name,
        amount=amount,
        expense_date=expense_date
    )

    db.add(expense)
    db.commit()
    db.refresh(expense)

    return expense


def get_all_expenses(db: Session, wedding_id: int):
    return db.query(Expense).filter(
        Expense.wedding_id == wedding_id
    ).all()


def get_expense_by_id(
    db: Session,
    wedding_id: int,
    expense_id: int
):
    return db.query(Expense).filter(
        Expense.id == expense_id,
        Expense.wedding_id == wedding_id
    ).first()


def update_expense(
    db: Session,
    wedding_id: int,
    expense_id: int,
    expense_name: str,
    category_id: int,
    amount: float,
    expense_date=None
):
    if amount < 0:
        raise ValueError("Expense amount cannot be negative.")

    expense = get_expense_by_id(
        db, wedding_id, expense_id
    )

    if not expense:
        raise ValueError("Expense not found.")

    category = get_category_by_id(
        db, wedding_id, category_id
    )

    if not category:
        raise ValueError("Category not found.")

    expense.description = expense_name
    expense.category_id = category_id
    expense.amount = amount
    expense.expense_date = expense_date

    db.commit()
    db.refresh(expense)

    return expense


def delete_expense(
    db: Session,
    wedding_id: int,
    expense_id: int
):
    expense = get_expense_by_id(
        db, wedding_id, expense_id
    )

    if not expense:
        raise ValueError("Expense not found.")

    db.delete(expense)
    db.commit()

    return True


# ==========================================
# 4. BUDGET ANALYTICS
# ==========================================

def get_category_wise_summary(db: Session, wedding_id: int):
    categories = get_all_categories(db, wedding_id)

    summary = []

    for category in categories:
        actual_amount = db.query(
            func.sum(Expense.amount)
        ).filter(
            Expense.category_id == category.id,
            Expense.wedding_id == wedding_id
        ).scalar()

        actual_amount = float(actual_amount or 0)
        allocated_amount = float(category.allocated_amount or 0)

        summary.append({
            "category_id": category.id,
            "category_name": category.category_name,
            "allocated_amount": allocated_amount,
            "actual_amount": actual_amount,
            "remaining_amount": allocated_amount - actual_amount,
            "is_overspending": actual_amount > allocated_amount
        })

    return summary


def get_overspending_categories(db: Session, wedding_id: int):
    summary = get_category_wise_summary(db, wedding_id)

    return [
        category for category in summary
        if category["is_overspending"]
    ]
