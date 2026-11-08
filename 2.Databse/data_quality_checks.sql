-- =====================================================================
-- Data-quality checks
-- For each possible problem: how many requests have it, and what share.
-- =====================================================================


-- Query 1: The list of problems
-- One small SELECT per problem, stacked with UNION ALL.
-- The subquery gives the total number of requests, for the percentage.
SELECT 'No due date' AS check_name,
       COUNT(*) AS rows_affected,
       ROUND(100.0 * COUNT(*) / (SELECT COUNT(*) FROM service_request), 2) AS pct_of_requests
FROM service_request
WHERE due_date IS NULL

UNION ALL
SELECT 'No closed date',
       COUNT(*),
       ROUND(100.0 * COUNT(*) / (SELECT COUNT(*) FROM service_request), 2)
FROM service_request
WHERE closed_date IS NULL

UNION ALL
SELECT 'Status Closed but no closed date',
       COUNT(*),
       ROUND(100.0 * COUNT(*) / (SELECT COUNT(*) FROM service_request), 2)
FROM service_request
WHERE status = 'Closed' AND closed_date IS NULL

UNION ALL
SELECT 'Closed before created',
       COUNT(*),
       ROUND(100.0 * COUNT(*) / (SELECT COUNT(*) FROM service_request), 2)
FROM service_request
WHERE closed_date < created_date

UNION ALL
SELECT 'Took more than 90 days to close',
       COUNT(*),
       ROUND(100.0 * COUNT(*) / (SELECT COUNT(*) FROM service_request), 2)
FROM service_request
WHERE closed_date - created_date > INTERVAL '90 days'

UNION ALL
SELECT 'No GPS coordinates',
       COUNT(*),
       ROUND(100.0 * COUNT(*) / (SELECT COUNT(*) FROM service_request), 2)
FROM service_request
WHERE latitude IS NULL OR longitude IS NULL

UNION ALL
SELECT 'No ZIP code',
       COUNT(*),
       ROUND(100.0 * COUNT(*) / (SELECT COUNT(*) FROM service_request), 2)
FROM service_request sr
JOIN location l ON sr.location_id = l.location_id
WHERE l.incident_zip = 'Unknown'

UNION ALL
SELECT 'Borough Unspecified',
       COUNT(*),
       ROUND(100.0 * COUNT(*) / (SELECT COUNT(*) FROM service_request), 2)
FROM service_request sr
JOIN location l ON sr.location_id = l.location_id
WHERE l.borough = 'Unspecified'

UNION ALL
SELECT 'No problem detail',
       COUNT(*),
       ROUND(100.0 * COUNT(*) / (SELECT COUNT(*) FROM service_request), 2)
FROM service_request sr
JOIN complaint_type ct ON sr.complaint_type_id = ct.complaint_type_id
WHERE ct.descriptor = 'Unspecified'

ORDER BY rows_affected DESC;


-- Query 2: Did we lose rows between the CSV and the database? (should be 0)
SELECT (SELECT COUNT(*) FROM staging_311)     AS rows_in_csv,
       (SELECT COUNT(*) FROM service_request) AS rows_in_database,
       (SELECT COUNT(*) FROM staging_311)
     - (SELECT COUNT(*) FROM service_request) AS rows_lost;
