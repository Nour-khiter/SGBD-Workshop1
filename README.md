# CivicPulse — NYC 311 Decision-Support Portal

Workshop #01 — Applied Data Analytics & Decision Support: From SQL to Insight (Advanced Database Systems, ESI 2026).

CivicPulse helps New York City's managers decide **what** public-service problems to fix first, **where** to send their teams, **when** to add staff, and **how fast** each agency responds. It is built on real NYC 311 service requests, a PostgreSQL database, analytical SQL queries and a Power BI dashboard.

---

## 1. Project structure

```
.
├── README.md                          this file
├── 1.Data/
│   ├── Raw_data/                      the data: raw_311_2024_sample.csv (45,750 requests, 2024)
│   ├── 01_download_311.py             downloads the 2024 sample from NYC Open Data (optional)
│   ├── 02_check_sample.py             checks the sample (months, hours, boroughs, missing values)
│   ├── load_staging.py                copies the CSV into PostgreSQL (table staging_311)
│   ├── requirements.txt               Python dependencies
│   ├── Data Dictionary.pdf            meaning of every table, column and view
│   └── Data Quality Report.pdf        data problems found and how they are handled
├── 2.Databse/
│   ├── schema.sql                     creates and fills the 4 tables
│   ├── views.sql                      the 17 views used by the Power BI dashboard
│   ├── data_quality_checks.sql        data-quality checks in the database
│   ├── ERD.png                        database diagram
│   └── architecture.png               architecture of the solution
├── 3.SQL_Analysis/
│   ├── demand_and_geography.sql       WHAT and WHERE (7 queries)
│   ├── when_requests_arrive.sql       WHEN (4 queries)
│   ├── 03_resolution_analysis.sql     HOW FAST, per complaint type (1 query)
│   ├── 04_agency_analysis.sql         HOW FAST, per agency (3 queries + 1 check)
│   ├── demand & geography/            results of the demand and geography queries
│   └── When requests arrive/          results of the timing queries
├── 4.Dashboard/
│   ├── Dashboard.pbip                 the Power BI dashboard (open this file)
│   ├── Dashboard.Report/              report pages (Power BI project files)
│   ├── Dashboard.SemanticModel/       data model and connection (Power BI project files)
│   ├── Screenshots/                   screenshots of the 3 pages
│   ├── build_pbir.py                  script used to generate the report files
│   └── README.md                      details of the dashboard
├── 5.AI_comparaison/                  prompt, AI-generated dashboard (HTML + screenshots), comparison
└── 6.Presentation/                    executive presentation (PDF / PPTX)
```

---

## 2. Data source

| Item | Value |
|---|---|
| Dataset | NYC Open Data — *311 Service Requests from 2020 to Present* (`erm2-nwe9`) |
| Period | 1 January – 31 December 2024 |
| Size | 45,750 requests (workshop limit: 5,000–50,000 rows) |

**Sampling.** For every day of 2024, `01_download_311.py` keeps the requests whose number (`unique_key`) ends in 07 or 57 (about 2% of each day, spread over all hours), then draws 45,750 of them at random with a fixed seed (42), so the sample is identical for everyone. Results are reported as shares, rankings and medians, not as the city's total volumes.

The CSV is already included in `1.Data/Raw_data/`: **you do not need to download the data again.**

---

## 3. Requirements

| Tool | Version |
|---|---|
| PostgreSQL + pgAdmin 4 | PostgreSQL 14 or later |
| Python | 3.9 or later |
| Power BI Desktop (Windows, free) | a recent version that opens `.pbip` projects |

Python libraries (`1.Data/requirements.txt`): pandas, requests, sqlalchemy, psycopg2-binary. Install them from the project root:

```
pip install -r 1.Data/requirements.txt
```

---

## 4. Set up and configure the database

1. **Create an empty database.** In pgAdmin: *Servers → PostgreSQL → right-click Databases → Create → Database…*, name it `nyc311`, then *Save*.

2. **Load the CSV into PostgreSQL.** In a terminal:
   ```
   cd 1.Data
   python load_staging.py
   ```
   Enter your PostgreSQL password when asked (user `postgres`, host `localhost`, port `5432`; change them at the top of the script if yours differ).
   Expected: `Done: staging_311 has 45750 rows`.

3. **Create and fill the 4 tables.** In pgAdmin, click `nyc311` → *Tools → Query Tool*, open `2.Databse/schema.sql` and press **F5**.
   Expected: a summary table ending with `service_request | 45750`.

4. **Create the views for the dashboard.** In the Query Tool, open `2.Databse/views.sql` and press **F5**.
   Expected: the list of the 17 views.

5. **Check the data quality (optional).** Open `2.Databse/data_quality_checks.sql`, select one query, press **F5**.
   Expected: 45,750 rows in the CSV, 45,750 in the database, 0 lost.

### Database design

One table of requests linked by foreign keys to three descriptive tables (see `2.Databse/ERD.png`).

| Table | Rows | One row = | Key |
|---|---|---|---|
| `service_request` | 45,750 | one 311 request | `request_id` (PK); `agency_code`, `complaint_type_id`, `location_id` (FK) |
| `agency` | 14 | one agency | `agency_code` (PK) |
| `complaint_type` | 709 | one complaint type + detail | `complaint_type_id` (PK) |
| `location` | 222 | one ZIP code + borough | `location_id` (PK) |

---

## 5. Execute the SQL analysis

Open each file of `3.SQL_Analysis/` in the pgAdmin Query Tool (database `nyc311`), **select one query**, and press **F5**. Each query starts with a comment explaining the question it answers.

| File | Question |
|---|---|
| `demand_and_geography.sql` | What are the main problems, and where do they happen? |
| `when_requests_arrive.sql` | When do requests arrive (hours, days, periods)? |
| `03_resolution_analysis.sql` | How fast is each type of problem solved? |
| `04_agency_analysis.sql` | How fast does each agency solve requests, and how many are still open? |

**Rules used in all queries and views**

| Indicator | Definition |
|---|---|
| Open request | `status <> 'Closed'` |
| Resolution time | `closed_date - created_date`, only when `closed_date` exists and is not before `created_date` |
| Typical resolution time | the median (`PERCENTILE_CONT(0.5)`), shown in hours and days |
| % solved within 24 h / 7 days | requests solved within the limit ÷ requests with a valid closing date (`nb_closed_valid`) |
| Excluded | borough `Unspecified` (borough comparisons), ZIP `Unknown` (ZIP ranking); `due_date` is not used (99.5% empty) |

**Known data limit:** all 331 requests marked `Closed` without a closing date belong to DHS, so DHS resolution times cover only 354 of its 685 requests (see the Data Quality Report).

---

## 6. Run the dashboard

1. Make sure steps 4.1 to 4.4 are done (the 17 views must exist).
2. Open `4.Dashboard/Dashboard.pbip` in Power BI Desktop.
3. If Power BI asks for the data source, or shows an error: *Home → Transform data → Data source settings*, select the PostgreSQL source, and set **server** `localhost`, **database** `nyc311`; then enter user `postgres` and your password (*Edit Permissions → Edit*).
4. Click **Refresh**. The 3 pages (Overview, Geography, Performance) load from the views of `views.sql`.

More details: `4.Dashboard/README.md`.

---

## 7. Reproduce the whole solution

From an empty PostgreSQL server:

1. `pip install -r 1.Data/requirements.txt`
2. Create the database `nyc311` (section 4, step 1)
3. `cd 1.Data` then `python load_staging.py`
4. Run `2.Databse/schema.sql`, then `2.Databse/views.sql`
5. Run the queries of `3.SQL_Analysis/`
6. Open and refresh `4.Dashboard/Dashboard.pbip` (section 6)

**Check:** the most common complaint type must be *Illegal Parking* with 6,700 requests.

*(Optional)* To rebuild the sample from the source: `cd 1.Data` then `python 01_download_311.py` (5–30 minutes, depending on the NYC server; resumable if interrupted) and `python 02_check_sample.py`.
