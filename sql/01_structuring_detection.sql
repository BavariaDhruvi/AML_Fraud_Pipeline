-- 01_structuring_detection.sql
-- Detect accounts with multiple transactions between £9,000 and £9,900
-- within a 72-hour window (basic structuring/smurfing pattern).

WITH near_threshold AS (
    SELECT
        account_id,
        txn_timestamp,
        amount,
        LAG(txn_timestamp) OVER (
            PARTITION BY account_id
            ORDER BY txn_timestamp
        ) AS prev_txn_ts
    FROM transactions
    WHERE amount BETWEEN 9000 AND 9999
      AND currency = 'GBP'
),
struct_flags AS (
    SELECT
        account_id,
        txn_timestamp,
        amount,
        prev_txn_ts,
        EXTRACT(EPOCH FROM (txn_timestamp - prev_txn_ts)) / 3600 AS hours_since_prev
    FROM near_threshold
    WHERE prev_txn_ts IS NOT NULL
)
SELECT
    account_id,
    COUNT(*) AS near_threshold_txn_count,
    MIN(txn_timestamp) AS first_txn,
    MAX(txn_timestamp) AS last_txn,
    SUM(amount) AS total_amount
FROM struct_flags
WHERE hours_since_prev <= 72  -- within 72 hours
GROUP BY account_id
HAVING COUNT(*) >= 4;         -- at least 4 near-threshold transactions
