import sqlite3
import os
import stat
import platform
from pathlib import Path
from contextlib import contextmanager
from typing import Generator

class Database:
    def __init__(self, db_path: str = None):
        if db_path is None:
            # Resolve absolute path: ../../ledger.db from this file
            base_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
            self.db_path = os.path.join(base_dir, "ledger.db")
        else:
            self.db_path = db_path

    def init_db(self):
        """Initialize the database with schema and secure permissions."""
        
        # 1. Create file and set permissions immediately
        if not os.path.exists(self.db_path):
            Path(self.db_path).touch()
            # Enforce 600 (User Read/Write ONLY) - Unix/Linux/Mac only
            if platform.system() != "Windows":
                os.chmod(self.db_path, 0o600)
            # On Windows, file permissions work differently (ACLs)
            # The default permissions are already restrictive to the user
        
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        # 2. Create Tables
        # Transactions Table
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS transactions (
            id TEXT PRIMARY KEY,
            date TEXT NOT NULL,
            amount INTEGER NOT NULL,
            description TEXT NOT NULL,
            merchant TEXT,
            category TEXT DEFAULT 'Uncategorized',
            is_recurring BOOLEAN DEFAULT 0,
            source_file TEXT,
            currency TEXT DEFAULT 'INR',
            amount_normalized REAL
        )
        """)

        # Schema Migration: Add columns if they don't exist (for v1 users)
        cursor.execute("PRAGMA table_info(transactions)")
        columns = [info[1] for info in cursor.fetchall()]
        
        if 'currency' not in columns:
            cursor.execute("ALTER TABLE transactions ADD COLUMN currency TEXT DEFAULT 'INR'")
            print("Migrated DB: Added 'currency' column")
            
        if 'amount_normalized' not in columns:
            cursor.execute("ALTER TABLE transactions ADD COLUMN amount_normalized REAL")
            # Populate normalized amount (assuming INR for past txns)
            cursor.execute("UPDATE transactions SET amount_normalized = amount / 100.0 WHERE amount_normalized IS NULL")
            print("Migrated DB: Added 'amount_normalized' column")

        # Indexes for speed
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_category ON transactions (category)")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_date ON transactions (date)")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_merchant ON transactions (merchant)")

        # Config Table (Key-Value)
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS config (
            key TEXT PRIMARY KEY,
            value BLOB
        )
        """)

        # Rules Table
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS rules (
            pattern TEXT NOT NULL,
            category TEXT NOT NULL,
            priority INTEGER DEFAULT 10
        )
        """)

        conn.commit()
        conn.close()

    @contextmanager
    def get_connection(self) -> Generator[sqlite3.Connection, None, None]:
        """Yields a database connection."""
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        try:
            yield conn
        finally:
            conn.close()

# Global instance
DB = Database()
