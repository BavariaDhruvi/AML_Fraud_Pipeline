"""
Synthetic data generator for UK AML/fraud pipeline.
"""

import pandas as pd

if __name__ == "__main__":
    # Dummy transactions to start
    data = {
        "txn_id": [1, 2, 3],
        "account_id": [1, 1, 2],
        "merchant_id": [1, 2, None],
        "txn_type": ["DEBIT", "DEBIT", "CREDIT"],
        "amount": [100.0, 9500.0, 500.0],
        "currency": ["GBP", "GBP", "GBP"],
        "txn_timestamp": [
            "2025-01-01 10:00:00",
            "2025-01-01 10:05:00",
            "2025-01-01 11:00:00",
        ],
        "location_id": [1, 2, 1],
        "channel": ["ONLINE", "ONLINE", "MOBILE"],
        "counterparty_account_id": [None, None, 3],
        "is_fraud_label": [0, 0, 0],
    }
    df = pd.DataFrame(data)
    df.to_csv("../data/transactions_raw.csv", index=False)
    print("Dummy transactions file created.")
