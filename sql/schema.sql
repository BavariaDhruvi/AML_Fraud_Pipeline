-- Customers
CREATE TABLE customers (
    customer_id   SERIAL PRIMARY KEY,
    name          TEXT,
    country       TEXT,
    risk_rating   TEXT,
    onboard_date  DATE
);

-- Accounts
CREATE TABLE accounts (
    account_id    SERIAL PRIMARY KEY,
    customer_id   INT REFERENCES customers(customer_id),
    account_type  TEXT,
    currency      TEXT,
    open_date     DATE,
    status        TEXT
);

-- Merchants
CREATE TABLE merchants (
    merchant_id   SERIAL PRIMARY KEY,
    name          TEXT,
    category      TEXT,
    country       TEXT,
    risk_score    INT
);

-- Locations
CREATE TABLE locations (
    location_id   SERIAL PRIMARY KEY,
    city          TEXT,
    country       TEXT,
    lat           NUMERIC,
    lng           NUMERIC
);

-- Transactions
CREATE TABLE transactions (
    txn_id                SERIAL PRIMARY KEY,
    account_id            INT REFERENCES accounts(account_id),
    merchant_id           INT REFERENCES merchants(merchant_id),
    txn_type              TEXT,
    amount                NUMERIC,
    currency              TEXT,
    txn_timestamp         TIMESTAMP,
    location_id           INT REFERENCES locations(location_id),
    channel               TEXT,
    counterparty_account_id INT,
    is_fraud_label        INT
);
