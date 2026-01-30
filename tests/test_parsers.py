import pytest
from ledger_mcp.parsers.csv_parser import CSVParser

def test_credit_debit_logic():
    """Test 3: Negative/Credit Logic"""
    # Debit = Outflow (Negative), Credit = Inflow (Positive)
    # Our CSV parser logic: 
    # If debit column has value > 0 -> amount = -value
    # If credit column has value > 0 -> amount = +value
    
    content = "Date,Desc,Debit,Credit\n2026-01-01,Out,500,\n2026-01-02,In,,500"
    with open("tests/temp_crdr.csv", "w") as f:
        f.write(content)
        
    parser = CSVParser()
    txns = parser.parse("tests/temp_crdr.csv")
    
    assert len(txns) == 2
    
    # Sort by date to be sure
    txns.sort(key=lambda x: x.date)
    
    # Debit 500 -> Stored as -50000 (paise)
    assert txns[0].amount == -50000
    
    # Credit 500 -> Stored as 50000 (paise)
    assert txns[1].amount == 50000

# PDF Parsing is harder to mock without actual PDF files, 
# and creating them on the fly requires reportlab or similar. 
# We'll skip complex PDF generation for this automated suite 
# unless we add 'reportlab' to dev dependencies.
