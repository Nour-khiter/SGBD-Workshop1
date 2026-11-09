# Open the CivicPulse dashboard on another computer

This folder contains the editable **Power BI Project** (PBIP). The project is `Dashboard.pbip`; its report and semantic model are the adjacent `Dashboard.Report` and `Dashboard.SemanticModel` folders. Keep them together and preserve their relative paths.

> **This dashboard currently connects to PostgreSQL on `localhost`, database `nyc311`.** On another computer, `localhost` means that computer. The recipient must either recreate the database there or update the model's PostgreSQL server setting to point to an accessible shared database.

## What to copy

For a complete handoff, copy the whole project repository, including:

- `4.Dashboard/` (the PBIP file, report folder, semantic-model folder, and this README)
- `1.Data/Raw_data/raw_311_2024_sample.csv`
- `1.Data/load_staging.py`
- `2.Databse/schema.sql` and `2.Databse/views.sql`


## Requirements

- Power BI Desktop on Windows
- PostgreSQL running locally, with port `5432` available
- Python 3 and internet access to install the Python packages below
- The CivicPulse sample CSV and the SQL scripts listed above

## 1. Create and load the PostgreSQL database

1. Install/start PostgreSQL and create an empty database named `nyc311` (for example, in pgAdmin: **Databases → Create → Database**).
2. Open PowerShell in the repository's `1.Data` folder and install the CSV-loader requirements:

   ```powershell
   py -m pip install -r requirements.txt
   ```

   **Note:** `requirements.txt` lists the Python packages used by the data loader.

3. Run the staging loader:

   ```powershell
   py load_staging.py
   ```

   Enter the password for the PostgreSQL user `postgres` when prompted. The script loads the CSV into `staging_311` in the `nyc311` database.

4. In pgAdmin, open the Query Tool connected to `nyc311` and run `2.Databse/schema.sql`. This creates and populates the four core tables: `service_request`, `agency`, `complaint_type`, and `location`.
5. Run `2.Databse/views.sql` in the same database. These views provide the dashboard's prepared metrics and categories.

**Important:** `schema.sql` drops and rebuilds the four core tables, and `views.sql` drops and recreates the analysis views. Run these setup scripts only on the project database; back up any data you need before rerunning them.

## 2. Open the PBIP project

1. Start Power BI Desktop.
2. In Power BI Desktop, choose **File → Open report** and open `4.Dashboard/Dashboard.pbip`.
3. If Power BI asks for PostgreSQL credentials, choose **Database** authentication and enter the credentials for the local PostgreSQL instance. The model expects server `localhost` and database `nyc311`.
4. Select **Home → Refresh** and wait for the model refresh to finish. If Power BI reports missing or incomplete table data, confirm PostgreSQL is running, the database name and credentials are correct, and that both SQL scripts completed successfully.
5. Navigate through **Overview**, **Geography**, and **Performance** and check the visuals after refresh.

## 3. Use a PostgreSQL server on another host

If the database is hosted on a different computer or server, the recipient must have network access and database permissions. Update each PostgreSQL source in the Power Query partitions under `Dashboard.SemanticModel/definition/tables/`: replace `PostgreSQL.Database("localhost", "nyc311")` with the correct server and database, then reopen or refresh the PBIP project and enter that server's credentials. Do not put a password in the project files.

## Troubleshooting

- **Connection refused / server not found:** Start PostgreSQL and verify the host, port, database, firewall, and username.
- **Password prompt repeats:** Check the PostgreSQL credentials and remove any stale saved credentials in Power BI Desktop's data-source settings before reconnecting.
- **Tables or visuals are blank:** Refresh after confirming that `staging_311`, all four core tables, and the views exist in `nyc311`.
- **Map background is blank:** The Azure Maps visual needs internet access to load map tiles; borough charts and tables remain available without the tiles.
- **Performance visuals:** The PBIR definitions use Median aggregation for resolution charts and a built-in clustered bar visual for open/closed workload. Check their rendering in Desktop after refresh, especially if the report was opened with an older Desktop build.

## Data interpretation

This is a **2% sample of 2024 requests**. Compare shares, rates, and rankings rather than treating the sample counts as New York City's total request volume. Resolution-time metrics exclude records with a missing closing date or a closing date earlier than creation. The Performance page also flags incomplete or small samples, including DHS, OTI, and DOE.
