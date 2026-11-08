-- Member 4 | Query 2: typical solving time and number of requests, per agency
-- nb_requests = all requests of the agency
-- nb_closed_valid and the median = only closed requests with closed_date >= created_date
-- Typical time = median (not average)

SELECT a.agency_code,
       a.agency_name,
       COUNT(*) AS nb_requests,
       COUNT(*) FILTER (WHERE sr.closed_date IS NOT NULL
                        AND sr.closed_date >= sr.created_date) AS nb_closed_valid,
       ROUND(CAST(PERCENTILE_CONT(0.5) WITHIN GROUP (
         ORDER BY EXTRACT(EPOCH FROM (sr.closed_date - sr.created_date))/3600
       ) FILTER (WHERE sr.closed_date IS NOT NULL
                 AND sr.closed_date >= sr.created_date) AS NUMERIC), 1) AS median_hours,
       ROUND(CAST(PERCENTILE_CONT(0.5) WITHIN GROUP (
         ORDER BY EXTRACT(EPOCH FROM (sr.closed_date - sr.created_date))/86400
       ) FILTER (WHERE sr.closed_date IS NOT NULL
                 AND sr.closed_date >= sr.created_date) AS NUMERIC), 1) AS median_days
FROM service_request sr
JOIN agency a ON a.agency_code = sr.agency_code
GROUP BY a.agency_code, a.agency_name
ORDER BY median_hours DESC;


-- Member 4 | Query 3: number of open and closed requests, per agency
-- Open = status <> 'Closed' (team rule), closed = status = 'Closed'
-- pct_open = share of the agency's requests that are still open

SELECT a.agency_code,
       a.agency_name,
       COUNT(*) AS nb_requests,
       COUNT(*) FILTER (WHERE sr.status <> 'Closed') AS open_requests,
       COUNT(*) FILTER (WHERE sr.status = 'Closed')  AS closed_requests,
       ROUND(100.0 * COUNT(*) FILTER (WHERE sr.status <> 'Closed') / COUNT(*), 1) AS pct_open
FROM service_request sr
JOIN agency a ON a.agency_code = sr.agency_code
GROUP BY a.agency_code, a.agency_name
ORDER BY open_requests DESC;



-- Member 4 | Query 4: % of requests solved within 24 hours and within 7 days, per agency
-- Denominator = closed requests with a valid closing date (closed_date >= created_date)
-- Open requests and requests without a usable closing date are not in the percentage
-- nb_closed_valid is shown so the reader knows how reliable each percentage is

SELECT a.agency_code,
       a.agency_name,
       COUNT(*) AS nb_requests,
       COUNT(*) FILTER (WHERE sr.closed_date IS NOT NULL
                        AND sr.closed_date >= sr.created_date) AS nb_closed_valid,
       ROUND(100.0 * COUNT(*) FILTER (WHERE sr.closed_date >= sr.created_date
                        AND sr.closed_date - sr.created_date <= INTERVAL '24 hours')
             / NULLIF(COUNT(*) FILTER (WHERE sr.closed_date IS NOT NULL
                        AND sr.closed_date >= sr.created_date), 0), 1) AS pct_24h,
       ROUND(100.0 * COUNT(*) FILTER (WHERE sr.closed_date >= sr.created_date
                        AND sr.closed_date - sr.created_date <= INTERVAL '7 days')
             / NULLIF(COUNT(*) FILTER (WHERE sr.closed_date IS NOT NULL
                        AND sr.closed_date >= sr.created_date), 0), 1) AS pct_7d
FROM service_request sr
JOIN agency a ON a.agency_code = sr.agency_code
GROUP BY a.agency_code, a.agency_name
ORDER BY pct_24h DESC;

-- Check query (Member 4): why do some Closed requests have no usable closing date?
-- Shows, per agency, Closed requests with an empty closing date or a closing date before creation

SELECT sr.agency_code,
       COUNT(*) FILTER (WHERE sr.closed_date IS NULL) AS closed_without_date,
       COUNT(*) FILTER (WHERE sr.closed_date < sr.created_date) AS closed_before_created
FROM service_request sr
WHERE sr.status = 'Closed'
GROUP BY sr.agency_code
HAVING COUNT(*) FILTER (WHERE sr.closed_date IS NULL OR sr.closed_date < sr.created_date) > 0
ORDER BY closed_without_date DESC;