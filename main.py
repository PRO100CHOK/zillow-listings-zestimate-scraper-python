"""Zillow list-price vs Zestimate gap finder.

Use case: find for-sale homes in a market whose asking price sits well below
Zillow's own Zestimate, then re-check the shortlist in Zestimate mode to get
the dollar confidence range and the 30-day trend before anyone picks up the
phone.

  Step 1 - search for-sale houses and townhomes in one city (search cards
           already carry `zestimate` and `rentZestimate`).
  Step 2 - keep homes listed at least GAP below their Zestimate and compute a
           rough gross rent yield from `rentZestimate`.
  Step 3 - run Zestimate mode on the shortlist for `zestimateLow`,
           `zestimateHigh` and `zestimate30DayChange`.

Writes output.json and output.csv.

Run:
    pip install -r requirements.txt
    cp .env.example .env
    python main.py

Actor: https://apify.com/pro100chok/zillow-scraper-all-in-one?utm_source=github_pro100&utm_medium=readme&utm_campaign=zillow-listings-zestimate-scraper-python
"""
from __future__ import annotations

import csv
import json
import os
import sys
from pathlib import Path

from apify_client import ApifyClient
from apify_client.errors import ApifyApiError
from dotenv import load_dotenv

ACTOR_ID = "pro100chok/zillow-scraper-all-in-one"
LOCATION = "Indianapolis, IN"
PRICE_MAX = 350000
GAP = 0.08            # listed at least 8% under the Zestimate
SEARCH_LIMIT = 400
SHORTLIST = 25

COLUMNS = [
    "zpid", "address", "price", "zestimate", "gapPct", "zestimateLow",
    "zestimateHigh", "zestimate30DayChange", "rentZestimate", "grossYieldPct",
    "beds", "baths", "area", "homeType", "daysOnZillow", "brokerName", "url",
]


def main() -> int:
    load_dotenv()
    token = os.environ.get("APIFY_API_TOKEN")
    if not token:
        sys.exit("APIFY_API_TOKEN missing - copy .env.example to .env first.")

    client = ApifyClient(token)
    out = Path(__file__).parent

    # Step 1: search cards with Zestimate attached
    print(f"Step 1/3 - for-sale homes in {LOCATION} under ${PRICE_MAX:,}")
    try:
        run = client.actor(ACTOR_ID).call(
            run_input={
                "mode": "search",
                "locations": [LOCATION],
                "listingType": "forSale",
                "homeTypes": ["houses", "townhomes"],
                "priceMax": PRICE_MAX,
                "bedsMin": 2,
                "sort": "newest",
                "maxItems": SEARCH_LIMIT,
            },
            timeout_secs=1800,
        )
    except ApifyApiError as exc:
        sys.exit(f"Search step failed: {exc}")

    homes = list(client.dataset(run["defaultDatasetId"]).iterate_items())
    print(f"  {len(homes)} listings collected")

    # Step 2: biggest discounts to Zestimate
    candidates = []
    for h in homes:
        price, zest = h.get("price"), h.get("zestimate")
        if not price or not zest:
            continue
        gap = 1 - price / zest
        if gap >= GAP:
            h["gapPct"] = round(gap * 100, 1)
            if h.get("rentZestimate"):
                h["grossYieldPct"] = round(h["rentZestimate"] * 12 / price * 100, 1)
            candidates.append(h)
    candidates.sort(key=lambda h: -h["gapPct"])
    shortlist = candidates[:SHORTLIST]
    print(f"\nStep 2/3 - {len(candidates)} homes at least {int(GAP * 100)}% under "
          f"Zestimate, checking the top {len(shortlist)}")

    if not shortlist:
        print("  nothing matched - loosen GAP or raise PRICE_MAX")
        return 0

    # Step 3: confidence range and 30-day direction for the shortlist
    try:
        z_run = client.actor(ACTOR_ID).call(
            run_input={
                "mode": "zestimate",
                "zestimateItems": [str(h["zpid"]) for h in shortlist if h.get("zpid")],
            },
            timeout_secs=1200,
        )
    except ApifyApiError as exc:
        sys.exit(f"Zestimate step failed: {exc}")

    by_zpid = {str(z.get("zpid")): z
               for z in client.dataset(z_run["defaultDatasetId"]).iterate_items()}
    for h in shortlist:
        z = by_zpid.get(str(h.get("zpid")), {})
        for key in ("zestimateLow", "zestimateHigh", "zestimate30DayChange"):
            h[key] = z.get(key)

    print("\nStep 3/3 - shortlist")
    for h in shortlist:
        trend = h.get("zestimate30DayChange")
        trend_s = f"{trend:+,}" if isinstance(trend, (int, float)) else "n/a"
        print(f"  -{h['gapPct']:>5}%  ${h['price']:>9,} vs ${h['zestimate']:>9,}  "
              f"30d {trend_s:>8}  yield {h.get('grossYieldPct') or '-':>4}%  "
              f"{h.get('address')}")

    (out / "output.json").write_text(
        json.dumps(shortlist, indent=2, ensure_ascii=False), encoding="utf-8")
    with (out / "output.csv").open("w", newline="", encoding="utf-8") as fh:
        w = csv.DictWriter(fh, fieldnames=COLUMNS, extrasaction="ignore")
        w.writeheader()
        w.writerows(shortlist)
    print("\nSaved output.json and output.csv")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
