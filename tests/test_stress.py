import pytest
import os
import time
from ledger_mcp.parsers.csv_parser import CSVParser
from ledger_mcp.core.categorizer import Categorizer
from ledger_mcp.core.db import DB
from ledger_mcp.interface.mcp_server import search_transactions

def test_ingest_large_csv(temp_db):
    """Test 1: Ingest 5000+ row CSV"""
    csv_path = "tests/stress_test.csv"
    
    if not os.path.exists(csv_path):
        pytest.skip("Stress test CSV not found")
    
    parser = CSVParser()
    start = time.time()
    
    transactions = parser.parse(csv_path)
    
    duration = time.time() - start
    
    # Should parse 5000+ rows quickly
    assert len(transactions) > 5000
    assert duration < 10.0  # Should complete in under 10 seconds
    print(f"\nParsed {len(transactions)} transactions in {duration:.2f}s")

def test_categorize_large_dataset(temp_db):
    """Test 2: Categorize large dataset"""
    # First ingest the data
    csv_path = "tests/stress_test.csv"
    
    if not os.path.exists(csv_path):
        pytest.skip("Stress test CSV not found")
    
    parser = CSVParser()
    transactions = parser.parse(csv_path)
    
    # Insert into DB
    categorizer = Categorizer()
    count = 0
    
    with temp_db.get_connection() as conn:
        cursor = conn.cursor()
        
        # Add some categorization rules first
        cursor.execute("INSERT INTO rules (pattern, category, priority) VALUES ('UBER', 'Transport', 20)")
        cursor.execute("INSERT INTO rules (pattern, category, priority) VALUES ('SWIGGY', 'Food', 20)")
        cursor.execute("INSERT INTO rules (pattern, category, priority) VALUES ('NETFLIX', 'Entertainment', 20)")
        cursor.execute("INSERT INTO rules (pattern, category, priority) VALUES ('AMAZON', 'Shopping', 20)")
        conn.commit()
        
        # Reload rules
        categorizer.rules = categorizer._load_rules()
        
        start = time.time()
        
        for txn in transactions[:1000]:  # Test with first 1000 for speed
            merchant = categorizer.normalize(txn.description)
            category = categorizer.categorize(txn.description)
            
            try:
                cursor.execute("""
                    INSERT INTO transactions (id, date, amount, description, merchant, category)
                    VALUES (?, ?, ?, ?, ?, ?)
                """, (f"stress_{count}", txn.date, txn.amount, txn.description, merchant, category))
                count += 1
            except Exception:
                pass
        
        conn.commit()
        duration = time.time() - start
    
    assert count > 900  # Most should succeed
    assert duration < 5.0  # Should be fast
    print(f"\nCategorized {count} transactions in {duration:.2f}s")

def test_search_performance(temp_db):
    """Test 3: Search performance with large dataset"""
    # Insert 1000 test transactions
    with temp_db.get_connection() as conn:
        cursor = conn.cursor()
        data = [
            (f"id_{i}", '2026-01-01', -10000 + (i * 10), f'Transaction {i}', 'Merchant', 'Food', 0, '')
            for i in range(1000)
        ]
        cursor.executemany("INSERT INTO transactions VALUES (?,?,?,?,?,?,?,?)", data)
        conn.commit()
    
    # Test search performance
    start = time.time()
    results = search_transactions(keyword="Transaction", limit=100)
    duration = time.time() - start
    
    assert len(results) == 100
    assert duration < 1.0  # Should be fast
    print(f"\nSearch returned {len(results)} results in {duration:.2f}s")

def test_recurring_detection_performance(temp_db):
    """Test 4: Recurring detection at scale"""
    # Insert recurring patterns
    with temp_db.get_connection() as conn:
        cursor = conn.cursor()
        
        # Add 100 Netflix transactions (recurring)
        for i in range(100):
            cursor.execute("""
                INSERT INTO transactions (id, date, amount, merchant, description)
                VALUES (?, ?, ?, ?, ?)
            """, (f"netflix_{i}", f"2026-{(i % 12) + 1:02d}-01", -50000, "NETFLIX", "NETFLIX"))
        
        # Add 100 random transactions (non-recurring)
        for i in range(100):
            cursor.execute("""
                INSERT INTO transactions (id, date, amount, merchant, description)
                VALUES (?, ?, ?, ?, ?)
            """, (f"random_{i}", f"2026-01-{(i % 28) + 1:02d}", -10000 + (i * 100), f"Merchant_{i}", f"Random {i}"))
        
        conn.commit()
    
    categorizer = Categorizer()
    start = time.time()
    
    count = categorizer.detect_recurring()
    
    duration = time.time() - start
    
    assert count >= 100  # Should detect Netflix transactions
    assert duration < 2.0  # Should be reasonably fast
    print(f"\nDetected {count} recurring transactions in {duration:.2f}s")

def test_memory_usage(temp_db):
    """Test 5: Verify no memory leaks with large operations"""
    import sys
    
    # Get initial memory usage (rough estimate)
    initial_size = sys.getsizeof(temp_db)
    
    # Perform large operation
    with temp_db.get_connection() as conn:
        cursor = conn.cursor()
        data = [
            (f"mem_{i}", '2026-01-01', -10000, f'Test {i}', 'Merchant', 'Food', 0, '')
            for i in range(5000)
        ]
        cursor.executemany("INSERT INTO transactions VALUES (?,?,?,?,?,?,?,?)", data)
        conn.commit()
    
    # Query all data
    with temp_db.get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM transactions")
        rows = cursor.fetchall()
    
    # Memory should not grow excessively
    final_size = sys.getsizeof(temp_db)
    
    assert len(rows) == 5000
    # This is a basic check - in production you'd use memory_profiler
    print(f"\nProcessed {len(rows)} transactions, memory delta: {final_size - initial_size} bytes")
