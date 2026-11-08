"""
Step 3 - Download a RANDOM sample of NYC 311 requests for 2024  (version 2)

Why version 2:
  Version 1 took the first 125 requests of each day, so most rows were
  created just after midnight (hours 0-1). That sample was biased.

How this version samples:
  311 request numbers (unique_key) are given one after another, so their last
  digits have nothing to do with the time, place or type of the request.
  For every day of 2024 we keep only the requests whose number ends in a few
  chosen digits (about 2% of all requests). Then we draw exactly 45,750 rows
  at random from them, with a fixed seed so the whole team gets the same rows.
  Busy days, hours and boroughs keep their real share of the data.

RESUMABLE: each day is saved in data/days_v2/ as soon as it is downloaded.
If the script stops or some days fail, run it again: it only downloads the
missing days.

Run it from the project folder:
    python 01_download_311.py

Result: data/raw_311_2024_sample.csv  (replaces the biased version 1 file)
"""

import datetime as dt
import json
import os
import time

import pandas as pd
import requests

URL = "https://data.cityofnewyork.us/resource/erm2-nwe9.json"
YEAR = 2024
SAMPLE_SIZE = 45750      # final number of rows (workshop limit: 5,000-50,000)
SEED = 42                # same seed = same random rows for everyone
DAYS_DIR = os.path.join("data", "days_v2")
OUTPUT = os.path.join("data", "raw_311_2024_sample.csv")

MAX_ATTEMPTS = 6         # tries per day before giving up (for this run)
TIMEOUT = 120            # seconds to wait for the server to answer
PAGE = 1000              # rows per request

# Optional: a free "app token" from NYC Open Data makes the server slow you down less.
APP_TOKEN = ""

# Keep requests whose number ends in 07 or 57 (2 endings out of 100 = 2%).
# Two ways to write the same filter: one for a number column, one for a text column.
# The script finds out which one the server accepts.
KEY_FILTERS = [
    "unique_key % 50 = 7",
    "(unique_key like '%07' OR unique_key like '%57')",
]

COLUMNS = [
    "unique_key", "created_date", "closed_date", "due_date",
    "agency", "agency_name", "complaint_type", "descriptor",
    "status", "resolution_description",
    "incident_zip", "borough", "latitude", "longitude",
    "open_data_channel_type",
]

HEADERS = {"X-App-Token": APP_TOKEN} if APP_TOKEN else {}


def day_file(day: dt.date) -> str:
    return os.path.join(DAYS_DIR, f"{day}.json")


def get(params):
    """One call to the API. Returns (rows, error)."""
    try:
        response = requests.get(URL, params=params, headers=HEADERS, timeout=TIMEOUT)
        if response.status_code == 400:
            return None, "bad-filter"
        response.raise_for_status()
        return response.json(), None
    except requests.RequestException as error:
        return None, type(error).__name__


def find_key_filter() -> str:
    """Try each way of writing the filter on one day; keep the one that works."""
    for key_filter in KEY_FILTERS:
        params = {
            "$where": f"created_date >= '2024-01-02T00:00:00' AND "
                      f"created_date < '2024-01-03T00:00:00' AND {key_filter}",
            "$limit": 5,
        }
        for attempt in range(1, MAX_ATTEMPTS + 1):
            rows, error = get(params)
            if error is None:
                print(f"Using filter: {key_filter}")
                return key_filter
            if error == "bad-filter":
                break  # this way of writing it is not accepted; try the next one
            print(f"   testing the filter: attempt {attempt} failed ({error}), waiting...")
            time.sleep(min(10 * attempt, 60))
    raise SystemExit("Could not reach the NYC server or no filter worked. "
                     "Try again later and send the message above to Claude.")


def fetch_day(day: dt.date, key_filter: str):
    """All requests of one day whose number ends in the chosen digits.
    Returns the list of rows, or None if it failed."""
    next_day = day + dt.timedelta(days=1)
    where = (f"created_date >= '{day}T00:00:00' AND "
             f"created_date < '{next_day}T00:00:00' AND {key_filter}")
    rows = []
    offset = 0
    while True:
        params = {"$where": where, "$order": "unique_key",
                  "$limit": PAGE, "$offset": offset}
        for attempt in range(1, MAX_ATTEMPTS + 1):
            page, error = get(params)
            if error is None:
                break
            wait = min(10 * attempt, 60)
            print(f"   {day}: attempt {attempt}/{MAX_ATTEMPTS} failed ({error}), waiting {wait}s...")
            time.sleep(wait)
        else:
            return None
        rows.extend(page)
        if len(page) < PAGE:
            return rows
        offset += PAGE


def main():
    os.makedirs(DAYS_DIR, exist_ok=True)

    all_days = []
    day = dt.date(YEAR, 1, 1)
    while day.year == YEAR:
        all_days.append(day)
        day += dt.timedelta(days=1)

    todo = [d for d in all_days if not os.path.exists(day_file(d))]
    failed = []
    if todo:
        key_filter = find_key_filter()
        for day in todo:
            if day.day == 1 or day == todo[0]:
                print(f"{day:%B}: downloading...")
            rows = fetch_day(day, key_filter)
            if rows is None:
                print(f"   {day}: skipped for now (run the script again later to retry it)")
                failed.append(day)
                continue
            with open(day_file(day), "w", encoding="utf-8") as f:
                json.dump(rows, f)
            time.sleep(0.5)

    have = [d for d in all_days if os.path.exists(day_file(d))]
    print(f"\nDays downloaded: {len(have)} / {len(all_days)}")
    if failed:
        print(f"Missing days: {len(failed)}. Run 'python 01_download_311.py' again "
              "to download only those.")
        return

    all_rows = []
    for d in have:
        with open(day_file(d), encoding="utf-8") as f:
            all_rows.extend(json.load(f))

    df = pd.DataFrame(all_rows)
    missing = [c for c in COLUMNS if c not in df.columns]
    if missing:
        print(f"Warning: these columns were not in the data and will be empty: {missing}")
    df = df.reindex(columns=COLUMNS).drop_duplicates(subset="unique_key")
    print(f"Requests kept by the filter: {len(df)}")

    if len(df) > SAMPLE_SIZE:
        df = df.sample(n=SAMPLE_SIZE, random_state=SEED)
    df = df.sort_values("created_date")

    df.to_csv(OUTPUT, index=False)
    print(f"Done: {len(df)} rows saved to {OUTPUT}")


if __name__ == "__main__":
    main()
