-- 02_velocity_anomalies.sql
-- Detect accounts with unusually high transaction velocity in a single day
-- compared to their normal behavior (z-score > 3).

WITH daily_counts AS (
    SELECT
        account_id,
        CAST(txn_timestamp AS DATE) AS txn_date,
        COUNT(*) AS txn_count
    FROM transactions
    GROUP BY account_id, CAST(txn_timestamp AS DATE)
),
account_basics AS (
    SELECT
        account_id,
        AVG(txn_count * 1.0) AS avg_daily_txns,
        STDDEV(txn_count * 1.0) AS stddev_daily_txns
    FROM daily_counts
    GROUP BY account_id
),
velocity_flags AS (
    SELECT
        d.account_id,
        d.txn_date,
        d.txn_count,
        a.avg_daily_txns,
        a.stddev_daily_txns,
        (d.txn_count - a.avg_daily_txns) / NULLIF(a.stddev_daily_txns, 0) AS z_score
    FROM daily_counts d
    JOIN account_basics a
      ON d.account_id = a.account_id
)
SELECT *
FROM velocity_flags
WHERE z_score > 3;  -- more than 3 standard deviations above normal
