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
        """
        Normalize merchant names for consistent grouping.
        Strips payment prefixes, terminal IDs, transaction numbers, dates, and other noise.
        """
        if not text: return ""
        text = text.upper()
        
        # 1. Remove common bank/payment prefixes (India, EU, US)
        # e.g. "BEA, Apple Pay ...", "SEPA Incasso ...", "eCom, Apple Pay ..."
        text = re.sub(r'^(UPI-|POS-|NEFT-|IMPS-|ACH-|ATM-|EFT-|WIRE-)', '', text)
        text = re.sub(r'^(BEA,?\s*|SEPA\s+|ECOM,?\s*|IDEAL\s+|OVERBOEKING\s+)', '', text, flags=re.IGNORECASE)
        text = re.sub(r'^(APPLE PAY\s*|GOOGLE PAY\s*|SAMSUNG PAY\s*|ALIPAY\s*|PAYPAL\s*|VENMO\s*)+', '', text, flags=re.IGNORECASE)
        text = re.sub(r'^(BETAALPAS\s+|CREDITCARD\s+|DEBITCARD\s+|MASTERCARD\s*|VISA\s*)+', '', text, flags=re.IGNORECASE)
        
        # 2. Remove terminal/POS identifiers (EU/NL format)
        # e.g. ",PAS433 NR:CT938136" or "PAS433 NR:75400912"
        text = re.sub(r',?PAS\d+\s*NR:[A-Z0-9]+', '', text, flags=re.IGNORECASE)
        text = re.sub(r',?PAS\d+', '', text)
        
        # 3. Remove transaction IDs (alphanumeric codes)
        # e.g. "NR:MDGVCR92" or "/TRTP/SEPA..."
        text = re.sub(r'\bNR:[A-Z0-9]+', '', text, flags=re.IGNORECASE)
        text = re.sub(r'^/TRTP/[^/]+/', '', text)  # Remove /TRTP/xxxxx/ prefix
        text = re.sub(r'/IBAN/[A-Z0-9]+\s*', '', text)
        text = re.sub(r'/BIC/[A-Z0-9]+\s*', '', text)
        text = re.sub(r'/CSID/[A-Z0-9]+\s*', '', text)
        text = re.sub(r'/REMI/[A-Z0-9/ ]*', '', text)  # Remove remittance info (before NAME)
        text = re.sub(r'/NAME/([^/]+)/?', r'\1 ', text)  # Extract name content
        text = re.sub(r'KENMERK:\s*[A-Z0-9]+', '', text, flags=re.IGNORECASE)
        # Clean up any remaining slashes and IBAN/REMI prefixes
        text = re.sub(r'IBAN/', '', text)
        text = re.sub(r'REMI/', '', text)
        
        # 4. Remove embedded dates (various formats)
        # e.g. "03.06.25/12:14" or "24.08.25/16:10" or "2025-01-15"
        text = re.sub(r'\d{2}\.\d{2}\.\d{2}/\d{2}[:.]\d{2}', '', text)
        text = re.sub(r'\d{4}-\d{2}-\d{2}', '', text)
        text = re.sub(r'\d{2}/\d{2}/\d{4}', '', text)
        text = re.sub(r'\d{2}-\d{2}-\d{4}', '', text)
        
        # 5. Remove location suffixes that vary per transaction
        # e.g. trailing city names after comma
        text = re.sub(r',\s*(UTRECHT|AMSTERDAM|ROTTERDAM|NIEUWEGEIN|HOUTEN|NEDERLAND|NL)\s*$', '', text, flags=re.IGNORECASE)
        
        # 6. Remove common suffixes (refund markers, etc.)
        text = re.sub(r'\s*TERUGB(OEKING|ETALING)?\s*$', '', text, flags=re.IGNORECASE)
        text = re.sub(r'\s*REFUND\s*$', '', text, flags=re.IGNORECASE)
        
        # 7. Remove CCV* prefix (payment processor)
        text = re.sub(r'^CCV\*', '', text)
        
        # 8. Remove IBAN prefixes in description
        text = re.sub(r'IBAN:?\s*[A-Z]{2}\d{2}[A-Z0-9]+', '', text, flags=re.IGNORECASE)
        text = re.sub(r'/IBAN/[A-Z0-9]+', '', text)
        text = re.sub(r'/NAME/[^/]+/', '/', text)  # Keep structure but remove name
        text = re.sub(r'/REMI/[^/]+', '', text)  # Remove remittance info
        text = re.sub(r'BIC:?\s*[A-Z0-9]+', '', text, flags=re.IGNORECASE)
        text = re.sub(r'NAAM:\s*', '', text, flags=re.IGNORECASE)
        text = re.sub(r'OMSCHRIJVING:\s*', '', text, flags=re.IGNORECASE)
        
        # 9. Remove long alphanumeric codes (transaction IDs, reference numbers)
        # e.g. "T92TSMX55W9GL2X338" or "3FA371FE1E134CE8A435BA2C114442AB"
        text = re.sub(r'\b[A-Z0-9]{16,}\b', '', text)  # Very long codes
        text = re.sub(r'\b[A-Z]{1,3}\d{6,}\b', '', text)  # Letter prefix + many digits
        text = re.sub(r'\b\d{5,}\b', '', text)  # Pure digit sequences (5+ digits)
        text = re.sub(r'\b\d?[A-Z]{2,3}\s*\d{4,}\b', '', text)  # "5BK 71805" pattern
        text = re.sub(r'\b\d[A-Z]{2,3}\b', '', text)  # Remaining "5BK" codes
        text = re.sub(r'\b[A-Z]{4}\d{4}', '', text)  # "WERO0157" pattern
        text = re.sub(r'\bID DEBITEUR:?\s*\d*', '', text, flags=re.IGNORECASE)
        text = re.sub(r'\bEREF/\s*[A-Z0-9]+', '', text, flags=re.IGNORECASE)  # Bank reference
        text = re.sub(r'TOP-UP\s+-?\d{2}-\d{4}\s+\d{2}:\d{2}', '', text)  # Remove TOP-UP date suffix
        text = re.sub(r':\d{2}\s*$', '', text)  # Trailing ":45" time fragments
        text = re.sub(r'\b(JANUARI|FEBRUARI|MAART|APRIL|MEI|JUNI|JULI|AUGUSTUS|SEPTEMBER|OKTOBER|NOVEMBER|DECEMBER)\b', '', text, flags=re.IGNORECASE)  # Dutch months
        text = re.sub(r'\b(JANUARY|FEBRUARY|MARCH|APRIL|MAY|JUNE|JULY|AUGUST|SEPTEMBER|OCTOBER|NOVEMBER|DECEMBER)\b', '', text, flags=re.IGNORECASE)  # English months
        text = re.sub(r'\bINCASS?ANT:?\s*', '', text, flags=re.IGNORECASE)  # INCASSANT: label
        text = re.sub(r'\bDERDENGELDEN\b', '', text, flags=re.IGNORECASE)  # Dutch financial term
        text = re.sub(r'\bVIA\s+(ST\.|STICHTING)\s+', '', text, flags=re.IGNORECASE)  # "VIA ST. " prefix
        text = re.sub(r'\bDOORLOPEND\b', '', text, flags=re.IGNORECASE)  # "DOORLOPEND" (recurring)
        text = re.sub(r'\bALGEMEEN\b', '', text, flags=re.IGNORECASE)  # "ALGEMEEN" (general)
        text = re.sub(r'\bMACHTIGING:?\s*', '', text, flags=re.IGNORECASE)  # "MACHTIGING:" (authorization)
        text = re.sub(r'/O\s+VKNR\s*', '', text, flags=re.IGNORECASE)  # "/O VKNR" pattern
        text = re.sub(r'\bEMS\s*\.?\s*', '', text, flags=re.IGNORECASE)  # "EMS ." noise
        text = re.sub(r'\bNV\s+NV\b', 'NV', text, flags=re.IGNORECASE)  # Duplicate "NV NV"
        text = re.sub(r'TOP-UP\s+TOP-UP', 'TOP-UP', text, flags=re.IGNORECASE)  # Duplicate "TOP-UP TOP-UP"
        text = re.sub(r'/[A-Z]+\s+[A-Z]+\s+FUNDING\s*', '', text, flags=re.IGNORECASE)  # "/ALLIANZ EIGEN FUNDING" pattern
        text = re.sub(r'-\d{4}-\s*$', '', text)  # Trailing "-0112-" fragments
        text = re.sub(r'-\d{2}-\d{2}\s*$', '', text)  # Trailing "-08-20" date fragments
        text = re.sub(r'CSID//?', '', text, flags=re.IGNORECASE)  # "CSID//" prefix
        text = re.sub(r'/?\bN\s*AME/?\s*', '', text, flags=re.IGNORECASE)  # "N AME/" pattern
        text = re.sub(r'/MARF/\s*\d*', '', text, flags=re.IGNORECASE)  # "/MARF/ 18" pattern
        text = re.sub(r'/OVKNR\s*[A-Z0-9]+', '', text, flags=re.IGNORECASE)  # "/OVKNR 202510BNAN" pattern
        text = re.sub(r'\d{6}[A-Z]{4}\s*$', '', text)  # Trailing "202510BNAN" codes
        text = re.sub(r'/EREF/[A-Z0-9\-]+', '', text, flags=re.IGNORECASE)  # "/EREF/-0255" pattern
        text = re.sub(r'\b[A-Z]{3}\s+TW\s+PAYMENT\b', '', text, flags=re.IGNORECASE)  # "QHY TW PAYMENT" (WISE)
        text = re.sub(r'\bBETALING\s+AAN\s*', '', text, flags=re.IGNORECASE)  # "BETALING AAN" (payment to)
        text = re.sub(r'\bKENMERK\s+', '', text, flags=re.IGNORECASE)  # "KENMERK" (reference)
        text = re.sub(r'\bREL\.?NR\.?\s*', '', text, flags=re.IGNORECASE)  # "REL.NR." (relation number)
        text = re.sub(r'\bPERIODE\s*', '', text, flags=re.IGNORECASE)  # "PERIODE" (period)
        text = re.sub(r'\s+-\d{2}-\d{4}\s+\d{2}\s*$', '', text)  # Trailing "-10-2025 16" date fragments
        
        # 10. Remove Dutch bank transfer prefixes that appear after previous cleanup
        text = re.sub(r'^(OVERBOEKING|INCASSO|IDEAL)\s+', '', text, flags=re.IGNORECASE)
        
        # 11. Handle duplicate merchant names by truncating at first repeated word sequence
        # "ABN AMRO KREDIETEN NV ABN AMRO KREDIETEN NV" -> "ABN AMRO KREDIETEN NV"
        words = text.split()
        seen = set()
        result_words = []
        for i, word in enumerate(words):
            key = word.upper()
            if key in seen and i > 2:  # Allow first few words to repeat (e.g., "TOP-UP VIA BUNQ TOP-UP")
                break
            seen.add(key)
            result_words.append(word)
        text = ' '.join(result_words)
        
        # 12. Collapse whitespace and trim
        text = re.sub(r'\s+', ' ', text).strip()
        
        # 13. Remove trailing punctuation and slashes
        text = re.sub(r'[,;:/\-\s]+$', '', text)
        text = re.sub(r'^[,;:/\-\s]+', '', text)
        
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
