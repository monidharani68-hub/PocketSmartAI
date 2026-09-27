# Ensure config is called to load env vars and setup LLM
import os
import warnings

from annotated_types import test_cases
from langchain.chat_models import init_chat_model

from SendEmail import send_gmail
from Storing import database_setup, handle_query, load_from_db, get_total_spending
from main import  State
from nodes import classify_message, save_expense, send_monthly_report, router
# CHANGE: Suppress Pydantic warnings for cleaner output

warnings.filterwarnings("ignore", category=UserWarning, module="pydantic")

# CHANGE: Debug environment variables loading
print("--- Debug: Environment Variables ---")
print(f"GMAIL_USER loaded: {'✅' if os.getenv('GMAIL_USER') else '❌'}")
print(f"GMAIL_APP_PASSWORD loaded: {'✅' if os.getenv('GMAIL_APP_PASSWORD') else '❌'}")
print(f"RECIPIENT_EMAIL loaded: {'✅' if os.getenv('RECIPIENT_EMAIL') else '❌'}")
print(f"API_KEY loaded: {'✅' if os.getenv('API_KEY') else '❌'}")

# CHANGE: Check if database file exists
import sqlite3
db_file_exists = os.path.exists('Spendings.db')
print(f"Database file exists: {'✅' if db_file_exists else '❌'}")

if db_file_exists:
    # Quick check of database structure
    conn = sqlite3.connect('Spendings.db')
    c = conn.cursor()
    c.execute("SELECT COUNT(*) FROM expenses")
    count = c.fetchone()[0]
    print(f"Current expenses in database: {count}")
    conn.close()


print("--- Setting up Database ---")
database_setup()
print("Database initialized!")

# --- Test 1: Classify Message ---
# --- Test 1: Classify Message ---
print("--- Testing Message Classification ---")

# CHANGE: Added multiple test cases for different categories
# CHANGE: Added multiple test cases for different categories
test_cases = [
    {
        "name": "Food/Groceries",
        "message": "I spent 25 JD on groceries yesterday.",
        "expected_category": "food"
    },
    {
        "name": "Transportation",
        "message": "Paid 50 JD for gas at the station.",
        "expected_category": "transportation"
    },
    {
        "name": "Housing/Utilities",
        "message": "My electricity bill was 80 JD this month.",
        "expected_category": "housing"
    },
    {
        "name": "Entertainment",
        "message": "Bought movie tickets for 15 JD.",
        "expected_category": "entertainment"
    },
    {
        "name": "Shopping/Clothes",
        "message": "I bought a new shirt for 35 JD.",
        "expected_category": "shopping"
    },
    {
        "name": "Healthcare",
        "message": "Doctor visit cost me 40 JD.",
        "expected_category": "healthcare"
    },
    {
        "name": "Personal Care",
        "message": "Got a haircut for 20 JD.",
        "expected_category": "personal_care"
    },
    {
        "name": "Subscriptions",
        "message": "Netflix subscription is 12 JD monthly.",
        "expected_category": "subscriptions"
    },
    {
        "name": "Food/Restaurant",
        "message": "Had dinner at restaurant, cost 45 JD.",
        "expected_category": "food"
    },
    {
        "name": "Debt Payment",
        "message": "Made credit card payment of 200 JD.",
        "expected_category": "debt"
    },
    {
        "name": "Gifts",
        "message": "Bought birthday gift for friend, 60 JD.",
        "expected_category": "gifts"
    },
    {
        "name": "Savings",
        "message": "Deposited 500 JD into savings account.",
        "expected_category": "savings"
    }
]

# Test each category
classified_results = []
for i, test_case in enumerate(test_cases, 1):
    print(f"\n{i}. Testing {test_case['name']}:")
    print(f"   Input: \"{test_case['message']}\"")

    test_state: State = {
        "messages": [{"role": "user", "content": test_case['message']}],
        "category": None,
        "amount": None,
        "description": None
    }

    classified_data = classify_message(test_state)
    print(
        f"   Result: Category='{classified_data['category']}', Amount={classified_data['amount']}, Description='{classified_data['description']}'")

    # Check if classification matches expected
    status = "✅" if classified_data['category'] == test_case['expected_category'] else "❌"
    print(f"   Status: {status} (Expected: {test_case['expected_category']})")

    classified_results.append({
        'test_case': test_case,
        'result': classified_data,
        'correct': classified_data['category'] == test_case['expected_category']
    })

# Summary
print(f"\n--- Classification Summary ---")
correct_count = sum(1 for r in classified_results if r['correct'])
total_count = len(classified_results)
print(f"Correct classifications: {correct_count}/{total_count} ({correct_count / total_count * 100:.1f}%)")

# CHANGE: Save all classified test states for further testing
print(f"\n--- Saving All Classified Expenses ---")
saved_count = 0
for i, result in enumerate(classified_results, 1):
    test_state: State = {
        "messages": [{"role": "user", "content": result['test_case']['message']}],
        "category": result['result']['category'],
        "amount": result['result']['amount'],
        "description": result['result']['description']
    }

    try:
        save_response = save_expense(test_state)
        print(f"{i:2d}. {save_response['messages'][0]['content']}")
        saved_count += 1
    except Exception as e:
        print(f"{i:2d}. ❌ Failed to save: {result['test_case']['name']} - {e}")

print(f"\n✅ Successfully saved {saved_count}/{total_count} test expenses to database")

# Use the first test case for remaining tests (keep original structure)
test_state_1 = {
    "messages": [{"role": "user", "content": test_cases[0]['message']}],
    "category": classified_results[0]['result']['category'],
    "amount": classified_results[0]['result']['amount'],
    "description": classified_results[0]['result']['description']
}
# --- Test 2: Save Expense (using classified data) ---
print("\n--- Testing Saving Expense ---")
# Assuming save_to_db is implemented and accessible
save_response = save_expense(test_state_1)
print("Save Response:", save_response["messages"][0]["content"])

# CHANGE: Test handle_query function
print("\n--- Testing Handle Query ---")
query_state: State = {
    "messages": [{"role": "user", "content": "Show me my total spending"}],
    "category": None,
    "amount": None,
    "description": None
}
query_response = handle_query(query_state)
print("Query Response:", query_response["messages"][0]["content"])

# --- Test 3: Send Monthly Report ---
print("\n--- Testing Monthly Report Generation/Send ---")
all_expenses = load_from_db()
print(f"Total expenses in database: {len(all_expenses)}")
if all_expenses:
    print("Recent expenses:")
    for exp in all_expenses[:3]:  # Show first 3
        print(f"  - {exp['description']}: ${exp['amount']:.2f} ({exp['category']})")
else:
    print("No expenses found in database")

total = get_total_spending()
print(f"Total spending: ${total:.2f} JD")

# CHANGE: Add more test expenses to verify functionality
print("\n--- Adding More Test Expenses ---")
test_expenses = [
    {"messages": [{"role": "user", "content": "I bought coffee for 5 JD"}], "category": None, "amount": None, "description": None},
    {"messages": [{"role": "user", "content": "Paid 50 JD for gas"}], "category": None, "amount": None, "description": None}
]

for i, expense_state in enumerate(test_expenses, 1):
    print(f"Adding test expense {i}...")
    classified = classify_message(expense_state)
    expense_state.update(classified)
    save_response = save_expense(expense_state)
    print(f"  {save_response['messages'][0]['content']}")
# You might want to add some test data to your JSON/DB first for a meaningful report
# Example: Add a couple more test expenses manually to expenses.json or via the save function
report_state: State = {
     "messages": [{"role": "user", "content": "Please send the monthly report."}],
     "category": None,
     "amount": None,
     "description": None
}
# Assuming get_monthly_summary is implemented
report_response = send_monthly_report(report_state)
print("Report Response:", report_response["messages"][0]["content"])

# --- Test 4: Router Logic ---
print("\n--- Testing Router Logic ---")
# Test with different message types
test_messages = [
    {"content": "I bought a new shirt for $30", "expected": "classify_message"},
    {"content": "Show me my total spending this week", "expected": "handle_query"}, # Note: handle_query isn't shown
    {"content": "Send me the monthly summary email", "expected": "send_monthly_report"},
    {"content": "Hello!", "expected": "END"}, # Should end
]

dummy_state: State = {
    "messages": [],
    "category": None,
    "amount": None,
    "description": None
}

for msg in test_messages:
    dummy_state["messages"] = [{"role": "user", "content": msg["content"]}]
    # Reset classification data for clean test
    dummy_state["category"] = None
    dummy_state["amount"] = None
    dummy_state["description"] = None
    route = router(dummy_state)
    print(f"Message: '{msg['content']}' -> Routed to: {route} (Expected: {msg['expected']})")

