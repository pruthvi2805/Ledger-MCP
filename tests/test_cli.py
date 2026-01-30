import pytest
import os
import tempfile
from typer.testing import CliRunner
from ledger_mcp.cli import app
from ledger_mcp.core.db import DB

runner = CliRunner()

@pytest.fixture
def temp_db_path():
    """Create a temporary database path for CLI tests."""
    fd, path = tempfile.mkstemp(suffix='.db')
    os.close(fd)
    
    # Override DB path
    original_path = DB.db_path
    DB.db_path = path
    
    yield path
    
    # Cleanup
    DB.db_path = original_path
    if os.path.exists(path):
        os.remove(path)

def test_init_command(temp_db_path):
    """Test 1: Database initialization."""
    result = runner.invoke(app, ["init"])
    
    assert result.exit_code == 0
    assert "Initializing Ledger MCP" in result.stdout
    assert "Setup complete" in result.stdout
    assert os.path.exists(temp_db_path)

def test_init_already_initialized(temp_db_path):
    """Test 2: Init is idempotent."""
    # First init
    runner.invoke(app, ["init"])
    
    # Second init
    result = runner.invoke(app, ["init"])
    
    assert result.exit_code == 0
    assert "already initialized" in result.stdout

def test_ingest_csv(temp_db_path):
    """Test 3: CSV ingestion."""
    # Initialize first
    runner.invoke(app, ["init"])
    
    # Create a test CSV
    csv_content = "Date,Description,Debit,Credit\n2026-01-01,Test Transaction,100,\n"
    csv_path = "tests/temp_cli_test.csv"
    with open(csv_path, "w") as f:
        f.write(csv_content)
    
    try:
        result = runner.invoke(app, ["ingest", csv_path])
        
        assert result.exit_code == 0
        assert "Ingesting" in result.stdout
        assert "Successfully ingested" in result.stdout
    finally:
        if os.path.exists(csv_path):
            os.remove(csv_path)

def test_ingest_nonexistent_file(temp_db_path):
    """Test 4: Error handling for missing file."""
    runner.invoke(app, ["init"])
    
    result = runner.invoke(app, ["ingest", "nonexistent.csv"])
    
    assert result.exit_code == 1
    assert "Error: File not found" in result.stdout

def test_recategorize_command(temp_db_path):
    """Test 5: Recategorization command."""
    runner.invoke(app, ["init"])
    
    # Add some test data first
    csv_content = "Date,Description,Debit,Credit\n2026-01-01,UBER,100,\n"
    csv_path = "tests/temp_recat_test.csv"
    with open(csv_path, "w") as f:
        f.write(csv_content)
    
    try:
        runner.invoke(app, ["ingest", csv_path])
        result = runner.invoke(app, ["recategorize"])
        
        assert result.exit_code == 0
        assert "Updated" in result.stdout
    finally:
        if os.path.exists(csv_path):
            os.remove(csv_path)

def test_detect_recurring_command(temp_db_path):
    """Test 6: Recurring detection command."""
    runner.invoke(app, ["init"])
    
    result = runner.invoke(app, ["detect-recurring"])
    
    assert result.exit_code == 0
    assert "Flagged" in result.stdout
