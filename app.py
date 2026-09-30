from flask import Flask, render_template, request, redirect, url_for, flash
import sqlite3
from datetime import date
from pathlib import Path

app = Flask(__name__)
app.secret_key = "change-this-secret-key"
DB = Path(__file__).with_name("pocketsmart.db")
CATEGORIES = ["Food", "Transport", "Shopping", "Bills", "Education", "Health", "Entertainment", "Other"]

def db():
    conn = sqlite3.connect(DB)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    with db() as con:
        con.execute("""CREATE TABLE IF NOT EXISTS transactions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            kind TEXT NOT NULL CHECK(kind IN ('income','expense')),
            amount REAL NOT NULL,
            category TEXT NOT NULL,
            note TEXT,
            spent_on TEXT NOT NULL
        )""")
        con.execute("""CREATE TABLE IF NOT EXISTS settings (
            key TEXT PRIMARY KEY, value REAL NOT NULL
        )""")
        con.execute("INSERT OR IGNORE INTO settings(key,value) VALUES('monthly_budget',10000)")

@app.route("/")
def index():
    with db() as con:
        rows = con.execute("SELECT * FROM transactions ORDER BY spent_on DESC, id DESC LIMIT 8").fetchall()
        income = con.execute("SELECT COALESCE(SUM(amount),0) FROM transactions WHERE kind='income'").fetchone()[0]
        expenses = con.execute("SELECT COALESCE(SUM(amount),0) FROM transactions WHERE kind='expense'").fetchone()[0]
        budget = con.execute("SELECT value FROM settings WHERE key='monthly_budget'").fetchone()[0]
        by_category = con.execute("""SELECT category, SUM(amount) total FROM transactions
            WHERE kind='expense' AND strftime('%Y-%m',spent_on)=strftime('%Y-%m','now')
            GROUP BY category ORDER BY total DESC""").fetchall()
    remaining = budget - sum(x["total"] for x in by_category)
    tips = recommendations(by_category, income, expenses, budget)
    return render_template("index.html", rows=rows, income=income, expenses=expenses,
                           balance=income-expenses, budget=budget, remaining=remaining,
                           categories=by_category, tips=tips, today=date.today().isoformat())

@app.route("/add", methods=["POST"])
def add():
    kind = request.form.get("kind", "expense")
    category = request.form.get("category", "Other")
    note = request.form.get("note", "").strip()
    try:
        amount = float(request.form.get("amount", "0"))
        if amount <= 0 or kind not in ("income", "expense") or category not in CATEGORIES:
            raise ValueError
    except ValueError:
        flash("Enter a valid positive amount and category.")
        return redirect(url_for("index"))
    spent_on = request.form.get("spent_on") or date.today().isoformat()
    with db() as con:
        con.execute("INSERT INTO transactions(kind,amount,category,note,spent_on) VALUES(?,?,?,?,?)",
                    (kind, amount, category, note, spent_on))
    flash("Transaction added.")
    return redirect(url_for("index"))

@app.route("/delete/<int:transaction_id>", methods=["POST"])
def delete(transaction_id):
    with db() as con:
        con.execute("DELETE FROM transactions WHERE id=?", (transaction_id,))
    flash("Transaction deleted.")
    return redirect(url_for("index"))

@app.route("/budget", methods=["POST"])
def budget():
    try:
        value = float(request.form.get("monthly_budget", "0"))
        if value < 0: raise ValueError
    except ValueError:
        flash("Please enter a valid budget.")
        return redirect(url_for("index"))
    with db() as con:
        con.execute("UPDATE settings SET value=? WHERE key='monthly_budget'", (value,))
    flash("Monthly budget updated.")
    return redirect(url_for("index"))

def recommendations(categories, income, expenses, budget):
    tips = []
    total_month = sum(row["total"] for row in categories)
    if budget > 0 and total_month > budget:
        tips.append(f"You are ₹{total_month-budget:,.0f} over your monthly budget. Review non-essential spending.")
    elif budget > 0:
        tips.append(f"You have ₹{max(0,budget-total_month):,.0f} left in your monthly budget.")
    if income and expenses / income >= .8:
        tips.append("Your recorded expenses are at least 80% of your income. Consider setting a savings target.")
    if categories:
        top = categories[0]
        tips.append(f"{top['category']} is your largest expense category this month (₹{top['total']:,.0f}).")
    if not tips:
        tips.append("Add income and expenses to receive personalized budget insights.")
    tips.append("Try recording purchases daily so your recommendations reflect current spending.")
    return tips

if __name__ == "__main__":
    init_db()
    app.run(debug=True)
