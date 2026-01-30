from mcp.server.fastmcp import FastMCP
from typing import Optional, List, Dict
import json
from ledger_mcp.core.db import DB
from ledger_mcp.core.categorizer import Categorizer

# Create MCP Server
mcp = FastMCP("ledger-mcp")

@mcp.tool()
def search_transactions(keyword: str = None, min_amount: float = None, max_amount: float = None, category: str = None, start_date: str = None, end_date: str = None, limit: int = 10) -> List[Dict]:
    """
    Search for transactions based on various filters.
    """
    query = "SELECT * FROM transactions WHERE 1=1"
    params = []
    
    if keyword:
        query += " AND (description LIKE ? OR merchant LIKE ?)"
        keyword_wc = f"%{keyword}%"
        params.extend([keyword_wc, keyword_wc])
    
    if min_amount is not None:
        query += " AND amount >= ?"
        params.append(int(min_amount * 100))
        
    if max_amount is not None:
        query += " AND amount <= ?"
        params.append(int(max_amount * 100))
        
    if category:
        query += " AND category = ?"
        params.append(category)

    if start_date:
        query += " AND date >= ?"
        params.append(start_date)

    if end_date:
        query += " AND date <= ?"
        params.append(end_date)
        
    query += " ORDER BY date DESC LIMIT ?"
    params.append(limit)
    
    with DB.get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute(query, params)
        rows = cursor.fetchall()
        
    return [
        {
            "id": row['id'],
            "date": row['date'],
            "amount": row['amount'] / 100.0,
            "description": row['description'],
            "category": row['category']
        }
        for row in rows
    ]

@mcp.tool()
def get_monthly_summary(month: int, year: int) -> Dict[str, Dict[str, float]]:
    """
    Get spending summary by category and currency for a specific month.
    Returns: {"Food": {"INR": -5000, "USD": -20}, ...}
    """
    start_date = f"{year}-{month:02d}-01"
    if month == 12:
        end_date = f"{year+1}-01-01"
    else:
        end_date = f"{year}-{month+1:02d}-01"
        
    with DB.get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("""
            SELECT category, currency, SUM(amount) as total 
            FROM transactions 
            WHERE date >= ? AND date < ? 
            GROUP BY category, currency
        """, (start_date, end_date))
        rows = cursor.fetchall()
        
    summary = {}
    for row in rows:
        cat = row['category']
        curr = row['currency'] or 'INR'
        amount = row['total'] / 100.0
        
        if cat not in summary:
            summary[cat] = {}
        summary[cat][curr] = amount
        
    return summary

@mcp.tool()
def find_recurring() -> List[Dict]:
    """
    Find recurring subscriptions or regular payments.
    """
    # Auto-detect before returning
    Categorizer().detect_recurring()

    with DB.get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM transactions WHERE is_recurring = 1 ORDER BY date DESC")
        rows = cursor.fetchall()
        
    return [
        {
            "merchant": row['merchant'],
            "amount": row['amount'] / 100.0,
            "description": row['description'],
            "date": row['date']
        }
        for row in rows
    ]

@mcp.tool()
def get_budget_status(month: int, year: int) -> str:
    """
    Compare actual spending vs budget targets.
    """
    # 1. Fetch Targets
    targets = {}
    with DB.get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT value FROM config WHERE key='budget_targets_json'")
        row = cursor.fetchone()
        if row and row['value']:
            try:
                targets = json.loads(row['value'])
            except:
                pass

    if not targets:
        return "No budget targets set."

    # 2. Fetch Actuals (multi-currency format: {"Food": {"INR": -5000, "EUR": -20}, ...})
    actuals_raw = get_monthly_summary(month, year)
    
    # Flatten to single value per category (sum all currencies)
    actuals = {}
    for cat, currency_dict in actuals_raw.items():
        if isinstance(currency_dict, dict):
            actuals[cat] = sum(currency_dict.values())
        else:
            actuals[cat] = currency_dict
    
    # 3. Compare - FIXED: Use absolute values for comparison
    report = []
    for cat, limit in targets.items():
        spent = actuals.get(cat, 0.0)
        # Both spent and limit are negative for expenses
        # Compare absolute values: abs(-15000) > abs(-10000) → OVER
        if abs(spent) > abs(limit):
            status = "OVER BUDGET"
            percent = (abs(spent) / abs(limit) * 100) if limit != 0 else 0
        else:
            status = "OK"
            percent = (abs(spent) / abs(limit) * 100) if limit != 0 else 0
        
        report.append(f"{cat}: Spent ₹{abs(spent):.2f} / Limit ₹{abs(limit):.2f} ({percent:.0f}%) - {status}")
        
    return "\n".join(report)

@mcp.tool()
def add_rule(pattern: str, category: str) -> str:
    """
    Add a new categorization rule and apply it to existing transactions.
    Pattern is a regex that will match against transaction descriptions.
    Category can be any string - custom categories are fully supported.
    """
    with DB.get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("INSERT INTO rules (pattern, category, priority) VALUES (?, ?, ?)", 
                       (pattern, category, 20))
        conn.commit()
    
    # Auto-apply logic
    cat = Categorizer()
    updated = cat.recategorize_all()
        
    return f"Rule added: '{pattern}' → '{category}'. Auto-updated {updated} transactions."

@mcp.tool()
def categorize_transaction(transaction_id: str, category: str, create_rule: bool = False) -> str:
    """
    Categorize a specific transaction by its ID. 
    If create_rule is True, creates a rule based on the transaction's description 
    so similar transactions are auto-categorized in the future.
    Category can be ANY string - users can create custom categories on the fly.
    """
    with DB.get_connection() as conn:
        cursor = conn.cursor()
        
        # Get transaction details
        cursor.execute("SELECT description, merchant FROM transactions WHERE id = ?", (transaction_id,))
        row = cursor.fetchone()
        if not row:
            return f"Error: Transaction ID '{transaction_id}' not found."
        
        description = row['description']
        merchant = row['merchant'] or description
        
        # Update category
        cursor.execute("UPDATE transactions SET category = ? WHERE id = ?", (category, transaction_id))
        
        # Optionally create rule
        if create_rule:
            # Use merchant name as pattern (more reliable than full description)
            import re
            pattern = re.escape(merchant.split()[0]) if merchant else re.escape(description.split()[0])
            cursor.execute("INSERT INTO rules (pattern, category, priority) VALUES (?, ?, ?)", 
                          (pattern, category, 20))
        
        conn.commit()
    
    if create_rule:
        return f"✓ Categorized '{description}' as '{category}' and created a rule for similar transactions."
    else:
        return f"✓ Categorized '{description}' as '{category}' (one-time only)."

@mcp.tool()
def get_uncategorized(limit: int = 20) -> List[Dict]:
    """
    Get uncategorized transactions so the user can categorize them via conversation.
    Returns transaction details including ID, date, amount, and description.
    """
    with DB.get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("""
            SELECT id, date, amount, description, merchant 
            FROM transactions 
            WHERE category = 'Uncategorized' 
            ORDER BY date DESC 
            LIMIT ?
        """, (limit,))
        rows = cursor.fetchall()
    
    return [
        {
            "id": row['id'],
            "date": row['date'],
            "amount": row['amount'] / 100.0,
            "description": row['description'],
            "merchant": row['merchant'] or "Unknown"
        }
        for row in rows
    ]

@mcp.tool()
def get_all_categories() -> List[str]:
    """
    Get all unique categories currently in use (both from rules and transactions).
    This helps users see what categories are available and maintain consistency.
    """
    with DB.get_connection() as conn:
        cursor = conn.cursor()
        
        # Get categories from transactions
        cursor.execute("SELECT DISTINCT category FROM transactions WHERE category != 'Uncategorized'")
        txn_cats = {row['category'] for row in cursor.fetchall()}
        
        # Get categories from rules
        cursor.execute("SELECT DISTINCT category FROM rules")
        rule_cats = {row['category'] for row in cursor.fetchall()}
        
        # Combine and sort
        all_cats = sorted(txn_cats | rule_cats)
    
    return all_cats if all_cats else ["No categories defined yet. You can create any category you want!"]

@mcp.tool()
def set_base_currency(currency: str) -> str:
    """
    Set the primary currency for reporting and normalization (e.g., 'EUR', 'USD', 'INR').
    Default is 'INR'. verified against supported currencies.
    """
    supported = ["INR", "USD", "EUR", "GBP", "JPY", "CAD", "AUD"]
    if currency.upper() not in supported:
        return f"Error: Currency '{currency}' not supported. Use one of: {', '.join(supported)}"
        
    with DB.get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("INSERT OR REPLACE INTO config (key, value) VALUES (?, ?)", 
                      ('base_currency', currency.upper().encode('utf-8')))
        conn.commit()
    
    return f"✓ Base currency set to {currency.upper()}. Future reports will use this as the primary currency."

def _get_base_currency() -> str:
    with DB.get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT value FROM config WHERE key='base_currency'")
        row = cursor.fetchone()
        if row and row['value']:
            return row['value'].decode('utf-8')
    return "INR"

@mcp.tool()
def add_transaction(date: str, amount: float, description: str, category: str = "Uncategorized", merchant: str = None, currency: str = None, exchange_rate: float = None) -> str:
    """
    Manually add a transaction.
    date: YYYY-MM-DD
    amount: positive/negative (in the transaction currency)
    currency: ISO code (defaults to System Base Currency if not provided)
    exchange_rate: (Optional) Rate to convert to Base Currency. Required if currency != base.
    """
    from ledger_mcp.core.security import Security
    
    base_currency = _get_base_currency()
    txn_currency = currency.upper() if currency else base_currency
    
    # 1. Validation: Require Exchange Rate for Foreign Currencies
    if txn_currency != base_currency and exchange_rate is None:
        return f"Error: Transaction is in {txn_currency} but Base Currency is {base_currency}. Please provide `exchange_rate` (Rate: 1 {txn_currency} = X {base_currency}) or convert the amount manually."

    # Generate unique ID
    txn_id = Security.generate_transaction_id(date, int(amount * 100), description, "manual_entry")
    
    # Normalize merchant
    cat = Categorizer()
    if not merchant:
        merchant = cat.normalize(description)
        
    # 2. Calculate Normalized Amount
    if txn_currency == base_currency:
        amount_normalized = amount
    else:
        # Use provided realtime rate
        amount_normalized = amount * exchange_rate
    
    with DB.get_connection() as conn:
        cursor = conn.cursor()
        try:
            cursor.execute("""
                INSERT INTO transactions (id, date, amount, description, merchant, category, source_file, currency, amount_normalized)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (txn_id, date, int(amount * 100), description, merchant, category, "manual", txn_currency, amount_normalized))
            conn.commit()
            return f"✓ Added transaction: {description} ({txn_currency} {amount:.2f}) → Normalized: {base_currency} {amount_normalized:.2f} (Rate: {exchange_rate or 1.0})"
        except Exception as e:
            return f"Error: Could not add transaction. {str(e)}"

@mcp.tool()
def update_transaction(transaction_id: str, category: str = None, description: str = None, amount: float = None, date: str = None) -> str:
    """
    Update an existing transaction's details.
    Only provided fields will be updated.
    Amount should be in rupees (will be converted to paise internally).
    """
    with DB.get_connection() as conn:
        cursor = conn.cursor()
        
        # Check if transaction exists
        cursor.execute("SELECT * FROM transactions WHERE id = ?", (transaction_id,))
        if not cursor.fetchone():
            return f"Error: Transaction ID '{transaction_id}' not found."
        
        # Build update query dynamically
        updates = []
        params = []
        
        if category is not None:
            updates.append("category = ?")
            params.append(category)
        if description is not None:
            updates.append("description = ?")
            params.append(description)
        if amount is not None:
            updates.append("amount = ?")
            params.append(int(amount * 100))
        if date is not None:
            updates.append("date = ?")
            params.append(date)
        
        if not updates:
            return "Error: No fields to update."
        
        params.append(transaction_id)
        query = f"UPDATE transactions SET {', '.join(updates)} WHERE id = ?"
        
        cursor.execute(query, params)
        conn.commit()
        
        return f"✓ Updated transaction {transaction_id}"

@mcp.tool()
def delete_transaction(transaction_id: str) -> str:
    """
    Delete a transaction by ID (for duplicates, errors, or corrections).
    """
    with DB.get_connection() as conn:
        cursor = conn.cursor()
        
        # Get transaction details before deleting
        cursor.execute("SELECT description, amount FROM transactions WHERE id = ?", (transaction_id,))
        row = cursor.fetchone()
        
        if not row:
            return f"Error: Transaction ID '{transaction_id}' not found."
        
        description = row['description']
        amount = row['amount'] / 100.0
        
        cursor.execute("DELETE FROM transactions WHERE id = ?", (transaction_id,))
        conn.commit()
        
        return f"✓ Deleted transaction: {description} (₹{amount:.2f})"

@mcp.tool()
def set_budget(category: str, monthly_limit: float) -> str:
    """
    Set a monthly budget limit for a category (in rupees).
    Use positive values - they'll be auto-converted to negative for expense tracking.
    """
    # Auto-convert positive to negative for expense budgets
    # Most categories are expenses, so positive input is more intuitive
    if monthly_limit > 0:
        monthly_limit = -monthly_limit
        converted = True
    else:
        converted = False
    
    with DB.get_connection() as conn:
        cursor = conn.cursor()
        
        # Get existing budget targets
        cursor.execute("SELECT value FROM config WHERE key='budget_targets_json'")
        row = cursor.fetchone()
        
        if row and row['value']:
            try:
                targets = json.loads(row['value'])
            except:
                targets = {}
        else:
            targets = {}
        
        # Update target
        targets[category] = monthly_limit
        
        # Save back
        cursor.execute("""
            INSERT OR REPLACE INTO config (key, value) 
            VALUES ('budget_targets_json', ?)
        """, (json.dumps(targets),))
        conn.commit()
        
        if converted:
            return f"✓ Set budget for '{category}': ₹{abs(monthly_limit):,.2f}/month (auto-converted to negative for expense tracking)"
        else:
            return f"✓ Set budget for '{category}': ₹{abs(monthly_limit):,.2f}/month"

@mcp.tool()
def list_rules() -> List[Dict]:
    """
    List all categorization rules with their patterns, categories, and priorities.
    Higher priority rules are applied first.
    """
    with DB.get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT pattern, category, priority FROM rules ORDER BY priority DESC")
        rows = cursor.fetchall()
    
    return [
        {
            "pattern": row['pattern'],
            "category": row['category'],
            "priority": row['priority']
        }
        for row in rows
    ]

@mcp.tool()
def delete_rule(pattern: str) -> str:
    """
    Delete a categorization rule by its pattern.
    """
    with DB.get_connection() as conn:
        cursor = conn.cursor()
        
        # Check if rule exists
        cursor.execute("SELECT category FROM rules WHERE pattern = ?", (pattern,))
        row = cursor.fetchone()
        
        if not row:
            return f"Error: No rule found with pattern '{pattern}'."
        
        category = row['category']
        
        cursor.execute("DELETE FROM rules WHERE pattern = ?", (pattern,))
        conn.commit()
        
        return f"✓ Deleted rule: '{pattern}' → '{category}'"

@mcp.tool()
def find_duplicates(tolerance_days: int = 1, tolerance_amount: float = 1.0) -> List[Dict]:
    """
    Find potential duplicate transactions.
    
    tolerance_days: How many days apart to consider duplicates (default: 1)
    tolerance_amount: Amount difference tolerance in rupees (default: 1.0)
    
    Returns: List of duplicate pairs with amount_diff and days_apart metadata
    """
    from datetime import datetime
    
    with DB.get_connection() as conn:
        cursor = conn.cursor()
        
        # More lenient duplicate detection - match on description OR merchant
        cursor.execute("""
            SELECT t1.id as id1, t1.date as date1, t1.description as desc1, t1.amount as amt1, t1.merchant as merch1,
                   t2.id as id2, t2.date as date2, t2.description as desc2, t2.amount as amt2, t2.merchant as merch2
            FROM transactions t1
            JOIN transactions t2 ON t1.id < t2.id
            WHERE ABS(JULIANDAY(t1.date) - JULIANDAY(t2.date)) <= ?
              AND ABS(t1.amount - t2.amount) <= ?
              AND (
                  t1.description = t2.description
                  OR (t1.merchant IS NOT NULL AND t2.merchant IS NOT NULL 
                      AND UPPER(t1.merchant) = UPPER(t2.merchant))
              )
            ORDER BY t1.date DESC
            LIMIT 50
        """, (tolerance_days, int(tolerance_amount * 100)))
        rows = cursor.fetchall()
    
    if not rows:
        return []
    
    duplicates = []
    for row in rows:
        duplicates.append({
            "transaction_1": {
                "id": row['id1'],
                "date": row['date1'],
                "description": row['desc1'],
                "merchant": row['merch1'],
                "amount": row['amt1'] / 100.0
            },
            "transaction_2": {
                "id": row['id2'],
                "date": row['date2'],
                "description": row['desc2'],
                "merchant": row['merch2'],
                "amount": row['amt2'] / 100.0
            },
            "amount_diff": abs(row['amt1'] - row['amt2']) / 100.0,
            "days_apart": abs((datetime.strptime(row['date1'], "%Y-%m-%d") - 
                             datetime.strptime(row['date2'], "%Y-%m-%d")).days)
        })
    
    return duplicates

@mcp.tool()
def categorize_batch(transaction_ids: List[str], category: str, create_rule: bool = False) -> str:
    """
    Categorize multiple transactions at once (bulk operation).
    
    transaction_ids: List of transaction IDs to categorize
    category: Category to assign to all transactions
    create_rule: If True, creates a rule from the first transaction's merchant pattern
    """
    if not transaction_ids:
        return "Error: No transaction IDs provided."
    
    with DB.get_connection() as conn:
        cursor = conn.cursor()
        
        updated_count = 0
        first_merchant = None
        
        for txn_id in transaction_ids:
            # Get transaction details
            cursor.execute("SELECT merchant, description FROM transactions WHERE id = ?", (txn_id,))
            row = cursor.fetchone()
            
            if not row:
                continue
            
            if first_merchant is None:
                first_merchant = row['merchant'] or row['description']
            
            # Update category
            cursor.execute("UPDATE transactions SET category = ? WHERE id = ?", (category, txn_id))
            updated_count += 1
        
        conn.commit()
        
        # Optionally create rule from first transaction
        if create_rule and first_merchant:
            # Extract merchant pattern (remove UPI- prefix and transaction ID)
            pattern = first_merchant.upper()
            if pattern.startswith("UPI-"):
                pattern = pattern[4:].split("-")[0]  # Get merchant name
            
            cursor.execute("INSERT OR IGNORE INTO rules (pattern, category, priority) VALUES (?, ?, ?)",
                         (pattern, category, 20))
            conn.commit()
            
            return f"✓ Categorized {updated_count} transactions as '{category}' and created rule: '{pattern}' → '{category}'"
        
        return f"✓ Categorized {updated_count} transactions as '{category}'"

@mcp.tool()
def get_category_trend(category: str, months: int = 6) -> List[Dict]:
    """
    Get monthly spending trend for a category.
    Shows how spending changes over time.
    
    category: Category to analyze
    months: Number of months to look back (default: 6)
    
    Returns: List of {month: "2026-01", amount: -12500, count: 45}
    """
    from datetime import datetime, timedelta
    
    with DB.get_connection() as conn:
        cursor = conn.cursor()
        
        # Get the most recent transaction date for this category
        cursor.execute("""
            SELECT MAX(date) FROM transactions WHERE category = ?
        """, (category,))
        max_date_row = cursor.fetchone()
        
        if not max_date_row or not max_date_row[0]:
            return []
        
        # Use the most recent transaction date as the end date
        # This ensures we capture data even if it's historical
        end_date = datetime.strptime(max_date_row[0], "%Y-%m-%d")
        start_date = end_date - timedelta(days=months * 31)
        
        # Format dates as strings for SQLite
        start_str = start_date.strftime("%Y-%m-%d")
        end_str = end_date.strftime("%Y-%m-%d")
        
        cursor.execute("""
            SELECT strftime('%Y-%m', date) as month, 
                   SUM(amount) as total,
                   COUNT(*) as count
            FROM transactions
            WHERE category = ?
              AND date >= ?
              AND date <= ?
            GROUP BY month
            ORDER BY month ASC
        """, (category, start_str, end_str))
        
        rows = cursor.fetchall()
    
    if not rows:
        return []
    
    return [
        {
            "month": row['month'],
            "amount": row['total'] / 100.0,
            "count": row['count'],
            "average": (row['total'] / 100.0) / row['count'] if row['count'] > 0 else 0
        }
        for row in rows
    ]

@mcp.tool()
def generate_monthly_report(month: int, year: int) -> str:
    """
    Generate a professional PDF financial report for a specific month.
    Includes charts for spending by category, top merchants, and summary.
    Returns the file path of the generated PDF.
    """
    try:
        from ledger_mcp.core.report_generator import ReportGenerator
        
        generator = ReportGenerator()
        pdf_path = generator.generate_pdf(month, year)
        
        return f"✓ Report generated successfully: {pdf_path}\nYou can open this file to view charts and detailed analysis."
        
    except ImportError:
        return "Error: Required libraries (reportlab, matplotlib) are missing. Please install them to use this feature."
    except Exception as e:
        return f"Error generating report: {str(e)}"

@mcp.tool()
def get_merchant_summary(limit: int = 10, start_date: str = None, end_date: str = None) -> List[Dict]:
    """
    Get top spending merchants across all categories.
    
    limit: Number of top merchants to return (default: 10)
    start_date: Optional start date (YYYY-MM-DD)
    end_date: Optional end date (YYYY-MM-DD)
    
    Returns: List of {merchant, total, count, average, category}
    """
    with DB.get_connection() as conn:
        cursor = conn.cursor()
        
        query = """
            SELECT merchant,
                   category,
                   SUM(amount) as total,
                   COUNT(*) as count,
                   AVG(amount) as average
            FROM transactions
            WHERE merchant IS NOT NULL
              AND merchant != ''
        """
        params = []
        
        if start_date:
            query += " AND date >= ?"
            params.append(start_date)
        
        if end_date:
            query += " AND date <= ?"
            params.append(end_date)
        
        query += """
            GROUP BY merchant, category
            ORDER BY ABS(total) DESC
            LIMIT ?
        """
        params.append(limit)
        
        cursor.execute(query, params)
        rows = cursor.fetchall()
    
    return [
        {
            "merchant": row['merchant'],
            "category": row['category'],
            "total": row['total'] / 100.0,
            "count": row['count'],
            "average": row['average'] / 100.0
        }
        for row in rows
    ]

@mcp.tool()
def smart_categorize_uncategorized(max_transactions: int = 10, auto_create_rules: bool = True) -> str:
    """
    Use AI to intelligently categorize uncategorized transactions.
    This is a hybrid approach: hardcoded patterns handle 85%, AI handles the remaining 15%.
    
    WARNING: This sends transaction descriptions to the AI for analysis.
    Only use if you're comfortable with that privacy tradeoff.
    
    max_transactions: How many uncategorized transactions to process (default: 10)
    auto_create_rules: If True, creates rules for AI-suggested categories (default: True)
    
    Returns: Summary of categorizations made
    """
    with DB.get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("""
            SELECT id, description, merchant, amount 
            FROM transactions 
            WHERE category = 'Uncategorized' 
            LIMIT ?
        """, (max_transactions,))
        uncategorized = cursor.fetchall()
    
    if not uncategorized:
        return "No uncategorized transactions found!"
    
    # Build a summary for AI to analyze
    summary = "Please categorize these transactions. Respond with ONLY a JSON array of {id, category}.\n\n"
    summary += "Common categories: Food, Transport, Shopping, Entertainment, Utilities, Healthcare, Education, Fitness, Income\n\n"
    summary += "Transactions:\n"
    
    for txn in uncategorized:
        amount_rupees = txn['amount'] / 100.0
        summary += f"- ID: {txn['id']}, Description: {txn['description']}, Amount: ₹{amount_rupees:.2f}\n"
    
    # Return instructions for user to paste into Claude
    return f"""
AI Categorization Ready!

{len(uncategorized)} uncategorized transactions found.

To use AI categorization:
1. Copy the text below
2. Paste it into this conversation
3. I'll analyze and categorize them for you

--- COPY BELOW ---
{summary}
--- END ---

Note: This is a privacy-conscious approach - YOU control when to share data with AI.
"""

@mcp.tool()
def get_financial_health(month: int, year: int) -> str:
    """
    Get a financial health dashboard: Income, Burn (True Expenses), and Savings Rate.
    Crucially, this separates 'Transfers' (money moved to savings/investments) from 'Burn'.
    
    Formula:
    - Income: Sum of all positive inflows
    - Burn: Total Outflows - Transfers/Investments
    - Savings: Income - Burn
    - Savings Rate: (Savings / Income) * 100
    """
    start_date = f"{year}-{month:02d}-01"
    if month == 12:
        end_date = f"{year+1}-01-01"
    else:
        end_date = f"{year}-{month+1:02d}-01"

    currency = _get_base_currency()
    
    with DB.get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("""
            SELECT category, amount 
            FROM transactions 
            WHERE date >= ? AND date < ?
        """, (start_date, end_date))
        rows = cursor.fetchall()
        
    income = 0.0
    total_outflow = 0.0
    transfers = 0.0
    
    savings_categories = {'Transfer', 'Investment', 'Savings', 'Save'}
    
    for row in rows:
        amount = row['amount'] / 100.0
        cat = row['category']
        
        if amount > 0:
            income += amount
        else:
            abs_amount = abs(amount)
            total_outflow += abs_amount
            if cat in savings_categories:
                transfers += abs_amount
                
    burn = total_outflow - transfers
    savings = income - burn
    
    if income > 0:
        rate = (savings / income) * 100
    else:
        rate = 0.0
        
    return f"""
Financial Health for {year}-{month:02d} ({currency}):

💰 Income:    {income:,.2f}
🔥 Burn:      {burn:,.2f} (True Spending)
🏦 Saved:     {savings:,.2f} (Unspent + Transfers)
📈 Rate:      {rate:.1f}%

Details:
- Total Outflows: {total_outflow:,.2f}
- Transfers/Investments: {transfers:,.2f} (Excluded from Burn)
"""

def start_mcp():
    """Entry point for CLI to start MCP."""
    mcp.run()
