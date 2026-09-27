#----------------Imports----------------
import json
from datetime import datetime
from typing import TypedDict, Annotated, Literal
import pandas as pd
from typing import Annotated
from pydantic import BaseModel
from pydantic.v1 import Field
from typing_extensions import TypedDict
from langgraph.graph import StateGraph, START, END
from langgraph.graph.message import add_messages
import os
from langchain.chat_models import init_chat_model


#--------------------------------------
# Import setup to initialize everything
from setup import State, MessageClassifier, llm
from nodes import classify_message, save_expense, send_monthly_report, router
from Storing import handle_query

# Initialize configuration


# Set up LLM
api_key = os.getenv("API_KEY")
if api_key is None:
    raise ValueError("❌ API_KEY not found in environment variables. Please check your .env file.")

os.environ["OPENAI_API_KEY"] = api_key
llm = init_chat_model("openai:gpt-4o-mini")




# os.environ["OPENAI_API_KEY"] = os.getenv("API_KEY")




# Import nodes after defining State and MessageClassifier


from Storing import handle_query


def handle_error(state: State):
    """Handle errors or invalid messages"""
    error_msg = state.get("error", "Invalid input or processing error")
    return {
        "messages": [{"role": "assistant", "content": f"❌ Error: {error_msg}"}]
    }


# Build the StateGraph
def create_expense_tracker_graph():
    """Create and return the expense tracker graph"""

    # Initialize the StateGraph
    workflow = StateGraph(State)

    # Add nodes
    workflow.add_node("classify_message", classify_message)
    workflow.add_node("save_expense", save_expense)
    workflow.add_node("handle_query", handle_query)
    workflow.add_node("send_monthly_report", send_monthly_report)
    workflow.add_node("handle_error", handle_error)
    workflow.add_node("router", router)

    # Add edges based on router logic
    workflow.add_edge(START, "router")

    # Router decides where to go next
    workflow.add_conditional_edges(
        "router",
        router,
        {
            "classify_message": "classify_message",
            "save_expense": "save_expense",
            "handle_query": "handle_query",
            "send_monthly_report": "send_monthly_report",
            "handle_error": "handle_error",
            "END": END
        }
    )

    # After classification, go back to router to decide next step
    workflow.add_edge("classify_message", "router")

    # After saving, handling query, sending report, or error - end
    workflow.add_edge("save_expense", END)
    workflow.add_edge("handle_query", END)
    workflow.add_edge("send_monthly_report", END)
    workflow.add_edge("handle_error", END)

    # Compile the graph
    app = workflow.compile()
    return app


# Create the graph
expense_tracker = create_expense_tracker_graph()


def run_expense_tracker(message: str):
    """Run the expense tracker with a message"""
    initial_state = {
        "messages": [{"role": "user", "content": message}],
        "category": None,
        "amount": None,
        "description": None,
        "error": None
    }

    try:
        result = expense_tracker.invoke(initial_state)
        return result
    except Exception as e:
        print(f"Error during invocation: {e}")
        return {
            "messages": [{"role": "assistant", "content": f"Error processing message: {str(e)}"}],
            "error": str(e)
        }

# Function to visualize the graph
def visualize_graph():
    """Print the graph structure"""
    try:
        # Try to create a visual representation
        import matplotlib.pyplot as plt
        import networkx as nx

        # Create a simple network graph
        G = nx.DiGraph()

        # Add nodes
        nodes = ["START", "router", "classify_message", "save_expense",
                 "handle_query", "send_monthly_report", "handle_error", "END"]
        G.add_nodes_from(nodes)

        # Add edges
        edges = [
            ("START", "router"),
            ("router", "classify_message"),
            ("router", "save_expense"),
            ("router", "handle_query"),
            ("router", "send_monthly_report"),
            ("router", "handle_error"),
            ("router", "END"),
            ("classify_message", "router"),
            ("save_expense", "END"),
            ("handle_query", "END"),
            ("send_monthly_report", "END"),
            ("handle_error", "END")
        ]
        G.add_edges_from(edges)

        # Create layout
        pos = nx.spring_layout(G, k=2, iterations=50)

        # Draw the graph
        plt.figure(figsize=(12, 8))
        nx.draw(G, pos, with_labels=True, node_color='lightblue',
                node_size=2000, font_size=8, font_weight='bold',
                arrows=True, arrowsize=20, edge_color='gray')

        plt.title("Expense Tracker Workflow Architecture", size=16, weight='bold')
        plt.tight_layout()
        plt.show()

    except ImportError:
        # Fallback to text representation
        print("📊 EXPENSE TRACKER ARCHITECTURE")
        print("=" * 50)
        print("""
START
  ↓
router (decides based on message content)
  ├── classify_message → router → save_expense → END
  ├── handle_query → END
  ├── send_monthly_report → END
  ├── handle_error → END
  └── END (for invalid/greeting messages)

FLOW LOGIC:
1. START → router
2. router analyzes message type and routes to:
   - classify_message (for new expenses)
   - handle_query (for questions/reports)
   - send_monthly_report (for email requests)
   - handle_error (for errors)
   - END (for greetings/invalid)
3. classify_message → router (to check if ready to save)
4. save_expense/handle_query/send_monthly_report/handle_error → END
        """)


if __name__ == "__main__":
    print("🚀 Expense Tracker Initialized!")
    print(f"✅ API Key loaded: {'Yes' if os.getenv('API_KEY') else 'No'}")
    print("📊 Visualizing Architecture...")
    visualize_graph()

    print("\n💡 Test the system:")

# Test examples
    test_messages = [
        "I spent 25 JD on groceries",
        "Show me my total spending",
        "Send monthly report",
        "Hello there!"
    ]

    for msg in test_messages:
        print(f"\n📝 Testing: '{msg}'")
        try:
            result = run_expense_tracker(msg)
            print(f"✅ Response: {result['messages'][-1]['content']}")
        except Exception as e:
            print(f"❌ Error: {e}")








