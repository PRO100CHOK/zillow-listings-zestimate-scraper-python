"""Bulk Zestimate lookup from plain street addresses.

Zestimate mode accepts addresses, ZPIDs or homedetails URLs in
`zestimateItems` and returns the value, its dollar range, the 30-day change and
the Rent Zestimate - useful for valuing a portfolio or a lead list of owners.

Actor: https://apify.com/pro100chok/zillow-scraper-all-in-one?utm_source=github_pro100&utm_medium=readme&utm_campaign=zillow-listings-zestimate-scraper-python
"""
import os

from apify_client import ApifyClient
from dotenv import load_dotenv

# One home per line. Formats can be mixed: a street address, a bare ZPID such
# as "48749425", or a full https://www.zillow.com/homedetails/..._zpid/ URL.
PORTFOLIO = [
    "2114 Bigelow Ave N, Seattle, WA 98109",
    "1517 Lafayette Ave, Saint Louis, MO 63104",
    "4012 Avenue G, Austin, TX 78751",
]

load_dotenv()
client = ApifyClient(os.environ["APIFY_API_TOKEN"])

run = client.actor("pro100chok/zillow-scraper-all-in-one").call(run_input={
    "mode": "zestimate",
    "zestimateItems": PORTFOLIO,
})

total = 0
for z in client.dataset(run["defaultDatasetId"]).iterate_items():
    value = z.get("zestimate") or 0
    total += value
    change = z.get("zestimate30DayChange")
    print(f"{z.get('streetAddress')}, {z.get('city')} {z.get('state')}")
    print(f"  Zestimate ${value:,}  (range ${z.get('zestimateLow') or 0:,} - "
          f"${z.get('zestimateHigh') or 0:,})  30-day {change if change is not None else 'n/a'}")
    print(f"  rent ${z.get('rentZestimate') or 0:,}/mo  tax assessed "
          f"${z.get('taxAssessedValue') or 0:,}  tax rate {z.get('propertyTaxRate') or '-'}%")

print(f"\nPortfolio value by Zestimate: ${total:,}")
