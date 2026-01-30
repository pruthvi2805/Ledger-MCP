<div align="center">

```
██╗     ███████╗██████╗  ██████╗ ███████╗██████╗     ███╗   ███╗ ██████╗██████╗ 
██║     ██╔════╝██╔══██╗██╔════╝ ██╔════╝██╔══██╗    ████╗ ████║██╔════╝██╔══██╗
██║     █████╗  ██║  ██║██║  ███╗█████╗  ██████╔╝    ██╔████╔██║██║     ██████╔╝
██║     ██╔══╝  ██║  ██║██║   ██║██╔══╝  ██╔══██╗    ██║╚██╔╝██║██║     ██╔═══╝ 
███████╗███████╗██████╔╝╚██████╔╝███████╗██║  ██║    ██║ ╚═╝ ██║╚██████╗██║     
╚══════╝╚══════╝╚═════╝  ╚═════╝ ╚══════╝╚═╝  ╚═╝    ╚═╝     ╚═╝ ╚═════╝╚═╝     
```

### 🔒 Privacy-First Financial Management for AI Assistants

[![Python 3.10+](https://img.shields.io/badge/python-3.10+-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Tests](https://img.shields.io/badge/tests-36%20passing-brightgreen.svg)]()

**Part of [kpruthvi.com](https://kpruthvi.com) developer tools**

</div>

---

**Ledger MCP** transforms your bank statements into conversational financial insights. Ask questions, set budgets, and analyze spending patterns through natural language—all while keeping your data 100% local.

```
You: "What's my burn rate for the last 3 months?"
AI: "Your average monthly spending is ₹45,230..."

You: "Set a ₹10,000 budget for Food"
AI: "Budget set. You're currently at 68% (₹6,800 spent this month)"
```

### Why Ledger MCP?

Most finance apps require you to upload your sensitive bank statements to their cloud. **Ledger MCP is different.**

- **🔒 100% Local Storage:** Your financial data lives in a standard SQLite database on *your* disk.
- **🚫 No Cloud Uploads:** We never see your data. No servers. No APIs.
- **🛑 No Bank Logins:** We parse your PDF/CSV statements locally. No giving away your banking passwords.
- **🤖 Private AI:** Works with local LLMs (via Ollama) or standard AI desktops, but the data retrieval happens strictly on your machine.

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
Built from the ground up for security. Your financial life stays on your laptop, not our servers.

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

Supports CSV or Text-based PDF statements from **any bank**.
Universal parser automatically detects date, amount, and description columns.

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

### Universal Import

**PDF:** Supports text-based PDF statements from **any bank worldwide**. Smart column detection automatically finds date, amount, and description columns.

**CSV:** Generic CSV importer works with **any bank export** or manual spreadsheet. Auto-detects columns (Date, Amount, Description, Debit/Credit).

**Multi-Currency:** Handles any currency format - supports both US/UK style (`1,234.56`) and European style (`1.234,56`). Parses €, $, £, ₹, ¥ symbols automatically.

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

- [ ] Additional bank parsers (Axis, Kotak, IDFC)
- [x] Multi-currency support (EUR, USD, GBP, etc.)
- [x] Global merchant categorization
- [x] Professional PDF Reports
- [ ] Transaction tagging system
- [ ] Analytics dashboard (read-only web UI)
- [ ] Split transaction support

---

## 📊 Ledger MCP vs. Alternatives

| Feature | Ledger MCP | Mint/RocketMoney | Spreadsheets |
|---------|------------|------------------|---------------|
| **Privacy** | ✅ 100% local | ❌ Cloud servers | ✅ Local |
| **Bank Login** | ✅ Not needed | ❌ Required | ✅ Not needed |
| **AI Powered** | ✅ Natural language | ❌ Menu-based | ❌ Manual |
| **Multi-Currency** | ✅ EUR/USD/INR | ⚠️ Limited | ❌ Manual |
| **Auto-Categorize** | ✅ 200+ patterns | ✅ Yes | ❌ Manual |
| **Open Source** | ✅ MIT Licensed | ❌ Proprietary | N/A |
| **Cost** | ✅ Free forever | ⚠️ Subscription | ✅ Free |

---

## Contributing

Contributions welcome! Please open an issue or submit a pull request.

---

## License

MIT License - see LICENSE file for details

---

## 🙏 Acknowledgments

**Built with care by [Pruthvi Kauticwar](https://kpruthvi.com)**

Inspired by the frustration of:
- Uploading bank statements to sketchy online tools
- Sharing banking passwords with aggregator apps
- Privacy policies that read like dystopian fiction

Ledger MCP exists because your financial data should stay **yours**.

---

<div align="center">

## 🚀 Ready to Try It?

<sub>No cloud. No tracking. Just insights.</sub>

---

**⭐ Star this repo if you find it useful!**

Made for developers who value privacy 🔒

[![GitHub stars](https://img.shields.io/github/stars/pruthvi2805/Ledger-MCP?style=social)](https://github.com/pruthvi2805/Ledger-MCP/stargazers)
[![GitHub forks](https://img.shields.io/github/forks/pruthvi2805/Ledger-MCP?style=social)](https://github.com/pruthvi2805/Ledger-MCP/network/members)

**More tools at [kpruthvi.com](https://kpruthvi.com)**

</div>

