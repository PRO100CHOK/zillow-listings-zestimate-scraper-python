"""Price-cut watchlist in a Google Sheet.

Setup:
  1. Google Cloud console -> create a service account -> download its JSON key.
  2. Save it as service_account.json next to this file (it is gitignored).
  3. Share your spreadsheet with the service account's email address.

Each run pulls homes with a recent price reduction (`priceReducedOnly`) in the
markets below and appends them with the cut amount and the Zestimate, so a
weekly schedule turns the sheet into a motivated-seller list.

Actor: https://apify.com/pro100chok/zillow-scraper-all-in-one?utm_source=github_pro100&utm_medium=readme&utm_campaign=zillow-listings-zestimate-scraper-python
"""
import os
from datetime import datetime, timezone

import gspread
from apify_client import ApifyClient
from dotenv import load_dotenv
from google.oauth2.service_account import Credentials

SPREADSHEET = "Zillow price cuts"
WORKSHEET = "watchlist"
MARKETS = ["Orlando, FL", "Kissimmee, FL"]
SCOPES = ["https://www.googleapis.com/auth/spreadsheets"]
HEADER = ["collected_at", "zpid", "address", "price", "price_cut", "cut_date",
          "zestimate", "beds", "baths", "sqft", "days_on_zillow", "broker", "url"]

load_dotenv()
client = ApifyClient(os.environ["APIFY_API_TOKEN"])

run = client.actor("pro100chok/zillow-scraper-all-in-one").call(run_input={
    "mode": "search",
    "locations": MARKETS,
    "listingType": "forSale",
    "priceReducedOnly": True,
    "sort": "priceReduced",
    "priceMax": 550000,
    "maxItems": 250,
})

stamp = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M")
rows = [[stamp, h.get("zpid"), h.get("address"), h.get("price"),
         h.get("priceReduction") or h.get("priceChange"), h.get("priceChangeDate"),
         h.get("zestimate"), h.get("beds"), h.get("baths"), h.get("area"),
         h.get("daysOnZillow"), h.get("brokerName"), h.get("url")]
        for h in client.dataset(run["defaultDatasetId"]).iterate_items()]

creds = Credentials.from_service_account_file("service_account.json", scopes=SCOPES)
book = gspread.authorize(creds).open(SPREADSHEET)
try:
    ws = book.worksheet(WORKSHEET)
except gspread.WorksheetNotFound:
    ws = book.add_worksheet(WORKSHEET, rows=20000, cols=len(HEADER))
    ws.append_row(HEADER)

if rows:
    ws.append_rows(rows, value_input_option="USER_ENTERED")
print(f"Appended {len(rows)} price-reduced homes to {SPREADSHEET}/{WORKSHEET}")
