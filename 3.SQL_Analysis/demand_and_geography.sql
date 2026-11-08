-- Query 1: Requests per month and change from the previous month
WITH monthly_counts AS (
    SELECT
        DATE_TRUNC('month', created_date) AS month,
        COUNT(*) AS total_requests
    FROM service_request
    GROUP BY DATE_TRUNC('month', created_date)
)
SELECT
    month,
    total_requests,
    total_requests - LAG(total_requests) OVER (ORDER BY month) AS net_change
FROM monthly_counts
ORDER BY month;


-- Query 2: Number of requests per borough and share of the city total
SELECT
    l.borough,
    COUNT(*) AS total_requests,
    ROUND(100.0 * COUNT(*) / (SELECT COUNT(*) FROM service_request), 2) AS request_pct
FROM service_request sr
JOIN location l ON sr.location_id = l.location_id
GROUP BY l.borough
ORDER BY total_requests DESC;


-- Query 3: Number of requests still open per borough
SELECT
    l.borough,
    COUNT(*) AS open_requests
FROM service_request sr
JOIN location l ON sr.location_id = l.location_id
WHERE sr.status <> 'Closed'
GROUP BY l.borough
ORDER BY open_requests DESC;


-- Query 4: 10 most common complaint types
SELECT
    ct.complaint_type,
    COUNT(*) AS request_count
FROM service_request sr
JOIN complaint_type ct ON sr.complaint_type_id = ct.complaint_type_id
GROUP BY ct.complaint_type
ORDER BY request_count DESC
LIMIT 10;


-- Query 5: 3 most common complaint types in each borough
WITH borough_complaints AS (
    SELECT
        l.borough,
        ct.complaint_type,
        COUNT(*) AS requests,
        DENSE_RANK() OVER (
            PARTITION BY l.borough
            ORDER BY COUNT(*) DESC
        ) AS rank
    FROM service_request sr
    JOIN location l ON sr.location_id = l.location_id
    JOIN complaint_type ct ON sr.complaint_type_id = ct.complaint_type_id
    WHERE l.borough <> 'Unspecified'
    GROUP BY l.borough, ct.complaint_type
)
SELECT borough, rank, complaint_type, requests
FROM borough_complaints
WHERE rank <= 3
ORDER BY borough, rank;


-- Query 6: ZIP codes with the most requests
-- (missing ZIP codes are stored as 'Unknown')
SELECT
    l.incident_zip,
    l.borough,
    COUNT(*) AS request_count
FROM service_request sr
JOIN location l ON sr.location_id = l.location_id
WHERE l.incident_zip <> 'Unknown'
GROUP BY l.incident_zip, l.borough
ORDER BY request_count DESC
LIMIT 10;


-- Query 7: Unsolved requests by status
-- (which kind of unfinished work makes up the backlog?)
SELECT
    status,
    COUNT(*) AS requests
FROM service_request
WHERE status <> 'Closed'
GROUP BY status
ORDER BY requests DESC;
