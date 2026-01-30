# Ledger MCP: AI-Powered Personal Finance Manager 💰

**Ledger MCP** is a privacy-first financial management tool that connects your bank statements to AI assistants via the Model Context Protocol (MCP).

**🔒 100% Local. Zero Cloud Uploads. Your data never leaves your machine.**

Works with any MCP-compatible AI client: **Claude Desktop**, **Cursor**, **Windsurf**, **Cline**, and more.

**Key Features:**
- 🤖 **AI-Powered Analysis** - Ask natural language questions about your finances
- 🏷️ **Smart Categorization** - 85% auto-categorization with 80+ merchant patterns
- 💰 **Budget Tracking** - Set limits and monitor spending
- 📊 **Trend Analysis** - Burn rate, recurring payments, spending patterns
- ✏️ **Full CRUD** - Add, edit, delete transactions via conversation
- 🔐 **Privacy-First** - All data stays local, no cloud uploads

---

## 🚀 Quick Start (3 Steps)

### Step 1: Install

Requires **Python 3.10+**

```bash
git clone https://github.com/pruthvi2805/Ledger-MCP
cd Ledger-MCP
pip install -e .
ledger init
```

This creates a secure local database at `Ledger-MCP/ledger.db`

---

### Step 2: Add Your Bank Statements

Put your statements **anywhere** (Downloads, Desktop, Documents - your choice!)

```bash
# Auto-detects HDFC, ICICI, SBI formats
ledger ingest ~/Downloads/statement.pdf

# Works with CSV too
ledger ingest ~/Documents/transactions.csv
```

**Supported Formats:**
- 📄 PDF statements (HDFC, ICICI, SBI)
- 📊 CSV exports (any bank)

---

### Step 3: Connect to Your AI

The MCP works with **any MCP-compatible AI client**. Choose your favorite:

<details>
<summary><b>🔵 Claude Desktop</b></summary>

**Config Location:**
- Windows: `%APPDATA%\Claude\claude_desktop_config.json`
- Mac: `~/Library/Application Support/Claude/claude_desktop_config.json`

**Add this:**
```json
{
  "mcpServers": {
    "ledger": {
      "command": "ledger",
      "args": ["mcp"]
    }
  }
}
```

**Restart Claude Desktop** and look for the 🔌 icon.

> **Troubleshooting:** If you see "Connection Error", use the absolute Python path:
> ```json
> {
>   "command": "C:\\Users\\You\\AppData\\Local\\Programs\\Python\\Python311\\python.exe",
>   "args": ["-m", "ledger_mcp.cli", "mcp"]
> }
> ```

</details>

<details>
<summary><b>⚡ Cursor</b></summary>

**Config Location:**
- Windows: `%APPDATA%\Cursor\User\globalStorage\saoudrizwan.claude-dev\settings\cline_mcp_settings.json`
- Mac: `~/Library/Application Support/Cursor/User/globalStorage/saoudrizwan.claude-dev/settings/cline_mcp_settings.json`

**Add this:**
```json
{
  "mcpServers": {
    "ledger": {
      "command": "ledger",
      "args": ["mcp"]
    }
  }
}
```

**Restart Cursor** and the MCP will be available in Cline/Claude Dev extension.

</details>

<details>
<summary><b>🌊 Windsurf</b></summary>

**Config Location:**
- Windows: `%APPDATA%\Windsurf\User\globalStorage\saoudrizwan.claude-dev\settings\cline_mcp_settings.json`
- Mac: `~/Library/Application Support/Windsurf/User/globalStorage/saoudrizwan.claude-dev/settings/cline_mcp_settings.json`

**Add this:**
```json
{
  "mcpServers": {
    "ledger": {
      "command": "ledger",
      "args": ["mcp"]
    }
  }
}
```

**Restart Windsurf** and the MCP will be available.

</details>

<details>
<summary><b>🔧 Other MCP Clients</b></summary>

Any tool that supports the [Model Context Protocol](https://modelcontextprotocol.io/) can use Ledger MCP.

**Standard Configuration:**
```json
{
  "command": "ledger",
  "args": ["mcp"]
}
```

Or use the Python module directly:
```json
{
  "command": "python",
  "args": ["-m", "ledger_mcp.cli", "mcp"]
}
```

</details>

---

## � Example Conversations

Once connected, try these prompts:

**Financial Analysis:**
- *"What's my total spending this month?"*
- *"Show me my top 5 expense categories"*
- *"Compare my spending: January vs February"*

**Smart Categorization:**
- *"Categorize all Swiggy transactions as Food Delivery"*
- *"Find uncategorized transactions and suggest categories"*

**Recurring Payments:**
- *"List all my subscriptions"*
- *"Which recurring payments can I cancel to save money?"*

**Budget Tracking:**
- *"Am I over budget on Food this month?"*
- *"Set a ₹10,000 budget for Entertainment"*

---



---

## 💬 Example Conversations

Once connected to your AI assistant, you can interact naturally:

**Financial Analysis:**
```
You: "What's my total spending this month?"
AI: "You spent ₹45,230 in January across 8 categories..."

You: "Show me my top 5 expense categories"
AI: "1. Food: ₹12,500 | 2. Transport: ₹8,200 | 3. Shopping: ₹7,100..."

You: "Compare my spending: January vs December"
AI: "January spending increased by 15% compared to December..."
```

**Smart Categorization:**
```
You: "Show me uncategorized transactions"
AI: "You have 12 uncategorized transactions..."

You: "That Starbucks transaction should be Food"
AI: "✓ Categorized 'Starbucks' as Food and created a rule for future transactions"

You: "Categorize all Uber rides as Transport"
AI: "✓ Created rule: UBER → Transport. Auto-categorized 8 transactions"
```

**Manual Entry & Corrections:**
```
You: "Add a ₹500 cash coffee expense from today"
AI: "✓ Added transaction: Coffee (₹500.00) on 2026-01-30 → Food"

You: "Delete that duplicate Netflix transaction"
AI: "✓ Deleted transaction: Netflix (₹499.00)"

You: "Update transaction abc123 to ₹1000"
AI: "✓ Updated transaction abc123"
```

**Budget Management:**
```
You: "Set a ₹10,000 budget for Food"
AI: "✓ Set budget for 'Food': ₹10,000/month"

You: "Am I over budget on Entertainment?"
AI: "You've spent ₹3,200 of your ₹5,000 Entertainment budget (64%)"
```

**Smart Features:**
```
You: "Find duplicate transactions"
AI: "Found 2 potential duplicates: Netflix ₹499 on 2026-01-03..."

You: "List all my categorization rules"
AI: "You have 5 rules: SWIGGY → Food, UBER → Transport..."

You: "Find all my subscriptions"
AI: "Detected 4 recurring payments: Netflix (₹499), Spotify (₹119)..."
```

---

## 🤖 MCP Capabilities

Ledger MCP provides **19 powerful tools** for AI-powered financial management:

### 📖 Read Operations
- `search_transactions` - Find transactions with flexible filters
- `get_monthly_summary` - Spending breakdown by category
- `get_uncategorized` - View transactions needing categorization
- `get_all_categories` - List all categories in use

### ✏️ Write Operations (Full CRUD)
- `add_transaction` - Manually add cash purchases or pending items
- `update_transaction` - Edit existing transaction details
- `delete_transaction` - Remove duplicates or errors

### 🏷️ Categorization
- `categorize_transaction` - Categorize with optional rule creation
- `categorize_batch` - **NEW** Bulk categorize multiple transactions at once
- `add_rule` - Create regex-based categorization rules

### 📋 Rule Management
- `list_rules` - View all categorization rules
- `delete_rule` - Remove unwanted rules

### 💰 Budget Management
- `set_budget` - Set monthly budget limits
- `get_budget_status` - Check budget vs actual spending (with % used)

### 📊 Analysis & Trends
- `find_recurring` - Detect subscriptions automatically
- `find_duplicates` - Find potential duplicate transactions
- `get_category_trend` - **NEW** Monthly spending trends for a category
- `get_merchant_summary` - **NEW** Top spending merchants across categories
- `smart_categorize_uncategorized` - AI-powered categorization (opt-in)

**Example Conversations:**
```
"Add a ₹500 cash coffee expense from today"
"Delete that duplicate Netflix transaction"
"Set a ₹10,000 budget for Food"
"Find all my subscriptions"
```

---

## 🛠️ Features

### 🔒 Privacy-First
- **Zero cloud uploads** - Everything runs locally
- **Encrypted storage** - SQLite database with secure permissions
- **No telemetry** - Your data stays on your machine

### 🧠 Smart Categorization
- **Auto-learning** - Remembers your categorization preferences
- **Regex-based rules** - Powerful pattern matching
- **Priority system** - Fine-grained control over rules

### 🇮🇳 Indian Banking Support
- **Native parsers** for HDFC, ICICI, SBI PDF statements
- **Generic CSV loader** for any bank
- **Handles Indian number formats** (₹10,00,000)


---

## 🗂️ File Organization

**You control where your files live!**

```
Your Computer/
├── Downloads/
│   └── hdfc_statement_jan.pdf    ← Put statements anywhere
├── Documents/
│   └── bank_exports.csv           ← CSV files work too
└── Ledger-MCP/
    └── ledger.db                  ← Database stays here (auto-created)
```

The `ledger ingest` command works with **absolute or relative paths**, so organize your statements however you prefer.

---

## 🔧 Advanced Commands

```bash
# Re-run categorization after adding new rules
ledger recategorize

# Detect recurring subscriptions
ledger detect-recurring

# Start MCP server manually (for debugging)
ledger mcp
```

---

## 🧪 Testing & Development

We maintain **67% test coverage** with comprehensive edge case validation.

```bash
pip install pytest pytest-cov
pytest tests/ --cov=ledger_mcp
```

**Test Results:**
- ✅ 36/36 tests passing
- ✅ Stress tested with 5000+ transactions
- ✅ All core modules >80% coverage

---

## 🤝 Contributing

Found a bug? Want to add support for your bank? PRs welcome!

1. Fork the repo
2. Create a feature branch
3. Add tests for your changes
4. Submit a PR

---

## 📜 License

MIT License - Use freely, commercially or personally.

---

## 🙏 Credits

Built with:
- [FastMCP](https://github.com/jlowin/fastmcp) - MCP server framework
- [Typer](https://typer.tiangolo.com/) - CLI framework
- [pdfplumber](https://github.com/jsvine/pdfplumber) - PDF parsing

**Made for privacy-conscious users who want AI-powered financial insights without cloud uploads.**
