import pytest
import os
import tempfile
from ledger_mcp.core.db import DB
from ledger_mcp.core.security import Security

@pytest.fixture
def temp_db():
    """Create a temporary database for testing."""
    # Create a temp file
    fd, path = tempfile.mkstemp(suffix='.db')
    os.close(fd)
    
    # Initialize DB (creates tables)
    original_path = DB.db_path
    DB.db_path = path
    DB.init_db()
    
    yield DB
    
    # Teardown
    DB.db_path = original_path
    if os.path.exists(path):
        os.remove(path)

@pytest.fixture
def mock_config(temp_db):
    """Seed the DB with config data."""
    salt = Security.generate_salt()
    with temp_db.get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("INSERT INTO config (key, value) VALUES (?, ?)", ('salt', salt))
        conn.commit()
    return temp_db
