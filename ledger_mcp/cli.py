import typer
import uvicorn
import sys
import os
from typing import Optional
from pathlib import Path

# Adjust path so we can import local modules
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from ledger_mcp.core.db import DB
from ledger_mcp.core.security import Security
from ledger_mcp.core.categorizer import Categorizer
from ledger_mcp.parsers.csv_parser import CSVParser
from ledger_mcp.parsers.pdf_parser import PDFParser

app = typer.Typer(help="Ledger MCP: Local-first Finance CLI")

@app.command()
def init():
    """Initialize the database and security configuration."""
    print("Initializing Ledger MCP...")
    DB.init_db()
    
    # Check if config exists, if not setup keys
    with DB.get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT value FROM config WHERE key='salt'")
        if not cursor.fetchone():
            salt = Security.generate_salt()
            cursor.execute("INSERT INTO config (key, value) VALUES (?, ?)", ('salt', salt))
            conn.commit()
            print("Generated new security salt.")
        else:
            print("Database already initialized.")
    
    print("Setup complete. Database at:", DB.db_path)

@app.command()
def ingest(file_path: str, bank: str = "auto", password: Optional[str] = None):
    """Ingest a bank statement (PDF or CSV)."""
    if not os.path.exists(file_path):
        print(f"Error: File not found: {file_path}")
        raise typer.Exit(code=1)

    print(f"Ingesting {file_path}...")
    
    parser = None
    if file_path.lower().endswith('.csv'):
        parser = CSVParser()
    elif file_path.lower().endswith('.pdf'):
        parser = PDFParser()
    else:
        print("Unsupported file format. Use CSV or PDF.")
        raise typer.Exit(code=1)
        
    try:
        transactions = parser.parse(file_path, password=password)
    except Exception as e:
        print(f"Parsing Failed: {e}")
        raise typer.Exit(code=1)
        
    # Insert into DB
    count = 0
    categorizer = Categorizer()
    
    with DB.get_connection() as conn:
        cursor = conn.cursor()
        for txn in transactions:
            # Generate ID
            txn_id = Security.generate_transaction_id(txn.date, txn.amount, txn.description, os.path.basename(file_path))
            
            # Normalize Merchant
            merchant = categorizer.normalize(txn.description)
            # Initial Categorization
            category = categorizer.categorize(txn.description)
            
            # Determine Currency (default to INR if not set)
            currency = getattr(txn, 'currency', 'INR')
            
            # TODO: Add CLI argument for exchange rate or fetch from DB
            # For now, we avoid hardcoding rates as per user request. 
            # Normalized amount defaults to raw amount (assuming 1:1 if unknown).
            # User can update normalization later via MCP tools.
            amount_normalized = txn.amount / 100.0

            try:
                cursor.execute("""
                    INSERT INTO transactions (id, date, amount, description, merchant, category, source_file, currency, amount_normalized)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                """, (txn_id, txn.date, txn.amount, txn.description, merchant, category, os.path.basename(file_path), currency, amount_normalized))
                count += 1
            except Exception:
                # Ignore duplicates (Primary Key collision on ID)
                pass
        conn.commit()
        
    print(f"Successfully ingested {count} new transactions.")

@app.command()
def recategorize():
    """Re-run categorization rules on all transactions."""
    categorizer = Categorizer()
    count = categorizer.recategorize_all()
    print(f"Updated {count} transactions.")

@app.command()
def detect_recurring():
    """Detect and flag recurring transactions."""
    categorizer = Categorizer()
    count = categorizer.detect_recurring()
    print(f"Flagged {count} recurring transaction groups.")

@app.command()
def config(key: str, value: str):
    """
    Set configuration values (e.g., base_currency).
    Usage: ledger config base_currency EUR
    """
    with DB.get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("INSERT OR REPLACE INTO config (key, value) VALUES (?, ?)", 
                      (key.lower(), value.encode('utf-8')))
        conn.commit()
    print(f"OK Config updated: {key.lower()} = {value}")


@app.command()
def mcp():
    """Start the MCP Server (Stdio)."""
    # Delay import to avoid side effects if not running MCP
    from ledger_mcp.interface.mcp_server import start_mcp
    start_mcp()

if __name__ == "__main__":
    app()
