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