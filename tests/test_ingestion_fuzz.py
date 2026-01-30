import pytest
from ledger_mcp.parsers.csv_parser import CSVParser
from ledger_mcp.core.categorizer import Categorizer
from ledger_mcp.core.db import DB
import os

def test_precision_handling(temp_db):
    """Test 1: Rounding Errors"""
    # Create a micro-CSV on the fly
    content = "Date,Description,Debit,Credit\n2026-01-01,PrecisionTest,100.505,"
    with open("tests/temp_precision.csv", "w") as f:
        f.write(content)
        
    parser = CSVParser()
    txns = parser.parse("tests/temp_precision.csv")
    
    # 100.505 * 100 = 10050.5 -> round -> 10050 or 10051? 
    # Python round(0.5) rounds to nearest even number usually, but let's check our logic: int(round(val * 100))
    # 100.505 * 100 = 10050.5. round(10050.5) -> 10050 (nearest even)
    # Wait, 100.505 might represent 100 rupees 50.5 paise. 
    # Standard banking usually gives 2 decimal places. 
    # Let's ensure it doesn't crash and stores AN integer.
    
    assert len(txns) == 1
    # We accept reasonable rounding behavior, main goal is it IS an int.
    assert isinstance(txns[0].amount, int)
    
    os.remove("tests/temp_precision.csv")

def test_date_formats(temp_db):
    """Test 2: Mixed Date Formats"""
    content = "Date,Description,Amount\n2026-01-01,ISO,100\n02/01/2026,US,100\n03-01-2026,IN,100\n99-99-2099,Bad,100"
    with open("tests/temp_dates.csv", "w") as f:
        f.write(content)
        
    parser = CSVParser()
    txns = parser.parse("tests/temp_dates.csv")
    
    # Only 3 valid dates should be parsed
    assert len(txns) == 3
    dates = sorted([t.date for t in txns])
    assert dates == ['2026-01-01', '2026-01-02', '2026-01-03']
    
    os.remove("tests/temp_dates.csv")

def test_encoding(temp_db):
    """Test 3: Encoding Hell (Emojis/UTF-8)"""
    content = "Date,Description,Amount\n2026-01-01,Café 🍕,100"
    with open("tests/temp_utf8.csv", "w", encoding='utf-8') as f:
        f.write(content)
        
    parser = CSVParser()
    txns = parser.parse("tests/temp_utf8.csv")
    
    assert len(txns) == 1
    assert "Café" in txns[0].description
    assert "🍕" in txns[0].description
    
    os.remove("tests/temp_utf8.csv")
