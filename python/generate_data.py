"""
Synthetic data generator for UK AML/fraud pipeline.

Generates:
- customers, accounts, merchants, locations, transactions
- Injects fraud patterns:
  - Structuring (multiple £9k–£9.9k transactions in 72h)
  - Velocity spikes
  - Impossible travel
"""

import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import random
import os

np.random.seed(42)
random.seed(42)

# ---------- CONFIG ----------
N_CUSTOMERS = 500
N_ACCOUNTS = 800
N_MERCHANTS = 200
N_LOCATIONS = 50
N_TRANSACTIONS = 5000  # small but enough for demo

FRAUD_ACCOUNTS_STRUCTURING = 10
FRAUD_ACCOUNTS_VELOCITY = 10
FRAUD_ACCOUNTS_TRAVEL = 10

# ---------- HELPERS ----------
def random_date(start, end):
    delta = end - start
    return start + timedelta(days=random.randint(0, delta.days))

# ---------- LOCATIONS ----------
countries = ["GB", "FR", "DE", "US", "AE", "IN"]
cities_by_country = {
    "GB": ["London", "Manchester", "Birmingham"],
    "FR": ["Paris", "Lyon"],
    "DE": ["Berlin", "Munich"],
    "US": ["New York", "Los Angeles"],
    "AE": ["Dubai", "Abu Dhabi"],
    "IN": ["Mumbai", "Delhi"],
}

# Rough lat/lng for demo
lat_lng = {
    "London": (51.5074, -0.1278),
    "Manchester": (53.4808, -2.2426),
    "Birmingham": (52.4862, -1.8904),
    "Paris": (48.8566, 2.3522),
    "Lyon": (45.7640, 4.8357),
    "Berlin": (52.5200, 13.4050),
    "Munich": (48.1351, 11.5820),
    "New York": (40.7128, -74.0060),
    "Los Angeles": (34.0522, -118.2437),
    "Dubai": (25.2048, 55.2708),
    "Abu Dhabi": (24.4539, 54.3773),
    "Mumbai": (19.0760, 72.8777),
    "Delhi": (28.7041, 77.1025),
}

locations_data = []
for loc_id in range(1, N_LOCATIONS + 1):
    country = random.choice(countries)
    city = random.choice(cities_by_country[country])
    lat, lng = lat_lng[city]
    locations_data.append({
        "location_id": loc_id,
        "city": city,
        "country": country,
        "lat": lat,
        "lng": lng
    })
locations_df = pd.DataFrame(locations_data)

# ---------- MERCHANTS ----------
merchant_categories = ["RETAIL", "ONLINE", "CRYPTO", "MSB", "RESTAURANT", "TRAVEL"]
merchants_data = []
for m_id in range(1, N_MERCHANTS + 1):
    cat = random.choice(merchant_categories)
    country = random.choice(countries)
    risk_score = random.randint(1, 5) if cat in ["CRYPTO", "MSB"] else random.randint(1, 3)
    merchants_data.append({
        "merchant_id": m_id,
        "name": f"Merchant_{m_id}",
        "category": cat,
        "country": country,
        "risk_score": risk_score
    })
merchants_df = pd.DataFrame(merchants_data)

# ---------- CUSTOMERS ----------
customers_data = []
for c_id in range(1, N_CUSTOMERS + 1):
    country = random.choice(countries)
    risk_rating = random.choices(["LOW", "MEDIUM", "HIGH"], weights=[0.7, 0.25, 0.05])[0]
    customers_data.append({
        "customer_id": c_id,
        "name": f"Customer_{c_id}",
        "country": country,
        "risk_rating": risk_rating,
        "onboard_date": random_date(datetime(2020, 1, 1), datetime(2025, 1, 1)).date()
    })
customers_df = pd.DataFrame(customers_data)

# ---------- ACCOUNTS ----------
accounts_data = []
for a_id in range(1, N_ACCOUNTS + 1):
    cust_id = random.randint(1, N_CUSTOMERS)
    acc_type = random.choice(["CURRENT", "SAVINGS", "BUSINESS"])
    currency = "GBP" if random.random() < 0.8 else random.choice(["EUR", "USD"])
    accounts_data.append({
        "account_id": a_id,
        "customer_id": cust_id,
        "account_type": acc_type,
        "currency": currency,
        "open_date": random_date(datetime(2020, 1, 1), datetime(2025, 1, 1)).date(),
        "status": "ACTIVE"
    })
accounts_df = pd.DataFrame(accounts_data)

# ---------- TRANSACTIONS (base) ----------
txn_types = ["DEBIT", "CREDIT", "TRANSFER_IN", "TRANSFER_OUT", "CASH_DEPOSIT", "CASH_WITHDRAWAL"]
channels = ["ONLINE", "MOBILE", "BRANCH", "ATM"]

transactions_data = []

start_date = datetime(2025, 1, 1)
end_date = datetime(2025, 9, 1)

for t_id in range(1, N_TRANSACTIONS + 1):
    acc_id = random.randint(1, N_ACCOUNTS)
    merch_id = random.randint(1, N_MERCHANTS) if random.random() < 0.8 else None
    txn_type = random.choice(txn_types)
    amount = round(random.uniform(5, 2000), 2)
    currency = "GBP" if random.random() < 0.85 else random.choice(["EUR", "USD"])
    ts = random_date(start_date, end_date)
    loc_id = random.randint(1, N_LOCATIONS)
    channel = random.choice(channels)
    counterparty = random.randint(1, N_ACCOUNTS) if txn_type in ["TRANSFER_IN", "TRANSFER_OUT"] else None
    is_fraud = 0

    transactions_data.append({
        "txn_id": t_id,
        "account_id": acc_id,
        "merchant_id": merch_id,
        "txn_type": txn_type,
        "amount": amount,
        "currency": currency,
        "txn_timestamp": ts,
        "location_id": loc_id,
        "channel": channel,
        "counterparty_account_id": counterparty,
        "is_fraud_label": is_fraud
    })

transactions_df = pd.DataFrame(transactions_data)

# ---------- INJECT FRAUD PATTERNS ----------

next_txn_id = transactions_df["txn_id"].max() + 1

# 1) Structuring: multiple £9k–£9.9k in 72h
structuring_accounts = random.sample(range(1, N_ACCOUNTS + 1), FRAUD_ACCOUNTS_STRUCTURING)
for acc in structuring_accounts:
    base_ts = random_date(start_date, end_date - timedelta(days=5))
    for i in range(random.randint(4, 7)):
        next_txn_id += 1
        amount = round(random.uniform(9000, 9900), 2)
        ts = base_ts + timedelta(hours=random.randint(1, 60))
        loc_id = random.randint(1, N_LOCATIONS)
        transactions_df = pd.concat([
            transactions_df,
            pd.DataFrame([{
                "txn_id": next_txn_id,
                "account_id": acc,
                "merchant_id": None,
                "txn_type": "CASH_DEPOSIT",
                "amount": amount,
                "currency": "GBP",
                "txn_timestamp": ts,
                "location_id": loc_id,
                "channel": "BRANCH",
                "counterparty_account_id": None,
                "is_fraud_label": 1
            }])
        ], ignore_index=True)

# 2) Velocity spikes: many transactions in 24h
velocity_accounts = random.sample(range(1, N_ACCOUNTS + 1), FRAUD_ACCOUNTS_VELOCITY)
for acc in velocity_accounts:
    base_ts = random_date(start_date, end_date - timedelta(days=1))
    n_burst = random.randint(15, 30)
    for i in range(n_burst):
        next_txn_id += 1
        amount = round(random.uniform(50, 500), 2)
        ts = base_ts + timedelta(minutes=random.randint(0, 1400))
        loc_id = random.randint(1, N_LOCATIONS)
        transactions_df = pd.concat([
            transactions_df,
            pd.DataFrame([{
                "txn_id": next_txn_id,
                "account_id": acc,
                "merchant_id": random.randint(1, N_MERCHANTS),
                "txn_type": random.choice(["DEBIT", "CREDIT"]),
                "amount": amount,
                "currency": "GBP",
                "txn_timestamp": ts,
                "location_id": loc_id,
                "channel": random.choice(channels),
                "counterparty_account_id": None,
                "is_fraud_label": 1
            }])
        ], ignore_index=True)

# 3) Impossible travel: same account, far locations within <2h
travel_accounts = random.sample(range(1, N_ACCOUNTS + 1), FRAUD_ACCOUNTS_TRAVEL)
# pick two far locations (e.g., London and Dubai)
loc_pairs = [
    (1, 10),  # assume some IDs are far apart; this is a simplification
    (2, 11),
    (3, 12),
]
for acc in travel_accounts:
    base_ts = random_date(start_date, end_date - timedelta(days=2))
    loc1, loc2 = random.choice(loc_pairs)
    for i in range(2):
        next_txn_id += 1
        ts1 = base_ts + timedelta(hours=i*24)
        ts2 = ts1 + timedelta(minutes=random.randint(30, 90))
        for loc_id in [loc1, loc2]:
            next_txn_id += 1
            transactions_df = pd.concat([
                transactions_df,
                pd.DataFrame([{
                    "txn_id": next_txn_id,
                    "account_id": acc,
                    "merchant_id": random.randint(1, N_MERCHANTS),
                    "txn_type": "DEBIT",
                    "amount": round(random.uniform(100, 1000), 2),
                    "currency": "GBP",
                    "txn_timestamp": ts1 if loc_id == loc1 else ts2,
                    "location_id": loc_id,
                    "channel": "ONLINE",
                    "counterparty_account_id": None,
                    "is_fraud_label": 1
                }])
            ], ignore_index=True)

# Sort by txn_id and timestamp
transactions_df = transactions_df.sort_values(["txn_id", "txn_timestamp"]).reset_index(drop=True)

# ---------- SAVE TO CSV ----------
os.makedirs("../data", exist_ok=True)

customers_df.to_csv("../data/customers.csv", index=False)
accounts_df.to_csv("../data/accounts.csv", index=False)
merchants_df.to_csv("../data/merchants.csv", index=False)
locations_df.to_csv("../data/locations.csv", index=False)
transactions_df.to_csv("../data/transactions_raw.csv", index=False)

print("Data generation complete. Files saved in ../data/")
print("Transactions rows:", len(transactions_df))
