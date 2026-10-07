"""Zillow agents in a city ranked by lifetime sales, with contact details.

In agent mode, `agentUrls` takes either profile URLs
(https://www.zillow.com/profile/<name>/) or a location to discover agents in;
`maxAgentsPerLocation` caps how many are fetched per location.

Actor: https://apify.com/pro100chok/zillow-scraper-all-in-one?utm_source=github_pro100&utm_medium=readme&utm_campaign=zillow-listings-zestimate-scraper-python
"""
import os

from apify_client import ApifyClient
from dotenv import load_dotenv

load_dotenv()
client = ApifyClient(os.environ["APIFY_API_TOKEN"])

run = client.actor("pro100chok/zillow-scraper-all-in-one").call(run_input={
    "mode": "agent",
    "agentUrls": ["Charlotte, NC"],
    "maxAgentsPerLocation": 25,
    "includeAgentListings": True,
    "includeAgentPastSales": True,
    "includeAgentReviews": False,
})

agents = list(client.dataset(run["defaultDatasetId"]).iterate_items())
agents.sort(key=lambda a: -(a.get("pastSalesTotal") or 0))

for a in agents:
    print(f"{a.get('pastSalesTotal') or 0:>5} sales  {a.get('forSaleCount') or 0:>3} active  "
          f"{a.get('ratingAverage') or '-'} stars ({a.get('ratingCount') or 0})  "
          f"{(a.get('name') or '-')[:30]:<30}  {a.get('phoneCell') or ''}  {a.get('email') or ''}")
