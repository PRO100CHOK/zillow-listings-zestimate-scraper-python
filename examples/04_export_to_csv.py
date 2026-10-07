"""Sold homes in the last 6 months to CSV, with $/sqft by home type in pandas.

`listingType: sold` plus `daysOnZillow: "6m"` returns recent sales; `flatOutput`
flattens nested fields so the dataset drops cleanly into a DataFrame.

Actor: https://apify.com/pro100chok/zillow-scraper-all-in-one?utm_source=github_pro100&utm_medium=readme&utm_campaign=zillow-listings-zestimate-scraper-python
"""
import os

import pandas as pd
from apify_client import ApifyClient
from dotenv import load_dotenv

load_dotenv()
client = ApifyClient(os.environ["APIFY_API_TOKEN"])

run = client.actor("pro100chok/zillow-scraper-all-in-one").call(run_input={
    "mode": "search",
    "locations": ["Boise, ID"],
    "listingType": "sold",
    "daysOnZillow": "6m",
    "sqftMin": 900,
    "flatOutput": True,
    "maxItems": 300,
})

df = pd.DataFrame(client.dataset(run["defaultDatasetId"]).list_items().items)
if df.empty:
    raise SystemExit("No sold homes returned.")

df["soldPrice"] = df["listingSoldPrice"].fillna(df["price"]) if "listingSoldPrice" in df else df["price"]
df = df[df["soldPrice"].notna() & df["area"].notna()]
df["pricePerSqft"] = (df["soldPrice"] / df["area"]).round(0)

cols = ["address", "zipcode", "homeType", "soldPrice", "dateSold", "beds", "baths",
        "area", "pricePerSqft", "zestimate", "url"]
df[[c for c in cols if c in df.columns]].to_csv("output.csv", index=False)
df.to_json("output.json", orient="records", indent=2)

print(f"{len(df)} sales saved to output.csv\n")
print(df.groupby("homeType")["pricePerSqft"].describe()[["count", "50%", "min", "max"]])
