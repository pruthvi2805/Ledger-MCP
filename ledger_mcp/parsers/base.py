from abc import ABC, abstractmethod
from typing import List, Dict, Any, Optional
from dataclasses import dataclass
from datetime import date

@dataclass
class TransactionData:
    date: str
    amount: int  # in paise
    description: str
    merchant: Optional[str] = None
    category: str = "Uncategorized"
    currency: str = "INR"

class BaseParser(ABC):
    @abstractmethod
    def parse(self, file_path: str, password: Optional[str] = None, interactive: bool = False) -> List[TransactionData]:
        """
        Parse the file and return a list of TransactionData objects.
        """
        pass
