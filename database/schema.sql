
-- ==========================================
-- MODULE 3: BUDGET AND EXPENSE MANAGEMENT
-- ==========================================

CREATE TABLE IF NOT EXISTS budget_settings (
    setting_id INTEGER PRIMARY KEY AUTOINCREMENT,
    overall_budget NUMERIC(12, 2) NOT NULL DEFAULT 0,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS budget_categories (
    category_id INTEGER PRIMARY KEY AUTOINCREMENT,
    category_name VARCHAR(100) NOT NULL UNIQUE,
    allocated_amount NUMERIC(12, 2) NOT NULL DEFAULT 0,
    description VARCHAR(500),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS expenses (
    expense_id INTEGER PRIMARY KEY AUTOINCREMENT,
    category_id INTEGER NOT NULL,
    expense_name VARCHAR(150) NOT NULL,
    estimated_amount NUMERIC(12, 2) NOT NULL DEFAULT 0,
    actual_amount NUMERIC(12, 2),
    expense_date DATE NOT NULL,
    description VARCHAR(500),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,

    FOREIGN KEY (category_id)
        REFERENCES budget_categories(category_id)
);
