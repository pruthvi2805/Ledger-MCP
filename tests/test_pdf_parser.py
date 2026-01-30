import pytest
from ledger_mcp.parsers.pdf_parser import PDFParser

def test_detect_bank_hdfc():
    """Test 1: HDFC bank detection"""
    parser = PDFParser()
    text = "HDFC BANK LIMITED\nAccount Statement"
    
    bank = parser._detect_bank(text)
    assert bank == "HDFC"

def test_detect_bank_icici():
    """Test 2: ICICI bank detection"""
    parser = PDFParser()
    text = "ICICI BANK\nStatement of Account"
    
    bank = parser._detect_bank(text)
    assert bank == "ICICI"

def test_detect_bank_sbi():
    """Test 3: SBI bank detection"""
    parser = PDFParser()
    text = "STATE BANK OF INDIA\nAccount Statement"
    
    bank = parser._detect_bank(text)
    assert bank == "SBI"

def test_detect_bank_unknown():
    """Test 4: Unknown bank format"""
    parser = PDFParser()
    text = "Some Random Bank\nStatement"
    
    bank = parser._detect_bank(text)
    assert bank == "UNKNOWN"

def test_parse_date_formats():
    """Test 5: Date parsing with various formats"""
    parser = PDFParser()
    
    # DD/MM/YYYY
    assert parser._parse_date("15/01/2026") == "2026-01-15"
    
    # DD-MM-YYYY
    assert parser._parse_date("15-01-2026") == "2026-01-15"
    
    # DD Mon YYYY
    assert parser._parse_date("15 Jan 2026") == "2026-01-15"
    
    # Invalid date
    assert parser._parse_date("invalid") is None
    assert parser._parse_date("") is None
    assert parser._parse_date(None) is None

def test_parse_amount():
    """Test 6: Amount parsing with commas and decimals"""
    parser = PDFParser()
    
    # Standard amount
    assert parser._parse_amount("1000.50") == 1000.50
    
    # With commas
    assert parser._parse_amount("1,000.50") == 1000.50
    assert parser._parse_amount("10,00,000.00") == 1000000.0
    
    # With spaces
    assert parser._parse_amount(" 500.25 ") == 500.25
    
    # Empty or invalid
    assert parser._parse_amount("") == 0.0
    assert parser._parse_amount(None) == 0.0
    assert parser._parse_amount("invalid") == 0.0
