# UK AML & Fraud Detection Pipeline

End-to-end SQL + ML project simulating banking transactions and detecting:
- Structuring (multiple transactions just under £10k)
- Velocity anomalies
- Impossible travel / geographic red flags

## Fraud patterns to detect

1. **Structuring / smurfing**  
   Multiple cash deposits or transfers between £9,000–£9,900 within 72 hours on the same account.

2. **Velocity anomalies**  
   Sudden spike in transaction count or value vs. account’s normal behavior.

3. **Impossible travel**  
   Transactions in different countries with impossibly short time between them.

4. **Rapid fund cycling (optional)**  
   Large inflow followed by >80% outflow within 24 hours.

## Data

Synthetic datasets (in `data/`):
- `customers.csv` – customer profiles and risk ratings  
- `accounts.csv` – accounts linked to customers  
- `merchants.csv` – merchants with categories and risk scores  
- `locations.csv` – cities/countries with lat/lng  
- `transactions_raw.csv` – transactions with injected fraud patterns:
  - Structuring accounts (multiple £9k–£9.9k in 72h)
  - Velocity spike accounts (many transactions in 24h)
  - Impossible travel accounts (far locations within <2h)
   
## SQL queries

- `sql/01_structuring_detection.sql` – Detects basic structuring patterns:  
  multiple transactions between £9,000–£9,900 within 72 hours on the same account.
