"""
Step 4 - Look at the sample before loading it.

Run it from the project folder:
    python 02_check_sample.py
"""

import pandas as pd

df = pd.read_csv("data/raw_311_2024_sample.csv", dtype=str)

print("1) Size")
print(f"   {len(df)} rows, {len(df.columns)} columns\n")

created = pd.to_datetime(df["created_date"], errors="coerce")

print("2) Rows per month (similar sizes, busier months a bit higher)")
print(created.dt.month.value_counts().sort_index().to_string(), "\n")

print("3) Rows per hour of the day (should be busiest in the daytime)")
print(created.dt.hour.value_counts().sort_index().to_string(), "\n")

print("4) Rows per borough")
print(df["borough"].value_counts(dropna=False).to_string(), "\n")

print("5) Top 10 complaint types")
print(df["complaint_type"].value_counts().head(10).to_string(), "\n")

print("6) Missing values per column (%)")
print((df.isna().mean() * 100).round(1).to_string(), "\n")

closed = pd.to_datetime(df["closed_date"], errors="coerce")
impossible = (closed < created).sum()
print(f"7) Requests closed BEFORE they were created: {impossible}  (a data-quality issue to report)")
