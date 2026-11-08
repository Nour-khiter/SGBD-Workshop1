-- =====================================================================
-- CivicPulse - WHEN do requests arrive?
-- Business question: when should the city put more staff?
-- Run in pgAdmin (Query Tool, database nyc311): select ONE query, F5.
-- =====================================================================


-- Query 1: Requests per hour of the day
SELECT
    EXTRACT(HOUR FROM created_date) AS hour_of_day,
    COUNT(*) AS requests,
    ROUND(100.0 * COUNT(*) / (SELECT COUNT(*) FROM service_request), 1) AS pct_of_requests
FROM service_request
GROUP BY EXTRACT(HOUR FROM created_date)
ORDER BY hour_of_day;


-- Query 2: Requests per day of the week (1 = Monday ... 7 = Sunday)
SELECT
    EXTRACT(ISODOW FROM created_date) AS weekday_number,
    COUNT(*) AS requests,
    ROUND(100.0 * COUNT(*) / (SELECT COUNT(*) FROM service_request), 1) AS pct_of_requests
FROM service_request
GROUP BY EXTRACT(ISODOW FROM created_date)
ORDER BY weekday_number;


-- Query 3: Pivot - day of the week x period of the day
-- One row per day, one column per period (pivot with FILTER),
-- and a total row added by ROLLUP (the last row, with an empty weekday).
SELECT
    EXTRACT(ISODOW FROM created_date) AS weekday_number,
    COUNT(*) FILTER (WHERE EXTRACT(HOUR FROM created_date) BETWEEN 0  AND 6)  AS night_0_6,
    COUNT(*) FILTER (WHERE EXTRACT(HOUR FROM created_date) BETWEEN 7  AND 11) AS morning_7_11,
    COUNT(*) FILTER (WHERE EXTRACT(HOUR FROM created_date) BETWEEN 12 AND 17) AS afternoon_12_17,
    COUNT(*) FILTER (WHERE EXTRACT(HOUR FROM created_date) BETWEEN 18 AND 23) AS evening_18_23,
    COUNT(*) AS total
FROM service_request
GROUP BY ROLLUP (EXTRACT(ISODOW FROM created_date))
ORDER BY weekday_number;


-- Query 4: Busiest hour for each of the 5 most common complaint types
-- (the 5 types come from the top-10 query of the demand analysis)
WITH ranked_type_hours AS (
    SELECT
        ct.complaint_type,
        EXTRACT(HOUR FROM sr.created_date) AS hour_of_day,
        COUNT(*) AS requests,
        DENSE_RANK() OVER (
            PARTITION BY ct.complaint_type
            ORDER BY COUNT(*) DESC
        ) AS rank
    FROM service_request sr
    JOIN complaint_type ct ON sr.complaint_type_id = ct.complaint_type_id
    WHERE ct.complaint_type IN ('Illegal Parking', 'Noise - Residential', 'HEAT/HOT WATER',
                                'Blocked Driveway', 'Noise - Street/Sidewalk')
    GROUP BY ct.complaint_type, EXTRACT(HOUR FROM sr.created_date)
)
SELECT complaint_type, hour_of_day AS busiest_hour, requests
FROM ranked_type_hours
WHERE rank = 1
ORDER BY busiest_hour, complaint_type;
