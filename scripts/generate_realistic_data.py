import csv
import random
from datetime import datetime, timedelta

# Realistic Indian merchants across categories
MERCHANTS = {
    "Food": ["Swiggy", "Zomato", "Dunzo", "Blinkit", "Zepto", "McDonald's", "KFC", "Domino's", "Starbucks", "Cafe Coffee Day"],
    "Transport": ["Uber", "Ola", "Rapido", "Namma Metro", "BMTC", "Indian Railways", "Petrol Pump"],
    "Shopping": ["Amazon", "Flipkart", "Myntra", "Ajio", "BigBasket", "DMart", "Reliance Fresh"],
    "Entertainment": ["Netflix", "Prime Video", "Spotify", "Hotstar", "BookMyShow", "PVR Cinemas"],
    "Utilities": ["Jio", "Airtel", "BESCOM", "ACT Fibernet", "Bangalore Water Supply"],
    "Healthcare": ["Apollo Pharmacy", "Practo", "PharmEasy", "Fortis Hospital"],
    "Education": ["Udemy", "Coursera", "Byju's", "Unacademy"],
    "Fitness": ["Cult.fit", "Gold's Gym", "Decathlon"],
}

INCOME_SOURCES = ["Salary", "Freelance Payment", "Interest Credit", "Cashback", "Refund", "Dividend"]

def generate_realistic_csv(filename: str, rows: int = 1000, months: int = 12):
    """Generate realistic Indian bank statement data"""
    with open(filename, 'w', newline='', encoding='utf-8') as f:
        writer = csv.writer(f)
        writer.writerow(["Date", "Description", "Debit", "Credit", "Balance"])
        
        start_date = datetime(2025, 1, 1)
        balance = 50000.0
        
        transactions = []
        
        # Generate transactions
        for i in range(rows):
            # Random date within the period
            days_offset = random.randint(0, months * 30)
            date_obj = start_date + timedelta(days=days_offset)
            
            # 15% chance of income
            if random.random() < 0.15:
                # Income transaction
                source = random.choice(INCOME_SOURCES)
                if source == "Salary":
                    amount = random.choice([50000, 60000, 75000, 100000])
                elif source == "Interest Credit":
                    amount = round(random.uniform(100, 1000), 2)
                else:
                    amount = round(random.uniform(500, 5000), 2)
                
                transactions.append({
                    'date': date_obj,
                    'description': source,
                    'debit': '',
                    'credit': amount,
                    'balance': balance + amount
                })
                balance += amount
            else:
                # Expense transaction
                category = random.choice(list(MERCHANTS.keys()))
                merchant = random.choice(MERCHANTS[category])
                
                # Realistic amounts per category
                if category == "Food":
                    amount = round(random.uniform(50, 1500), 2)
                elif category == "Transport":
                    amount = round(random.uniform(30, 800), 2)
                elif category == "Shopping":
                    amount = round(random.uniform(200, 5000), 2)
                elif category == "Entertainment":
                    amount = round(random.uniform(199, 999), 2)
                elif category == "Utilities":
                    amount = round(random.uniform(300, 2000), 2)
                elif category == "Healthcare":
                    amount = round(random.uniform(100, 3000), 2)
                elif category == "Education":
                    amount = round(random.uniform(500, 10000), 2)
                elif category == "Fitness":
                    amount = round(random.uniform(500, 3000), 2)
                
                # Add UPI prefix for most transactions
                if random.random() < 0.7:
                    desc = f"UPI-{merchant.upper().replace(' ', '')}-{random.randint(1000,9999)}"
                else:
                    desc = merchant
                
                transactions.append({
                    'date': date_obj,
                    'description': desc,
                    'debit': amount,
                    'credit': '',
                    'balance': balance - amount
                })
                balance -= amount
        
        # Sort by date
        transactions.sort(key=lambda x: x['date'])
        
        # Write transactions
        for txn in transactions:
            date_str = txn['date'].strftime("%d-%m-%Y")
            writer.writerow([
                date_str,
                txn['description'],
                txn['debit'],
                txn['credit'],
                txn['balance']
            ])
        
        # Add some recurring subscriptions (same amount, monthly)
        recurring_date = datetime(2025, 1, 15)
        for month in range(months):
            date_str = (recurring_date + timedelta(days=month*30)).strftime("%d-%m-%Y")
            writer.writerow([date_str, "NETFLIX SUBSCRIPTION", 499, "", balance])
            writer.writerow([date_str, "SPOTIFY PREMIUM", 119, "", balance])
            writer.writerow([date_str, "AMAZON PRIME", 1499, "", balance])

if __name__ == "__main__":
    # Generate different sizes
    generate_realistic_csv("tests/realistic_1000.csv", rows=1000, months=12)
    print("Generated tests/realistic_1000.csv (1000 transactions, 12 months)")
    
    generate_realistic_csv("tests/realistic_500.csv", rows=500, months=6)
    print("Generated tests/realistic_500.csv (500 transactions, 6 months)")
    
    generate_realistic_csv("tests/realistic_100.csv", rows=100, months=3)
    print("Generated tests/realistic_100.csv (100 transactions, 3 months)")
