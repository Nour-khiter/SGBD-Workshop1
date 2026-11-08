-- Member 4 | Query 1: typical time to solve a request, per complaint type
-- Rule: only closed requests with closed_date >= created_date
-- Typical time = median (not average), in hours and days
-- Reliability: types with few closed requests are not reliable (use nb_closed >= 30 in Power BI)

SELECT ct.complaint_type,
       COUNT(*) AS nb_closed,
       ROUND(CAST(PERCENTILE_CONT(0.5) WITHIN GROUP (
         ORDER BY EXTRACT(EPOCH FROM (sr.closed_date - sr.created_date))/3600
       ) AS NUMERIC), 1) AS median_hours,
       ROUND(CAST(PERCENTILE_CONT(0.5) WITHIN GROUP (
         ORDER BY EXTRACT(EPOCH FROM (sr.closed_date - sr.created_date))/86400
       ) AS NUMERIC), 1) AS median_days
FROM service_request sr
JOIN complaint_type ct ON ct.complaint_type_id = sr.complaint_type_id
WHERE sr.closed_date IS NOT NULL
  AND sr.closed_date >= sr.created_date
GROUP BY ct.complaint_type
ORDER BY median_hours DESC;