"""30 newest Zillow homes for sale in a ZIP code - the minimal call.

`locations` takes a city ("Austin, TX"), a ZIP ("90210") or a county
("Travis County, TX"). Search cards already include the Zestimate.

Actor: https://apify.com/pro100chok/zillow-scraper-all-in-one?utm_source=github_pro100&utm_medium=readme&utm_campaign=zillow-listings-zestimate-scraper-python
"""
import os

from apify_client import ApifyClient
from dotenv import load_dotenv

load_dotenv()
client = ApifyClient(os.environ["APIFY_API_TOKEN"])

run = client.actor("pro100chok/zillow-scraper-all-in-one").call(run_input={
    "mode": "search",
    "locations": ["30307"],
    "listingType": "forSale",
    "sort": "newest",
    "maxItems": 30,
})

for h in client.dataset(run["defaultDatasetId"]).iterate_items():
    print(f"${h.get('price') or 0:>10,}  zest ${h.get('zestimate') or 0:>10,}  "
          f"{h.get('beds') or '-'}bd/{h.get('baths') or '-'}ba  {h.get('area') or '-':>5} sqft  "
          f"{h.get('daysOnZillow') or 0:>3}d  {h.get('address')}")
