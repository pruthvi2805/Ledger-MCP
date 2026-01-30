import re
from typing import List, Tuple
from .db import DB

class Categorizer:
    from .global_merchants import GLOBAL_MERCHANTS
    
    DEFAULT_MERCHANTS = GLOBAL_MERCHANTS

    def __init__(self):
        self.rules = self._load_rules()

    def _load_rules(self) -> List[Tuple[str, str]]:
        with DB.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT pattern, category FROM rules ORDER BY priority DESC")
            return cursor.fetchall()

    def normalize(self, text: str) -> str:
        """Uppercase, clean prefixes, collapse whitespace."""
        if not text: return ""
        text = text.upper()
        # Remove common bank prefixes
        text = re.sub(r'^(UPI-|POS-|NEFT-|IMPS-|ACH-)', '', text)
        text = re.sub(r'\s+', ' ', text).strip()
        return text

    def categorize(self, description: str) -> str:
        """Determine category based on Rules > Defaults > Fallback."""
        norm_desc = self.normalize(description)
        
        # 1. User Rules (Cached)
        for row in self.rules:
            # row is tuple-like or sqlite3.Row
            pattern = row['pattern'] if isinstance(row,  (dict, object)) and hasattr(row, '__getitem__') and not isinstance(row, tuple) else row[0]
            category = row['category'] if isinstance(row, (dict, object)) and hasattr(row, '__getitem__') and not isinstance(row, tuple) else row[1]
            
            try:
                if re.search(pattern, norm_desc, re.IGNORECASE):
                    return category
            except re.error:
                continue

        # 2. Defaults
        for merchant, cat in self.DEFAULT_MERCHANTS.items():
            # Use word boundary to avoid partial matches (e.g., ACT in TRANSACT)
            if re.search(fr'\b{re.escape(merchant)}\b', norm_desc):
                return cat
                
        # 3. Fallback
        return "Uncategorized"

    def recategorize_all(self) -> int:
        """Re-run rules on all transactions."""
        # Refresh rules in case they changed
        self.rules = self._load_rules()
        
        count = 0
        with DB.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT id, description FROM transactions")
            rows = cursor.fetchall()
            
            for row in rows:
                new_cat = self.categorize(row['description'])
                # Only update if it's not Uncategorized? 
                # Or better: Update everything to ensure rules stick. 
                # If a rule was removed, it might default back to Uncategorized.
                # However, preserving manual edits is hard without a 'manual_override' flag.
                # For this v1, "recategorize" implies re-applying logic strictly.
                
                if new_cat != "Uncategorized":
                    # Check if actually changed to avoid DB churn
                    # (Requires fetching current cat, simplified here to just update)
                    cursor.execute("UPDATE transactions SET category = ? WHERE id = ?", (new_cat, row['id']))
                    count += 1
            conn.commit()
        return count

    def detect_recurring(self):
        """
        Identify recurring transactions.
        Logic: Same Merchant + Same Amount > 2 times.
        """
        with DB.get_connection() as conn:
            cursor = conn.cursor()
            # Find candidate groups
            cursor.execute("""
                SELECT merchant, amount, COUNT(*) as cnt
                FROM transactions
                WHERE merchant IS NOT NULL AND merchant != ''
                GROUP BY merchant, amount
                HAVING cnt > 2
            """)
            candidates = cursor.fetchall()
            
            updated_count = 0
            for row in candidates:
                merchant = row['merchant']
                amount = row['amount']
                
                # Fetch dates to verify
                cursor.execute("""
                    SELECT date FROM transactions 
                    WHERE merchant = ? AND amount = ? 
                    ORDER BY date
                """, (merchant, amount))
                
                cursor.execute("""
                    UPDATE transactions 
                    SET is_recurring = 1 
                    WHERE merchant = ? AND amount = ?
                """, (merchant, amount))
                updated_count += cursor.rowcount
            
            conn.commit()
            return updated_count
