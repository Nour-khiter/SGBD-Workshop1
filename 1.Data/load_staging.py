"""
Copy the CSV into PostgreSQL as a "staging" table.

Before running:
  - PostgreSQL is running
  - you created an empty database called nyc311 

"""

import getpass

import pandas as pd
from sqlalchemy import create_engine, text
from sqlalchemy.types import Text

DB_USER = "postgres"
DB_HOST = "localhost"
DB_PORT = 5432
DB_NAME = "nyc311"

password = getpass.getpass(f"PostgreSQL password for user '{DB_USER}': ")
engine = create_engine(
    f"postgresql+psycopg2://{DB_USER}:{password}@{DB_HOST}:{DB_PORT}/{DB_NAME}"
)

df = pd.read_csv("Raw_data/raw_311_2024_sample.csv", dtype=str)

# Every column as TEXT, so nothing is lost or converted wrongly at this stage
df.to_sql(
    "staging_311",
    engine,
    if_exists="replace",
    index=False,
    dtype={column: Text() for column in df.columns},
)

with engine.connect() as conn:
    count = conn.execute(text("SELECT COUNT(*) FROM staging_311")).scalar()
print(f"Done: staging_311 has {count} rows")
