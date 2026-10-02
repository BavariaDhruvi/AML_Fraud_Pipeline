-- 03_impossible_travel.sql
-- Detect accounts with transactions in far-apart locations within a short time
-- (simple version using Euclidean distance on lat/lng as a proxy).

WITH seq AS (
    SELECT
        t.account_id,
        t.txn_timestamp,
        l.lat AS curr_lat,
        l.lng AS curr_lng,
        LAG(l.lat) OVER (
            PARTITION BY t.account_id
            ORDER BY t.txn_timestamp
        ) AS prev_lat,
        LAG(l.lng) OVER (
            PARTITION BY t.account_id
            ORDER BY t.txn_timestamp
        ) AS prev_lng,
        LAG(t.txn_timestamp) OVER (
            PARTITION BY t.account_id
            ORDER BY t.txn_timestamp
        ) AS prev_txn_ts
    FROM transactions t
    JOIN locations l
      ON t.location_id = l.location_id
    WHERE l.lat IS NOT NULL AND l.lng IS NOT NULL
),
travel AS (
    SELECT
        account_id,
        txn_timestamp,
        prev_txn_ts,
        SQRT(
            POWER(curr_lat - prev_lat, 2) +
            POWER(curr_lng - prev_lng, 2)
        ) * 111 AS approx_km,  -- rough km per degree
        EXTRACT(EPOCH FROM (txn_timestamp - prev_txn_ts)) / 60 AS minutes_between
    FROM seq
    WHERE prev_txn_ts IS NOT NULL
)
SELECT *
FROM travel
WHERE approx_km > 800
  AND minutes_between < 120;  -- e.g., >800 km in under 2 hours
