# Ledger MCP

> Privacy-first financial management for AI assistants via Model Context Protocol

[![Python 3.10+](https://img.shields.io/badge/python-3.10+-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Tests](https://img.shields.io/badge/tests-36%20passing-brightgreen.svg)]()

**Ledger MCP** transforms your bank statements into conversational financial insights. Ask questions, set budgets, and analyze spending patterns through natural language—all while keeping your data 100% local.

```
You: "What's my burn rate for the last 3 months?"
AI: "Your average monthly spending is ₹45,230..."

You: "Set a ₹10,000 budget for Food"
AI: "Budget set. You're currently at 68% (₹6,800 spent this month)"

You: "Add expense $20 for GitHub Copilot"
AI: "Since your base currency is EUR, what is the current USD to EUR exchange rate?"
You: "It's 0.92"
AI: "Added transaction. Amount: $20 (Normalized: €18.40)"


```

---

## Features

**AI-Powered Analysis**  
Natural language queries for spending patterns, trends, and insights

**Smart Categorization**  
85% auto-categorization with 80+ merchant patterns. Custom categories supported.

**Budget Management**  
Set limits, track spending, get alerts when approaching budget caps

**Trend Analysis**  
Monthly spending trends, merchant summaries, recurring payment detection

**Full CRUD Operations**  
Add, edit, delete transactions via conversation. Bulk operations supported.

**Global & Multi-Currency **  
Support for INR, USD, EUR. 200+ global merchant patterns (Uber, Amazon, Apple, etc.).

**Professional Reporting**  
Generate beautiful PDF financial reports with charts for monthly reviews.

**Privacy-First Architecture**  
All data stored locally in SQLite. Zero cloud uploads. No external API calls.

---

## Quick Start

### Installation

Requires Python 3.10+

```bash
git clone https://github.com/pruthvi2805/Ledger-MCP
cd Ledger-MCP
pip install -e .
ledger init
```

### Ingest Bank Statements

Supports PDF (HDFC, ICICI, SBI) and CSV formats from any bank.

```bash
ledger ingest ~/Downloads/statement.pdf
# Successfully ingested 150 transactions
```

### Connect to AI

<details>
<summary><b>Claude Desktop</b></summary>

Add to `claude_desktop_config.json`:

**Windows:** `%APPDATA%\Claude\claude_desktop_config.json`  
**macOS:** `~/Library/Application Support/Claude/claude_desktop_config.json`

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

Restart Claude Desktop. Look for the 🔌 icon to confirm connection.

</details>

<details>
<summary><b>Cursor</b></summary>

Add to `cline_mcp_settings.json`:

**Windows:** `%APPDATA%\Cursor\User\globalStorage\saoudrizwan.claude-dev\settings\cline_mcp_settings.json`  
**macOS:** `~/Library/Application Support/Cursor/User/globalStorage/saoudrizwan.claude-dev/settings/cline_mcp_settings.json`

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

Restart Cursor.

</details>

<details>
<summary><b>Windsurf</b></summary>

Add to `cline_mcp_settings.json`:

**Windows:** `%APPDATA%\Windsurf\User\globalStorage\saoudrizwan.claude-dev\settings\cline_mcp_settings.json`  
**macOS:** `~/Library/Application Support/Windsurf/User/globalStorage/saoudrizwan.claude-dev/settings/cline_mcp_settings.json`

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

Restart Windsurf.

</details>

<details>
<summary><b>Other MCP Clients</b></summary>

Standard configuration:

```json
{
  "command": "ledger",
  "args": ["mcp"]
}
```

Or use Python module directly:

```json
{
  "command": "python",
  "args": ["-m", "ledger_mcp.cli", "mcp"]
}
```

</details>

---

## Usage Examples

### Financial Analysis

```
"What's my total spending this month?"
"Show me my top 5 expense categories"
"Compare January vs December spending"
```

### Smart Categorization

```
"Show me uncategorized transactions"
"Categorize that Starbucks transaction as Food"
"Categorize all Uber rides as Transport"
```

### Manual Entry & Corrections

```
"Add a ₹500 cash coffee expense from today"
"Delete that duplicate Netflix transaction"
"Update transaction abc123 category to Entertainment"
```

### Budget Management

```
"Set a ₹10,000 budget for Food"
"Am I over budget on Entertainment?"
"Show me budget status for this month"
```

### Advanced Analysis

```
"Find duplicate transactions"
"Show me Food spending trend for last 6 months"
"Who are my top 10 spending merchants?"
"Find all my subscriptions"
```

---

## MCP Tools

<details>
<summary><b>19 Available Tools</b></summary>

### Read Operations
- `search_transactions` - Find transactions with flexible filters
- `get_monthly_summary` - Spending breakdown by category
- `get_uncategorized` - View transactions needing categorization
- `get_all_categories` - List all categories in use

### Write Operations
- `add_transaction` - Manually add cash purchases or pending items
- `update_transaction` - Edit existing transaction details
- `delete_transaction` - Remove duplicates or errors

### Categorization
- `categorize_transaction` - Categorize with optional rule creation
- `categorize_batch` - Bulk categorize multiple transactions
- `add_rule` - Create regex-based categorization rules

### Rule Management
- `list_rules` - View all categorization rules
- `delete_rule` - Remove unwanted rules

### Budget Management
- `set_budget` - Set monthly budget limits
- `get_budget_status` - Check budget vs actual spending
- `set_base_currency` - **NEW** Set primary currency (INR, USD, EUR, etc.)

### Analysis & Trends
- `find_recurring` - Detect subscriptions automatically
- `find_duplicates` - Find potential duplicate transactions
- `get_category_trend` - Monthly spending trends for a category
- `get_merchant_summary` - Top spending merchants
- `generate_monthly_report` - **NEW** Generate PDF report with charts
- `smart_categorize_uncategorized` - AI-powered categorization (opt-in)

</details>

---

## Architecture

### Privacy-First Design

All data stored locally in SQLite. No external API calls. No cloud uploads.

```
Your Computer
├── ledger.db (SQLite)          ← All your financial data
├── Bank Statements (PDF/CSV)   ← Source files (can be deleted after ingestion)
└── AI Assistant (MCP)          ← Queries local database only
```

### Smart Categorization

**Auto-categorization:** 85% of transactions categorized automatically using **200+ global merchant patterns** (including US, UK, EU, India).

**Rule Engine:** Create custom rules with regex patterns. Rules apply retroactively.

**AI-Assisted:** Optional AI-powered categorization for edge cases (privacy-conscious, opt-in)

### Supported Banks

**PDF Parsing:**
- HDFC Bank
- ICICI Bank
- SBI (State Bank of India)

**CSV Import:**
- Any bank's CSV export (generic parser with auto-column detection)

---

## Technical Details

<details>
<summary><b>Tech Stack</b></summary>

- **Language:** Python 3.10+
- **Database:** SQLite with Row factory
- **MCP Framework:** FastMCP
- **CLI:** Typer
- **PDF Parsing:** PyPDF2
- **Testing:** pytest with 36 passing tests

</details>

<details>
<summary><b>Performance</b></summary>

- Ingestion: 1000 transactions in <2 seconds
- Search: Sub-100ms for most queries
- Memory: <50MB for 5000+ transactions
- Stress-tested with 5000+ transactions

</details>

<details>
<summary><b>Security</b></summary>

- Local-only data storage (no network calls)
- Database file permissions: 0o600 (owner read/write only)
- Transaction IDs: Cryptographically secure hashing
- No PII sent to external services

</details>

---

## Development

### Running Tests

```bash
pytest tests/ -v
# 36 passed, 144 warnings
```

### Project Structure

```
Ledger-MCP/
├── ledger_mcp/
│   ├── core/              # Database, categorizer, security
│   ├── interface/         # MCP server, CLI
│   └── parsers/           # PDF & CSV parsers
├── tests/                 # Comprehensive test suite
├── scripts/               # Utility scripts
└── dummy_statement.csv    # Sample data (109 transactions)
```

---

## Roadmap

- [ ] Additional bank support (Axis, Kotak, IDFC)
- [ ] Multi-currency support
- [ ] Transaction tagging system
- [ ] Export to CSV/PDF reports
- [ ] Analytics dashboard (read-only web UI)
- [ ] Merchant name normalization
- [ ] Split transaction support

---

## Contributing

Contributions welcome! Please open an issue or submit a pull request.

---

## License

MIT License - see LICENSE file for details

---

## Acknowledgments

Built with [FastMCP](https://github.com/jlowin/fastmcp) by Marvin AI team.

Inspired by the need for privacy-first financial tools in the age of AI assistants.

---

**Questions?** Open an issue on GitHub.

**Privacy Concerns?** All data stays on your machine. Review the source code—it's open source.
