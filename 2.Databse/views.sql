-- =====================================================================
-- 05 - Views for the Power BI dashboard
-- A view is a named, stored query: Power BI reads it like a table, and
-- =====================================================================

DROP VIEW IF EXISTS
    v_kpi_overview, v_data_quality,
    v_requests_by_hour, v_requests_by_weekday, v_requests_by_weekday_hour,
    v_busiest_hour_by_type,
    v_monthly_requests, v_requests_by_borough, v_open_requests_by_borough,
    v_top_complaint_types, v_top3_types_by_borough, v_top_zip_codes,
    v_requests
CASCADE;


-- =====================================================================
-- BASE VIEW
-- =====================================================================

-- v_requests: one row per request, with the names from the 3 other tables.
-- Business rule: resolution_time is only computed when the closing date
CREATE VIEW v_requests AS
SELECT
    sr.request_id,
    sr.created_date,
    sr.closed_date,
    DATE_TRUNC('month', sr.created_date) AS month,
    EXTRACT(HOUR FROM sr.created_date)   AS hour_of_day,
    EXTRACT(ISODOW FROM sr.created_date) AS weekday_number,   -- 1 = Monday ... 7 = Sunday
    sr.status,
    sr.channel,
    a.agency_code,
    a.agency_name,
    ct.complaint_type,
    ct.descriptor,
    l.borough,
    l.incident_zip,
    sr.latitude,
    sr.longitude,
    CASE WHEN sr.closed_date >= sr.created_date
         THEN sr.closed_date - sr.created_date
    END AS resolution_time
FROM service_request sr
JOIN agency a          ON sr.agency_code       = a.agency_code
JOIN complaint_type ct ON sr.complaint_type_id = ct.complaint_type_id
JOIN location l        ON sr.location_id       = l.location_id;


-- =====================================================================
-- OVERVIEW AND DATA QUALITY
-- =====================================================================

-- v_kpi_overview: the 4 main numbers for the top of the dashboard (one row)
CREATE VIEW v_kpi_overview AS
SELECT
    COUNT(*)                                     AS total_requests,
    COUNT(*) FILTER (WHERE status <> 'Closed')   AS open_requests,
    ROUND(100.0 * COUNT(*) FILTER (WHERE status = 'Closed') / COUNT(*), 1) AS closure_rate_pct,
    PERCENTILE_CONT(0.5) WITHIN GROUP (ORDER BY resolution_time)           AS median_resolution_time
FROM v_requests;

-- v_data_quality: number of requests affected by each data problem
CREATE VIEW v_data_quality AS
SELECT 'No due date' AS check_name, COUNT(*) AS rows_affected
FROM service_request WHERE due_date IS NULL
UNION ALL
SELECT 'No closed date', COUNT(*)
FROM service_request WHERE closed_date IS NULL
UNION ALL
SELECT 'Status Closed but no closed date', COUNT(*)
FROM service_request WHERE status = 'Closed' AND closed_date IS NULL
UNION ALL
SELECT 'Closed before created', COUNT(*)
FROM service_request WHERE closed_date < created_date
UNION ALL
SELECT 'No GPS coordinates', COUNT(*)
FROM service_request WHERE latitude IS NULL OR longitude IS NULL;


-- =====================================================================
-- WHEN do requests arrive?  (file 3.SQL_Analysis/when_requests_arrive.sql)
-- =====================================================================

CREATE VIEW v_requests_by_hour AS
SELECT
    EXTRACT(HOUR FROM created_date) AS hour_of_day,
    COUNT(*) AS requests,
    ROUND(100.0 * COUNT(*) / (SELECT COUNT(*) FROM service_request), 1) AS pct_of_requests
FROM service_request
GROUP BY EXTRACT(HOUR FROM created_date);

CREATE VIEW v_requests_by_weekday AS
SELECT
    EXTRACT(ISODOW FROM created_date) AS weekday_number,
    COUNT(*) AS requests,
    ROUND(100.0 * COUNT(*) / (SELECT COUNT(*) FROM service_request), 1) AS pct_of_requests
FROM service_request
GROUP BY EXTRACT(ISODOW FROM created_date);

-- for the heatmap (day of the week x hour)
CREATE VIEW v_requests_by_weekday_hour AS
SELECT
    EXTRACT(ISODOW FROM created_date) AS weekday_number,
    EXTRACT(HOUR FROM created_date)   AS hour_of_day,
    COUNT(*) AS requests
FROM service_request
GROUP BY EXTRACT(ISODOW FROM created_date), EXTRACT(HOUR FROM created_date);

CREATE VIEW v_busiest_hour_by_type AS
WITH ranked_type_hours AS (
    SELECT
        ct.complaint_type,
        EXTRACT(HOUR FROM sr.created_date) AS hour_of_day,
        COUNT(*) AS requests,
        DENSE_RANK() OVER (PARTITION BY ct.complaint_type ORDER BY COUNT(*) DESC) AS rank
    FROM service_request sr
    JOIN complaint_type ct ON sr.complaint_type_id = ct.complaint_type_id
    WHERE ct.complaint_type IN ('Illegal Parking', 'Noise - Residential', 'HEAT/HOT WATER',
                                'Blocked Driveway', 'Noise - Street/Sidewalk')
    GROUP BY ct.complaint_type, EXTRACT(HOUR FROM sr.created_date)
)
SELECT complaint_type, hour_of_day AS busiest_hour, requests
FROM ranked_type_hours
WHERE rank = 1;


-- =====================================================================
-- WHAT and WHERE  (file 3.SQL_Analysis/demand_and_geography.sql)
-- =====================================================================

CREATE VIEW v_monthly_requests AS
WITH monthly_counts AS (
    SELECT DATE_TRUNC('month', created_date) AS month,
           COUNT(*) AS total_requests
    FROM service_request
    GROUP BY DATE_TRUNC('month', created_date)
)
SELECT month,
       total_requests,
       total_requests - LAG(total_requests) OVER (ORDER BY month) AS net_change
FROM monthly_counts;

CREATE VIEW v_requests_by_borough AS
SELECT l.borough,
       COUNT(*) AS total_requests,
       ROUND(100.0 * COUNT(*) / (SELECT COUNT(*) FROM service_request), 2) AS request_pct
FROM service_request sr
JOIN location l ON sr.location_id = l.location_id
GROUP BY l.borough;

CREATE VIEW v_open_requests_by_borough AS
SELECT l.borough,
       COUNT(*) AS total_requests,
       COUNT(*) FILTER (WHERE sr.status <> 'Closed') AS open_requests,
       ROUND(100.0 * COUNT(*) FILTER (WHERE sr.status <> 'Closed') / COUNT(*), 2) AS open_rate_pct
FROM service_request sr
JOIN location l ON sr.location_id = l.location_id
WHERE l.borough <> 'Unspecified'
GROUP BY l.borough;

CREATE VIEW v_top_complaint_types AS
SELECT ct.complaint_type,
       COUNT(*) AS request_count
FROM service_request sr
JOIN complaint_type ct ON sr.complaint_type_id = ct.complaint_type_id
GROUP BY ct.complaint_type
ORDER BY request_count DESC
LIMIT 10;

CREATE VIEW v_top3_types_by_borough AS
WITH ranked_borough_complaints AS (
    SELECT l.borough,
           ct.complaint_type,
           COUNT(*) AS requests,
           DENSE_RANK() OVER (PARTITION BY l.borough ORDER BY COUNT(*) DESC) AS rank
    FROM service_request sr
    JOIN location l        ON sr.location_id       = l.location_id
    JOIN complaint_type ct ON sr.complaint_type_id = ct.complaint_type_id
    WHERE l.borough <> 'Unspecified'
    GROUP BY l.borough, ct.complaint_type
)
SELECT borough, rank, complaint_type, requests
FROM ranked_borough_complaints
WHERE rank <= 3;

CREATE VIEW v_top_zip_codes AS
SELECT l.incident_zip,
       l.borough,
       COUNT(*) AS request_count
FROM service_request sr
JOIN location l ON sr.location_id = l.location_id
WHERE l.incident_zip <> 'Unknown'
GROUP BY l.incident_zip, l.borough
ORDER BY request_count DESC
LIMIT 10;


-- =====================================================================
-- Not completed..
-- =====================================================================


-- list all the views
SELECT table_name AS view_name
FROM information_schema.views
WHERE table_schema = 'public'
ORDER BY table_name;
