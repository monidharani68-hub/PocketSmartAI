# 💰 Simple Budget Collection Assistant-Under Development

A smart, AI-powered personal budget tracker that helps you log expenses, analyze spending patterns, and get personalized money-saving recommendations.

## ✨ Features

- 🤖 **Natural Language Processing** - Just say "I spent $25 on groceries"
- 📊 **Smart Analytics** - Weekly, monthly, and yearly spending breakdowns
- 💡 **AI Recommendations** - Personalized tips to save money based on your patterns
- 📄 **Data Export** - Export your expenses to CSV for further analysis
- 💾 **Multiple Storage Options** - JSON, SQLite, or easily extend to cloud storage
- 🎯 **Simple Categories** - Food, transport, shopping, bills, entertainment, health, other

## 🚀 Quick Start

### Prerequisites

```bash
pip install openai langchain-openai langgraph python-dotenv pydantic
```

### Setup

1. Clone the repository:
```bash
git clone https://github.com/LaithAltawil/Budget_Assistant.git
cd Budget_Assistant
```

2. Create a `.env` file:
```env
API_KEY=your_openai_api_key_here
```

3. Run the assistant:
```bash
python budget_assistant.py
```

## 💬 Usage Examples

### Log Expenses
```
You: I spent $15 on lunch
Assistant: 💰 Saved: $15.00 for lunch (food)

You: Paid 50 for gas today
Assistant: 💰 Saved: $50.00 for gas (transport)
```

### View Analytics
```
You: show monthly spending
Assistant: 📅 Period Spending Analysis

This Week (Last 7 days): $127.50
  • food: $45.00
  • transport: $30.00

This Month: $340.25
  • food: $120.00
  • shopping: $95.75
```

### Get Recommendations
```
You: give me money saving tips
Assistant: 💡 Money Saving Recommendations

🎯 Focus Area: Food ($120.00 - 35.3% of spending)

Specific tips for food:
🍳 Cook at home more often - can save 60-70% vs eating out
📝 Plan meals weekly and make shopping lists
🛒 Buy generic brands - often 20-40% cheaper
```

### Export Data
```
You: export to csv
Assistant: 📄 Exported 47 expenses to expenses_export_20250720_143022.csv
```

## 🛠️ Architecture

Built with **LangGraph** for intelligent routing and state management:

![Architecture.png](Architure.png)

### Key Components

- **State Management** - TypedDict with LangGraph for conversation flow
- **AI Processing** - OpenAI GPT-4o-mini for cost-effective natural language understanding
- **Smart Router** - Automatically detects user intent and routes to appropriate function
- **Data Storage** - JSON files (free), SQLite (free), easily extensible to cloud

## 💾 Storage Options

### Current (Free)
- **JSON Files** - Simple, portable, version controllable
- **SQLite** - Structured queries, better for large datasets

### Easy Extensions
- **Google Sheets API** - 100 requests/100 seconds (free tier)
- **Supabase** - 500MB database, 2M row inserts/month (free)
- **Firebase** - 1GB storage, 50k reads/day (free)

## 🔧 Configuration

### Model Selection
```python
# Current: Cost-effective
llm = ChatOpenAI(model="gpt-4o-mini")

# Upgrade option: More powerful
llm = ChatOpenAI(model="gpt-4")
```

### Categories
Easily customize spending categories in `ExpenseData` class:
```python
category: Literal[
    "food", "transport", "shopping", "bills", 
    "entertainment", "health", "other"
]
```

## 🤝 Contributing

Ideas for contributions:
- 📱 Web interface with Streamlit/Flask
- 📈 Advanced visualizations with Plotly
- 🔔 Budget alerts and notifications
- 🏦 Bank account integration
- 📊 More detailed analytics
- 🌐 Multi-currency support

## 🙏 Acknowledgments

- Built with [LangGraph](https://github.com/langchain-ai/langgraph) for intelligent workflow management
- Powered by [OpenAI](https://openai.com/) for natural language processing
- Inspired by the need for simple, AI-powered personal finance tools

## 📞 Support

If you have questions or need help:
1. Check the [Issues](https://github.com/LaithAltawil/Budget_Assistant/issues) page
2. Create a new issue with detailed description
3. Star ⭐ the repo if you find it helpful!

---
**Made with ❤️ for better personal finance management**
