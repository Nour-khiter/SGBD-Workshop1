DROP TABLE IF EXISTS service_request, agency, complaint_type, location CASCADE;

-- ---------- who handles the request ----------
CREATE TABLE agency (
    agency_code  VARCHAR(20) PRIMARY KEY,      
    agency_name  TEXT NOT NULL
);

-- ---------- what the problem is ----------
CREATE TABLE complaint_type (
    complaint_type_id  SERIAL PRIMARY KEY,     
    complaint_type     TEXT NOT NULL,          
    descriptor         TEXT NOT NULL,         
    UNIQUE (complaint_type, descriptor)
);

-- ---------- where it happened ----------
CREATE TABLE location (
    location_id   SERIAL PRIMARY KEY,
    incident_zip  VARCHAR(10) NOT NULL,
    borough       VARCHAR(20) NOT NULL,
    UNIQUE (incident_zip, borough)
);

-- ---------- service request ----------
CREATE TABLE service_request (
    request_id              BIGINT PRIMARY KEY,          
    created_date            TIMESTAMP NOT NULL,
    closed_date             TIMESTAMP,
    due_date                TIMESTAMP,
    status                  VARCHAR(30),
    channel                 VARCHAR(20),                 
    resolution_description  TEXT,
    latitude                NUMERIC(9,6),
    longitude               NUMERIC(9,6),
    agency_code             VARCHAR(20) NOT NULL REFERENCES agency (agency_code),
    complaint_type_id       INT NOT NULL REFERENCES complaint_type (complaint_type_id),
    location_id             INT NOT NULL REFERENCES location (location_id)
);


INSERT INTO agency (agency_code, agency_name)
SELECT DISTINCT ON (agency) agency, COALESCE(agency_name, agency)
FROM staging_311
WHERE agency IS NOT NULL
ORDER BY agency, agency_name;

INSERT INTO complaint_type (complaint_type, descriptor)
SELECT DISTINCT complaint_type, COALESCE(descriptor, 'Unspecified')
FROM staging_311
WHERE complaint_type IS NOT NULL;

INSERT INTO location (incident_zip, borough)
SELECT DISTINCT COALESCE(incident_zip, 'Unknown'), COALESCE(borough, 'Unspecified')
FROM staging_311;

-- ===============================
-- Fill the service request table
-- ===============================

INSERT INTO service_request (
    request_id, created_date, closed_date, due_date, status, channel,
    resolution_description, latitude, longitude,
    agency_code, complaint_type_id, location_id
)
SELECT
    s.unique_key::BIGINT,
    s.created_date::TIMESTAMP,
    s.closed_date::TIMESTAMP,
    s.due_date::TIMESTAMP,
    s.status,
    s.open_data_channel_type,
    s.resolution_description,
    s.latitude::NUMERIC,
    s.longitude::NUMERIC,
    s.agency,
    ct.complaint_type_id,
    l.location_id
FROM staging_311 s
JOIN complaint_type ct
  ON ct.complaint_type = s.complaint_type
 AND ct.descriptor     = COALESCE(s.descriptor, 'Unspecified')
JOIN location l
  ON l.incident_zip = COALESCE(s.incident_zip, 'Unknown')
 AND l.borough      = COALESCE(s.borough, 'Unspecified')
WHERE s.agency IS NOT NULL
ON CONFLICT (request_id) DO NOTHING;

-- =====================================================================
-- Indexes on the columns we filter and join on most
-- =====================================================================

CREATE INDEX idx_sr_created   ON service_request (created_date);
CREATE INDEX idx_sr_agency    ON service_request (agency_code);
CREATE INDEX idx_sr_complaint ON service_request (complaint_type_id);
CREATE INDEX idx_sr_location  ON service_request (location_id);

-- =====================================================================
-- Check: how many rows in each table?
-- =====================================================================

SELECT 'staging_311'     AS table_name, COUNT(*) AS row_count FROM staging_311
UNION ALL SELECT 'agency',          COUNT(*) FROM agency
UNION ALL SELECT 'complaint_type',  COUNT(*) FROM complaint_type
UNION ALL SELECT 'location',        COUNT(*) FROM location
UNION ALL SELECT 'service_request', COUNT(*) FROM service_request;
