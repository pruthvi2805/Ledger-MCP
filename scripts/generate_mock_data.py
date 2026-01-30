import csv
import random
from datetime import datetime, timedelta

SAMPLE_MERCHANTS = ["Swiggy", "Zomato", "Uber", "Ola", "Netflix", "Amazon", "Flipkart", "Starbucks", "HDFC Bank", "ZERODHA"]
EDGE_CASES = [
    # Rounding
    {"desc": "Rounding Check 1", "amt": 100.505},
    {"desc": "Rounding Check 2", "amt": 0.01},
    {"desc": "Rounding Check 3", "amt": 9999999.99},
    # Encoding
    {"desc": "Unicode Café", "amt": 150.0},
    {"desc": "Emoji 🍕 Transaction", "amt": 500.0},
    # Negative/Credit handled via sign in generator
]

def generate_csv(filename: str, rows: int = 5000):
    with open(filename, 'w', newline='', encoding='utf-8') as f:
        writer = csv.writer(f)
        writer.writerow(["Date", "Description", "Debit", "Credit", "Balance"])
        
        start_date = datetime(2025, 1, 1)
        
        # 1. Edge Cases
        for case in EDGE_CASES:
            writer.writerow([
                start_date.strftime("%Y-%m-%d"),
                case['desc'],
                case['amt'],
                "",
                0
            ])
            
        # 2. Bulk Random Data
        for i in range(rows):
            date_obj = start_date + timedelta(days=random.randint(0, 365))
            date_str = date_obj.strftime(random.choice(["%Y-%m-%d", "%d/%m/%Y", "%d-%m-%Y"]))
            
            merchant = random.choice(SAMPLE_MERCHANTS)
            desc = f"UPI-{merchant}-{random.randint(1000,9999)}"
            amount = round(random.uniform(10.0, 5000.0), 2)
            
            if random.random() > 0.8: # 20% Income
                writer.writerow([date_str, f"Refund {desc}", "", amount, 0])
            else:
                writer.writerow([date_str, desc, amount, "", 0])
                
        # 3. Malformed Dates (Parser should handle gracefully or skip)
        writer.writerow(["99-99-2025", "Bad Date Transaction", 100, "", 0])

if __name__ == "__main__":
    generate_csv("tests/stress_test.csv")
    print("Generated tests/stress_test.csv")
