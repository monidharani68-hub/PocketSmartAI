import os
from typing import TypedDict, Annotated, Literal
from langgraph.graph.message import add_messages
from pydantic import BaseModel, Field
from langchain.chat_models import init_chat_model
from config import config


# Initialize configuration first
config()

# Set up LLM
api_key = os.getenv("API_KEY")
if api_key is None:
    raise ValueError("❌ API_KEY not found in environment variables. Please check your .env file.")

os.environ["OPENAI_API_KEY"] = api_key
llm = init_chat_model("openai:gpt-4o-mini")


class State(TypedDict):
    # Messages have the type "list". The `add_messages` function
    # in the annotation defines how this state key should be updated
    # (in this case, it appends messages to the list, rather than overwriting them)
    messages: Annotated[list, add_messages]
    category: str | None
    amount: float | None
    description: str | None

class MessageClassifier(BaseModel):
    category: Literal[
        "housing",
        "food",
        "transportation",
        "healthcare",
        "debt",
        "entertainment",
        "shopping",
        "personal_care",
        "savings",
        "investments",
        "gifts",
        "subscriptions",
        "other"
    ] = Field(
        ...,
        description="Broad classification of spending category if it is housing, food, transportation, healthcare, debt, entertainment, shopping, personal_care, savings, investments, gifts, subscriptions, or other."
    )
    amount: float = Field(..., description="Amount of money spent in the category.")
    description: str = Field(description="Brief description of the expense")
