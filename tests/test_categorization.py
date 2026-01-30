import pytest
from ledger_mcp.core.categorizer import Categorizer
from ledger_mcp.core.db import DB
import sqlite3

def test_priority_wars(temp_db):
    """Test 1: Priority Wars"""
    cat = Categorizer()
    
    # Add contending rules
    with temp_db.get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("INSERT INTO rules (pattern, category, priority) VALUES (?, ?, ?)", ("UBER", "Transport", 10))
        cursor.execute("INSERT INTO rules (pattern, category, priority) VALUES (?, ?, ?)", ("UBER EATS", "Food", 20))
        conn.commit()
    
    # Refresh rules
    cat.rules = cat._load_rules()
    
    # "UBER EATS" matches both "UBER" (partial) and "UBER EATS".
    # Since "UBER EATS" has higher priority (20), it should win.
    # IMPORTANT: The current implementation iterates rules list.
    # The SQL query sorts by priority DESC. 
    # So "UBER EATS" comes first in the list.
    # The first match returns.
    
    assert cat.categorize("UBER EATS") == "Food"
    assert cat.categorize("UBER RIDE") == "Transport"

def test_bad_regex(temp_db):
    """Test 2: Regex Safety"""
    cat = Categorizer()
    
    with temp_db.get_connection() as conn:
        cursor = conn.cursor()
        # Invalid regex: Unbalanced bracket
        cursor.execute("INSERT INTO rules (pattern, category) VALUES (?, ?)", ("[A-Z", "Broken"))
        conn.commit()
        
    cat.rules = cat._load_rules()
    
    # Should not crash, just skip the bad rule
    result = cat.categorize("Some Transaction")
    assert result == "Uncategorized"

def test_recurring_detection(temp_db):
    """Test 3: Recurring Detection"""
    with temp_db.get_connection() as conn:
        cursor = conn.cursor()
        # Seed 3 identical transactions
        cursor.execute("INSERT INTO transactions (id, date, amount, merchant, description) VALUES ('1', '2026-01-01', -50000, 'NETFLIX', 'NETFLIX')")
        cursor.execute("INSERT INTO transactions (id, date, amount, merchant, description) VALUES ('2', '2026-02-01', -50000, 'NETFLIX', 'NETFLIX')")
        cursor.execute("INSERT INTO transactions (id, date, amount, merchant, description) VALUES ('3', '2026-03-01', -50000, 'NETFLIX', 'NETFLIX')")
        conn.commit()
        
    cat = Categorizer()
    count = cat.detect_recurring()
    
    assert count == 3
    
    # Verify DB update
    with temp_db.get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT is_recurring FROM transactions WHERE merchant='NETFLIX'")
        rows = cursor.fetchall()
        assert all(row[0] == 1 for row in rows)
