import pandas as pd
from typing import List, Optional
from datetime import datetime
import re
from .base import BaseParser, TransactionData

class CSVParser(BaseParser):
    def parse(self, file_path: str, password: Optional[str] = None) -> List[TransactionData]:
        # Using pandas with python engine for better separator handling if needed
        # Assuming standard csv
        df = pd.read_csv(file_path)
        
        # Normalize headers
        df.columns = [c.strip().lower() for c in df.columns]
        
        date_col = self._find_column(df, ['date', 'txn date', 'transaction date'])
        desc_col = self._find_column(df, ['description', 'narration', 'particulars', 'remarks'])
        amount_col = self._find_column(df, ['amount', 'txn amount', 'debit', 'credit']) # Needs careful handling of Cr/Dr
        
        # Split credit/debit if they exist separately
        debit_col = self._find_column(df, ['debit', 'withdrawal'])
        credit_col = self._find_column(df, ['credit', 'deposit'])
        
        transactions = []
        
        for _, row in df.iterrows():
            # Date Parsing
            date_str = None
            raw_date = str(row[date_col])
            for fmt in ["%Y-%m-%d", "%d/%m/%Y", "%d-%m-%Y"]:
                try:
                    date_obj = datetime.strptime(raw_date, fmt)
                    date_str = date_obj.strftime("%Y-%m-%d")
                    break
                except ValueError:
                    continue
            
            if not date_str:
                continue # Skip invalid dates (maybe header/footer rows)

            # Amount Parsing
            amount_val = 0.0
            if debit_col and credit_col:
                debit = self._parse_amount(row.get(debit_col))
                credit = self._parse_amount(row.get(credit_col))
                if debit > 0:
                    amount_val = -debit
                elif credit > 0:
                    amount_val = credit
                # If both are 0, it stays 0
            elif amount_col:
                amount_val = self._parse_amount(row[amount_col])
                # Heuristic: if separate type column exists
                type_col = self._find_column(df, ['type', 'dr/cr'])
                if type_col:
                    val_type = str(row[type_col]).lower()
                    if 'dr' in val_type or 'debit' in val_type:
                        amount_val = -abs(amount_val)
                    elif 'cr' in val_type or 'credit' in val_type:
                        amount_val = abs(amount_val)
            
            # Convert to Integer Paise
            amount_int = int(round(amount_val * 100))
            
            desc = str(row[desc_col]) if desc_col else "Unknown"
            
            transactions.append(TransactionData(
                date=date_str,
                amount=amount_int,
                description=desc
            ))
            
        return transactions

    def _find_column(self, df: pd.DataFrame, keywords: List[str]) -> Optional[str]:
        for col in df.columns:
            if any(k in col for k in keywords):
                return col
        return None

    def _parse_amount(self, val: Any) -> float:
        if pd.isna(val) or val == '':
            return 0.0
        s = str(val).replace(',', '').strip()
        try:
            return float(s)
        except ValueError:
            return 0.0
