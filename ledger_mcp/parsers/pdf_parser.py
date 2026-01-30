import pdfplumber
import re
from typing import List, Optional, Any
from datetime import datetime
from .base import BaseParser, TransactionData
# from pdfplumber.password import PDFPasswordError

class PDFParser(BaseParser):
    def parse(self, file_path: str, password: Optional[str] = None) -> List[TransactionData]:
        try:
            with pdfplumber.open(file_path, password=password) as pdf:
                # 1. Detect Bank
                first_page_text = pdf.pages[0].extract_text()
                bank = self._detect_bank(first_page_text)
                
                # 2. Parse based on Bank
                if bank == 'HDFC':
                    return self._parse_hdfc(pdf)
                elif bank == 'ICICI':
                    return self._parse_icici(pdf)
                elif bank == 'SBI':
                    return self._parse_sbi(pdf)
                else:
                    print(f"Bank format not recognized. Attempting Universal Parser...")
                    return self._parse_universal(pdf)
                    
        except Exception as e:
            if "password" in str(e).lower():
                raise ValueError("PDF is password protected. Please provide a password.")
            raise e

    def _detect_bank(self, text: str) -> str:
        text = text.upper()
        if "HDFC BANK" in text:
            return "HDFC"
        elif "ICICI BANK" in text:
            return "ICICI"
        elif "STATE BANK OF INDIA" in text:
            return "SBI"
        return "UNKNOWN"

    def _parse_hdfc(self, pdf) -> List[TransactionData]:
        transactions = []
        for page in pdf.pages:
            tables = page.extract_tables()
            for table in tables:
                for row in table:
                    # Basic validation for HDFC row structure
                    # Date, Narration, ..., Withdrawal, Deposit, Closing Balance
                    if not row or len(row) < 3: continue
                    
                    try:
                        date_str = self._parse_date(row[0])
                        if not date_str: continue
                        
                        desc = row[1]
                        withdrawal = self._parse_amount(row[-3]) # Usually 3rd from last
                        deposit = self._parse_amount(row[-2])    # Usually 2nd from last
                        
                        amount = 0.0
                        if withdrawal > 0:
                            amount = -withdrawal
                        elif deposit > 0:
                            amount = deposit
                            
                        if amount == 0: continue

                        transactions.append(TransactionData(
                            date=date_str,
                            amount=int(round(amount * 100)),
                            description=desc
                        ))
                    except (ValueError, IndexError):
                        continue
        return transactions

    def _parse_icici(self, pdf) -> List[TransactionData]:
        # ICICI typically has: S.No, Value Date, Transaction Date, Cheque, Description, Dr, Cr, Balance
        # Logic similar to HDFC, adapt indices
        transactions = []
        for page in pdf.pages:
            tables = page.extract_tables()
            for table in tables:
                for row in table:
                    if not row or len(row) < 5: continue
                    
                    # Try finding date in first few cols
                    date_str = self._parse_date(row[1]) # Value Date typically
                    if not date_str:
                         date_str = self._parse_date(row[2]) # Txn Date
                    if not date_str: continue

                    desc = row[4]
                    debit = self._parse_amount(row[5])
                    credit = self._parse_amount(row[6])

                    amount = 0.0
                    if debit > 0:
                         amount = -debit
                    elif credit > 0:
                         amount = credit
                    
                    if amount == 0: continue

                    transactions.append(TransactionData(
                        date=date_str,
                        amount=int(round(amount * 100)),
                        description=desc
                    ))
        return transactions
                    
    def _parse_sbi(self, pdf) -> List[TransactionData]:
        # SBI often messy, regex might be needed if tables fail
        # Date, Description, Ref, Debit, Credit, Balance
        transactions = []
        for page in pdf.pages:
             # Try table first
            tables = page.extract_tables()
            if tables:
                for table in tables:
                    for row in table:
                        if not row or len(row) < 5: continue
                        date_str = self._parse_date(row[0])
                        if not date_str: continue
                        
                        desc = row[2] # Description often 3rd col
                        debit = self._parse_amount(row[3])
                        credit = self._parse_amount(row[4])
                        
                        amount = 0.0
                        if debit > 0: amount = -debit
                        elif credit > 0: amount = credit
                        if amount == 0: continue

                        transactions.append(TransactionData(
                            date=date_str,
                            amount=int(round(amount * 100)),
                            description=desc
                        ))
            else:
                # Fallback to Text Line parsing logic (Simplified for this version)
                pass # TODO: Implement Regex Fallback
        
        return transactions

    def _parse_universal(self, pdf) -> List[TransactionData]:
        """
        Universal fallback parser. Scans tables for consistent date/amount pattern.
        """
        transactions = []
        
        # Heuristics:
        # 1. Look for a Date column (DD/MM/YYYY or YYYY-MM-DD)
        # 2. Look for Amount column(s) - Debit/Credit or single Amount
        # 3. Description is usually the longest text column
        
        for page in pdf.pages:
            tables = page.extract_tables()
            for table in tables:
                if not table: continue
                
                # Analyze Header / First few rows to identify indices
                date_idx = -1
                desc_idx = -1
                amount_indices = [] # Could be multiple (Debit, Credit) or single (Amount)
                
                # --- STRATEGY 1: Header Detection (Priority) ---
                # Check the first row for specific keywords
                header_row = [str(cell).lower().strip() for cell in table[0]] if table else []
                
                debit_idx = -1
                credit_idx = -1
                
                # Check headers
                for i, col in enumerate(header_row):
                    if any(k in col for k in ['date', 'datum']):
                        date_idx = i
                    elif any(k in col for k in ['description', 'omschrijving', 'narration', 'particulars']):
                        desc_idx = i
                    elif any(k in col for k in ['amount credited', 'credit', 'bij', 'deposit']):
                        credit_idx = i
                    elif any(k in col for k in ['amount debited', 'debit', 'af', 'withdrawal']):
                        debit_idx = i
                    elif 'amount' in col or 'bedrag' in col:
                        # Fallback if no specific deb/cred
                        amount_indices.append(i)

                # If we found explicit Debit/Credit columns via headers, use them
                if credit_idx != -1 or debit_idx != -1:
                    if credit_idx != -1: amount_indices.append(credit_idx)
                    if debit_idx != -1: amount_indices.append(debit_idx)
                    # Ensure date/desc were found, else fallback to heuristics for them
                
                # --- STRATEGY 2: Heuristic Detection (Fallback) ---
                if date_idx == -1:
                    # Check first 5 rows to find date column
                    for col_idx in range(len(table[0])):
                        matches = 0
                        for row in table[:10]: # Check first 10 rows
                            if col_idx < len(row) and self._parse_date(row[col_idx]):
                                matches += 1
                        if matches >= 3: 
                            date_idx = col_idx
                            break
                
                if date_idx == -1: continue # No date parsing possible
                
                # If amounts not found via headers, use numeric heuristic
                if not amount_indices:
                    numeric_cols = []
                    for col_idx in range(len(table[0])):
                         if col_idx == date_idx: continue
                         is_numeric = 0
                         for row in table[:10]:
                             if col_idx < len(row) and self._is_numeric(row[col_idx]):
                                 is_numeric += 1
                         if is_numeric >= 3:
                             numeric_cols.append(col_idx)
                    amount_indices = numeric_cols

                # Description: Longest average length column
                if desc_idx == -1:
                    max_len = 0
                    for col_idx in range(len(table[0])):
                        if col_idx == date_idx or col_idx in amount_indices: continue
                        avg_len = sum([len(str(r[col_idx])) for r in table[:10] if col_idx < len(r)]) / 10
                        if avg_len > max_len:
                            max_len = avg_len
                            desc_idx = col_idx

                # Parse rows with identified indices
                for row_idx, row in enumerate(table):
                    # Skip header row if it contains text like "Date"
                    if row_idx == 0 and date_idx != -1 and "date" in str(row[date_idx]).lower():
                        continue
                        
                    if len(row) <= max(date_idx, desc_idx, max(amount_indices) if amount_indices else 0): continue
                    
                    date_str = self._parse_date(row[date_idx])
                    if not date_str: continue
                    
                    desc = row[desc_idx] if desc_idx != -1 else "Unknown Transaction"
                    
                    # Determine amount logic
                    amount = 0.0
                    
                    # Explicit Header-based Logic
                    if debit_idx != -1 or credit_idx != -1:
                        d_val = 0.0
                        c_val = 0.0
                        
                        if debit_idx != -1 and debit_idx < len(row):
                            d_val = self._parse_amount(row[debit_idx])
                        if credit_idx != -1 and credit_idx < len(row):
                            c_val = self._parse_amount(row[credit_idx])
                            
                        if d_val > 0: amount = -d_val
                        elif c_val > 0: amount = c_val
                        # Note: d_val might be negative if parser returned negative, handle abs
                        # Actually _parse_amount returns +/- based on CR/DR text, but raw numbers are positive
                        # Let's trust _parse_amount returns positive for numbers usually.
                    
                    elif len(amount_indices) >= 2:
                        debit = self._parse_amount(row[amount_indices[0]])
                        credit = self._parse_amount(row[amount_indices[1]])
                        if debit > 0: amount = -debit
                        elif credit > 0: amount = credit
                    elif len(amount_indices) == 1:
                        val = self._parse_amount(row[amount_indices[0]])
                        # If simple Amount column, heuristic: usually expense if no CR/DR flag.
                        # Can't guess sign easily. defaulting to negative (expense) for now as typical statement view? 
                        # Or check for 'Cr' 'Dr' suffix? 
                        # Let's assume negative if not specified, usually standard for CC statements.
                        amount = -abs(val) 
                        
                    if amount == 0: continue
                    
                    transactions.append(TransactionData(
                        date=date_str,
                        amount=int(round(amount * 100)),
                        description=desc
                    ))
                    
        return transactions

    def _is_numeric(self, raw: Any) -> bool:
        if not raw: return False
        # Remove common currency symbols and separators
        s = str(raw).replace(',', '').replace('.', '').replace(' ', '').replace('€', '').replace('$', '').replace('₹', '').strip()
        # Handle Cr/Dr signs
        s = s.replace('Cr', '').replace('Dr', '').replace('CR', '').replace('DR', '').strip()
        try:
            float(s)
            return True
        except ValueError:
            return False

    def _parse_date(self, raw: str) -> Optional[str]:
        if not raw: return None
        raw = str(raw).strip()
        # Common formats: DD-MM-YYYY, DD/MM/YYYY, DD.MM.YY
        formats = [
            "%d/%m/%Y", "%d-%m-%Y", "%d.%m.%Y", 
            "%d %b %Y", "%Y-%m-%d", "%d.%m.%y"
        ]
        for fmt in formats:
            try:
                return datetime.strptime(raw, fmt).strftime("%Y-%m-%d")
            except ValueError:
                continue
        return None

    def _parse_amount(self, raw: Any) -> float:
        if not raw: return 0.0
        s = str(raw).strip()
        
        # Handle Cr/Dr suffixes commonly found in PDFs
        multiplier = 1.0
        if s.upper().endswith(" DR") or s.upper().endswith("DR"):
            multiplier = -1.0
        elif s.upper().endswith(" CR") or s.upper().endswith("CR"):
            multiplier = 1.0
            
        # Clean currency symbols and text
        s = re.sub(r'[^\d.,-]', '', s)
        if not s: return 0.0
        
        try:
            # Heuristic for Decimal Separator
            # If comma is after the last dot (1.234,56) -> comma is decimal
            # If dot is after the last comma (1,234.56) -> dot is decimal
            last_comma = s.rfind(',')
            last_dot = s.rfind('.')
            
            if last_comma > last_dot:
                # Format: 1.234,56 (EU)
                s = s.replace('.', '').replace(',', '.')
            else:
                # Format: 1,234.56 (US/UK/India)
                s = s.replace(',', '')
                
            return float(s) * multiplier
        except ValueError:
            return 0.0
