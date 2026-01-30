<div align="center">

```
██╗     ███████╗██████╗  ██████╗ ███████╗██████╗     ███╗   ███╗ ██████╗██████╗ 
██║     ██╔════╝██╔══██╗██╔════╝ ██╔════╝██╔══██╗    ████╗ ████║██╔════╝██╔══██╗
██║     █████╗  ██║  ██║██║  ███╗█████╗  ██████╔╝    ██╔████╔██║██║     ██████╔╝
██║     ██╔══╝  ██║  ██║██║   ██║██╔══╝  ██╔══██╗    ██║╚██╔╝██║██║     ██╔═══╝ 
███████╗███████╗██████╔╝╚██████╔╝███████╗██║  ██║    ██║ ╚═╝ ██║╚██████╗██║     
╚══════╝╚══════╝╚═════╝  ╚═════╝ ╚══════╝╚═╝  ╚═╝    ╚═╝     ╚═╝ ╚═════╝╚═╝     
```

### 🔒 Privacy-First Financial Intelligence for AI Assistants

[![Python 3.10+](https://img.shields.io/badge/python-3.10+-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Tests](https://img.shields.io/badge/tests-passing-brightgreen.svg)]()

**Empower your AI to analyze your finances without ever seeing your bank credentials.**

[Features](#features) • [Installation](#installation) • [Usage](#usage) • [MCP Configuration](#mcp-configuration) • [Contributing](#contributing)

</div>

---

**Ledger MCP** turns your local bank statements into a conversational database. By running as a Model Context Protocol (MCP) server, it allows AI tools like Claude Desktop, Cursor, and Windsurf to answer questions about your finances, manage budgets, and generate reports—**all while your data stays 100% local on your machine.**

### Why Ledger MCP?

| Feature | Ledger MCP | Mint/RocketMoney | Spreadsheets |
|---------|------------|------------------|---------------|
| **Privacy** | ✅ **100% Local (SQLite)** | ❌ Cloud Servers | ✅ Local |
| **Credentials** | ✅ **No Login Required** | ❌ Banking Passwords | ✅ Not Needed |
| **Control** | ✅ **Interactive Mapping** | ❌ "Black Box" | ❌ Manual Entry |
| **AI Power** | ✅ **Natural Language** | ❌ Click-based UI | ❌ Formulas |
| **Cost** | ✅ **Free & Open Source** | ⚠️ Subscription | ✅ Free |

---

## Features

- **📂 Universal Ingestion**: Parse PDF and CSV statements from *any* bank using our intelligent fallback parser.
- **🖐️ Interactive Mode**: Manually map columns for complex PDF layouts—do it once, apply to all pages.
- **🤖 Smart Categorization**: Auto-categorizes 85% of transactions using 200+ global merchant patterns (Uber, Amazon, etc.).
- **💰 Multi-Currency**: Native support for USD, EUR, INR, GBP, and more.
- **📊 Professional Reporting**: Generate detailed PDF monthly reports with charts and insights.
- **🛡️ Privacy Architecture**: Zero data exfiltration. No APIs. No tracking.

---

## Installation

### Prerequisites
- Python 3.10 or higher
- Git

### Quick Start

1. **Clone the repository**
   ```bash
   git clone https://github.com/pruthvi2805/Ledger-MCP
   cd Ledger-MCP
   ```

2. **Install the package**
   ```bash
   # Install in editable mode (recommended)
   python -m pip install -e .
   ```

3. **Initialize the Database**
   ```bash
   python -m ledger_mcp.cli init
   ```
   *This creates a secured `ledger.db` file in the project directory.*

4. **Set your Base Currency** (Optional, defaults to INR)
   ```bash
   python -m ledger_mcp.cli config base_currency EUR
   ```

---

## Usage

### 1. Ingesting Bank Statements

Ledger MCP supports both automatic and interactive ingestion.

#### Option A: Automatic Ingestion (Fastest)
Best for standard formats. The parser auto-detects Date, Description, and Amount columns.

```bash
python -m ledger_mcp.cli ingest "C:\Users\YourName\Downloads\statement.pdf"
```

#### Option B: Interactive Mode (Most Reliable) ✨
Use this if the automatic parser isn't perfect or misses columns, or for complex layouts. You manually identify columns once, and the tool applies it to the whole file.

```bash
python -m ledger_mcp.cli ingest "C:\Users\YourName\Downloads\statement.pdf" -i
```
> **Pro Tip:** You only need to map the columns for the first page. When asked, select "Apply to all pages" to process the entire document instantly.

### 2. Generating Reports
Create a beautiful PDF summary of your month.

```bash
python -m ledger_mcp.cli report --month 01 --year 2026
```

---

## MCP Configuration

Connect Ledger MCP to your favorite AI assistant to chat with your data.

### 🤖 Claude Desktop

Add this to your `claude_desktop_config.json`:

**Windows:** `%APPDATA%\Claude\claude_desktop_config.json`  
**macOS:** `~/Library/Application Support/Claude/claude_desktop_config.json`

```json
{
  "mcpServers": {
    "ledger": {
      "command": "python",
      "args": ["-m", "ledger_mcp.cli", "mcp"]
    }
  }
}
```

### 💻 Cursor

Add this to your `cline_mcp_settings.json`:

**Windows:** `%APPDATA%\Cursor\User\globalStorage\saoudrizwan.claude-dev\settings\cline_mcp_settings.json`

```json
{
  "mcpServers": {
    "ledger": {
      "command": "python",
      "args": ["-m", "ledger_mcp.cli", "mcp"]
    }
  }
}
```

*Restart your editor/app after updating the config.*

---

## What Can I Ask?

Once connected, you can ask your AI assistant questions like:

**Analysis**
> "What is my burn rate for the last 3 months?"
> "Show me a pie chart of my expenses in January."
> "How much did I spend on Uber this year?"

**Budgeting**
> "Set a budget of €200 for Restaurants."
> "Am I over budget on Shopping?"

**Data Cleaning**
> "Find subscription payments that recur monthly."
> "Categorize all transactions from 'Supermarkt' as Groceries."

---

## Contributing

We welcome contributions! Whether it's adding a new bank parser, fixing a bug, or improving documentation.

1. Fork the repo.
2. Create feature branch: `git checkout -b feature/amazing-feature`
3. Commit changes: `git commit -m 'feat: Add amazing feature'`
4. Push to branch: `git push origin feature/amazing-feature`
5. Open a Pull Request.

### Running Tests
```bash
pytest tests/ -v
```

---

## License

Distributed under the MIT License. See `LICENSE` for more information.

---

<div align="center">
  <b>Built with ❤️ by <a href="https://kpruthvi.com">Pruthvi Kauticwar</a></b><br>
  <sub>Your Financial Data. Your Control.</sub>
</div>
