from setup import State
import sqlite3
from datetime import datetime, timedelta
from typing import List, Dict, Any, Optional


from datetime import datetime, timedelta
from typing import List, Dict, Any, Optional

def database_setup():
    conn = sqlite3.connect('Spendings.db')
    c = conn.cursor()
    c.execute(
        '''
            CREATE TABLE IF NOT EXISTS expenses (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            category TEXT NOT NULL,
            amount REAL NOT NULL CHECK (amount >= 0),
            description TEXT,
            expense_date TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
            created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
        )'''
              )
    conn.commit()
    conn.close()





def database_setup():
    """Initialize the database with expenses table"""
    conn = sqlite3.connect('Spendings.db')
    c = conn.cursor()
    c.execute(
        '''
        CREATE TABLE IF NOT EXISTS expenses
        (
            id
            INTEGER
            PRIMARY
            KEY
            AUTOINCREMENT,
            category
            TEXT
            NOT
            NULL,
            amount
            REAL
            NOT
            NULL
            CHECK
        (
            amount
            >=
            0
        ),
            description TEXT,
            expense_date TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
            created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
            )'''
    )
    conn.commit()
    conn.close()


def save_to_db(expense_data: Dict[str, Any], message: str = '') -> bool:
    """
    Save expense to database
    Returns True if successful, False otherwise
    """
    try:
        conn = sqlite3.connect('Spendings.db')
        c = conn.cursor()

        # Use description from expense_data if message is empty
        description = message if message else expense_data.get('description', '')

        c.execute('''
                  INSERT INTO expenses (category, amount, description, expense_date)
                  VALUES (?, ?, ?, ?)
                  ''', (
                      expense_data['category'],
                      expense_data['amount'],
                      description,
                      expense_data.get('date', datetime.now().isoformat())
                  ))

        conn.commit()
        conn.close()
        return True

    except Exception as e:
        print(f"Database error: {e}")
        return False


def load_from_db(limit: Optional[int] = None, category: Optional[str] = None) -> List[Dict[str, Any]]:
    """
    Load expenses from database

    Args:
        limit: Maximum number of records to return
        category: Filter by specific category
    """
    try:
        conn = sqlite3.connect('Spendings.db')
        conn.row_factory = sqlite3.Row  # This allows dict-like access
        c = conn.cursor()

        query = "SELECT * FROM expenses"
        params = []

        if category:
            query += " WHERE category = ?"
            params.append(category)

        query += " ORDER BY expense_date DESC"

        if limit:
            query += " LIMIT ?"
            params.append(limit)

        c.execute(query, params)
        rows = c.fetchall()

        # Convert to list of dictionaries
        expenses = []
        for row in rows:
            expenses.append({
                'id': row['id'],
                'category': row['category'],
                'amount': row['amount'],
                'description': row['description'],
                'expense_date': row['expense_date'],
                'created_at': row['created_at']
            })

        conn.close()
        return expenses

    except Exception as e:
        print(f"Database error: {e}")
        return []


def get_total_spending(days: Optional[int] = None, category: Optional[str] = None) -> float:
    """
    Get total spending amount

    Args:
        days: Number of days to look back (None for all time)
        category: Filter by specific category
    """
    try:
        conn = sqlite3.connect('Spendings.db')
        c = conn.cursor()

        query = "SELECT SUM(amount) FROM expenses"
        params = []
        conditions = []

        if days:
            date_threshold = (datetime.now() - timedelta(days=days)).isoformat()
            conditions.append("expense_date >= ?")
            params.append(date_threshold)

        if category:
            conditions.append("category = ?")
            params.append(category)

        if conditions:
            query += " WHERE " + " AND ".join(conditions)

        c.execute(query, params)
        result = c.fetchone()[0]

        conn.close()
        return result if result is not None else 0.0

    except Exception as e:
        print(f"Database error: {e}")
        return 0.0


def get_spending_by_category(days: Optional[int] = None) -> Dict[str, float]:
    """
    Get spending breakdown by category

    Args:
        days: Number of days to look back (None for all time)
    """
    try:
        conn = sqlite3.connect('Spendings.db')
        c = conn.cursor()

        query = "SELECT category, SUM(amount) FROM expenses"
        params = []

        if days:
            date_threshold = (datetime.now() - timedelta(days=days)).isoformat()
            query += " WHERE expense_date >= ?"
            params.append(date_threshold)

        query += " GROUP BY category ORDER BY SUM(amount) DESC"

        c.execute(query, params)
        results = c.fetchall()

        conn.close()

        return {category: amount for category, amount in results}

    except Exception as e:
        print(f"Database error: {e}")
        return {}


def delete_expense(expense_id: int) -> bool:
    """Delete an expense by ID"""
    try:
        conn = sqlite3.connect('Spendings.db')
        c = conn.cursor()

        c.execute("DELETE FROM expenses WHERE id = ?", (expense_id,))

        success = c.rowcount > 0
        conn.commit()
        conn.close()

        return success

    except Exception as e:
        print(f"Database error: {e}")
        return False


def update_expense(expense_id: int, **kwargs) -> bool:
    """
    Update an expense

    Args:
        expense_id: ID of expense to update
        **kwargs: Fields to update (category, amount, description)
    """
    if not kwargs:
        return False

    try:
        conn = sqlite3.connect('Spendings.db')
        c = conn.cursor()

        # Build update query
        fields = []
        values = []

        for field in ['category', 'amount', 'description']:
            if field in kwargs:
                fields.append(f"{field} = ?")
                values.append(kwargs[field])

        if not fields:
            return False

        values.append(expense_id)
        query = f"UPDATE expenses SET {', '.join(fields)} WHERE id = ?"

        c.execute(query, values)

        success = c.rowcount > 0
        conn.commit()
        conn.close()

        return success

    except Exception as e:
        print(f"Database error: {e}")
        return False


def get_monthly_summary(year: int = None, month: int = None) -> Dict[str, Any]:
    """
    Get monthly spending summary

    Args:
        year: Year to filter (default: current year)
        month: Month to filter (default: current month)
    """
    if year is None:
        year = datetime.now().year
    if month is None:
        month = datetime.now().month

    try:
        conn = sqlite3.connect('Spendings.db')
        c = conn.cursor()

        # Get date range for the month
        start_date = f"{year}-{month:02d}-01"
        if month == 12:
            end_date = f"{year + 1}-01-01"
        else:
            end_date = f"{year}-{month + 1:02d}-01"

        # Total for the month
        c.execute("""
                  SELECT SUM(amount)
                  FROM expenses
                  WHERE expense_date >= ?
                    AND expense_date < ?
                  """, (start_date, end_date))

        total = c.fetchone()[0] or 0.0

        # By category
        c.execute("""
                  SELECT category, SUM(amount)
                  FROM expenses
                  WHERE expense_date >= ?
                    AND expense_date < ?
                  GROUP BY category
                  ORDER BY SUM(amount) DESC
                  """, (start_date, end_date))

        by_category = dict(c.fetchall())

        # Transaction count
        c.execute("""
                  SELECT COUNT(*)
                  FROM expenses
                  WHERE expense_date >= ?
                    AND expense_date < ?
                  """, (start_date, end_date))

        count = c.fetchone()[0]

        conn.close()

        return {
            'year': year,
            'month': month,
            'total': total,
            'by_category': by_category,
            'transaction_count': count
        }

    except Exception as e:
        print(f"Database error: {e}")
        return {
            'year': year,
            'month': month,
            'total': 0.0,
            'by_category': {},
            'transaction_count': 0
        }


def handle_query(state: State):
    """Handle expense queries and generate reports"""
    last_message = state["messages"][-1]
    query = last_message.get("content", "").lower()

    if "total" in query:
        if "month" in query:
            total = get_total_spending(days=30)
            response = f"💰 Total spending (last 30 days): ${total:.2f} JD"
        else:
            total = get_total_spending()
            response = f"💰 Total spending (all time): ${total:.2f} JD"

    elif "category" in query or "breakdown" in query:
        days = 30 if "month" in query else None
        by_category = get_spending_by_category(days)

        if by_category:
            response = f"📊 Spending by category{'(last 30 days)' if days else ''}:\n"
            for cat, amount in by_category.items():
                response += f"• {cat.title()}: ${amount:.2f} JD\n"
        else:
            response = "No expenses found for the specified period."

    elif "recent" in query or "last" in query:
        limit = 10 if "10" in query else 5
        recent = load_from_db(limit=limit)

        if recent:
            response = f"📝 Recent {len(recent)} expenses:\n"
            for exp in recent:
                date = datetime.fromisoformat(exp['expense_date']).strftime('%m/%d')
                response += f"• {date}: {exp['description']} - ${exp['amount']:.2f} ({exp['category']})\n"
        else:
            response = "No recent expenses found."

    elif "monthly" in query and "summary" in query:
        summary = get_monthly_summary()
        response = f"📊 This Month's Summary:\n"
        response += f"💰 Total: ${summary['total']:.2f} JD\n"
        response += f"📝 Transactions: {summary['transaction_count']}\n"
        if summary['by_category']:
            response += f"🏆 Top category: {max(summary['by_category'].items(), key=lambda x: x[1])[0]}\n"

    else:
        response = """❓ I can help you with:
• "show total spending" - All time total
• "monthly total" - Last 30 days
• "category breakdown" - Spending by category  
• "recent expenses" - Latest transactions
• "monthly summary" - This month's overview
• "send monthly report" - Email monthly report"""

    return {"messages": [{"role": "assistant", "content": response}]}

# def save_to_json(expense_data):
#     """Save to JSON file - FREE storage option"""
#     filename = "expenses.json"
#
#     try:
#         with open(filename, 'r') as f:
#             expenses = json.load(f)
#     except FileNotFoundError:
#         expenses = []
#
#     expenses.append(expense_data)
#
#     with open(filename, 'w') as f:
#         json.dump(expenses, f, indent=2)