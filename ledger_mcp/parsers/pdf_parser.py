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
                    raise ValueError("Unknown bank format")
                    
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

    def _parse_date(self, raw: str) -> Optional[str]:
        if not raw: return None
        raw = str(raw).strip()
        for fmt in ["%d/%m/%Y", "%d-%m-%Y", "%d %b %Y"]:
            try:
                return datetime.strptime(raw, fmt).strftime("%Y-%m-%d")
            except ValueError:
                continue
        return None

    def _parse_amount(self, raw: Any) -> float:
        if not raw: return 0.0
        s = str(raw).replace(',', '').replace(' ', '').strip()
        try:
            return float(s)
        except ValueError:
            return 0.0
