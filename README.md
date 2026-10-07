# Zillow Listings & Zestimate Scraper — Python Example

> Export Zillow for-sale, rental and sold listings, Zestimate home values, full property details and agent profiles to Python, CSV or Google Sheets — no Zillow API key, no partner approval, no browser automation.

[![Apify Actor](https://img.shields.io/badge/Apify-Actor-blue)](https://apify.com/pro100chok/zillow-scraper-all-in-one?utm_source=github_pro100&utm_medium=readme&utm_campaign=zillow-listings-zestimate-scraper-python)
[![Python 3.10+](https://img.shields.io/badge/Python-3.10+-green)](https://python.org)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow)](LICENSE)

This repository wraps the [Zillow Scraper API actor on Apify](https://apify.com/pro100chok/zillow-scraper-all-in-one?utm_source=github_pro100&utm_medium=readme&utm_campaign=zillow-listings-zestimate-scraper-python) in small, readable Python scripts. Each one solves a concrete real-estate question — where are homes listed under their Zestimate, what did houses sell for last quarter, which agents close the most deals — instead of dumping raw JSON on you.

## What this does

Zillow retired most of its public data APIs, and what remains sits behind partner approval with tight quotas and a narrow field set. The actor is an unofficial Zillow API: it reads the publicly visible pages and returns clean records, without a key and without a daily call ceiling.

Four modes live in one actor, picked with `mode`:

| `mode` | Input | Output |
|---|---|---|
| `search` | `locations` (city, ZIP, county) or `searchUrls` | Listing cards with 60+ fields: price, beds, baths, area, lot, coordinates, Zestimate, Rent Zestimate, days on Zillow, broker, photos, open house, price change |
| `propertyDetail` | `propertyUrls` or `zpids` | 180+ facts per home, price and tax history, schools, agent contact, photos; optional Walk Score, climate risk, foreclosure detail and comps |
| `zestimate` | `zestimateItems` (address, ZPID or URL) | Zestimate with dollar low/high range, 30-day change, Rent Zestimate, tax-assessed value, 10-year value history |
| `agent` | `agentUrls` (profile URLs or a location) | Agent name, email, phones, rating, licences, team, active listings and past sales |

There is also `startUrls`: paste any mix of Zillow URLs and each one is routed to the right mode automatically.

## Past Zillow's 500-result wall

A Zillow search shows roughly 500 homes on screen, and the query behind it stops at about 820. For a metro like Houston that is a small slice. When a region holds more than the query limit, the actor splits the map into four quadrants and keeps subdividing until every rectangle fits. Set `maxItems` to `0` and a single search can return thousands of listings, with no hand-drawn map tiles.

## Use cases

- **Discount-to-Zestimate screening** — `main.py` finds homes asking well below their Zestimate and checks the confidence range before you act.
- **Portfolio and lead-list valuation** — feed hundreds of street addresses to Zestimate mode and get a value, range and rent estimate for each.
- **Sold comps** — `listingType: "sold"` with `daysOnZillow: "6m"` gives the last six months of sales for pricing or appraisal review.
- **Motivated-seller lists** — `priceReducedOnly` with `sort: "priceReduced"` surfaces recent price cuts.
- **Distressed-property sourcing** — the `foreclosures`, `auction` and `forSaleByOwner` toggles isolate bank-owned, auction and FSBO inventory.
- **Agent prospecting** — discover agents by city and rank them by `pastSalesTotal`, rating and active listings.
- **Rental underwriting** — `forRent` searches return monthly rent, and every for-sale card carries `rentZestimate` for a quick gross-yield check.
- **Climate and insurance checks** — `includeExtendedDetails` adds flood, fire, heat, wind and air scores with FEMA zone and Zillow's insurance recommendation.

## Requirements

- Python **3.10+**
- A free [Apify account](https://console.apify.com/sign-up) with its $5 monthly credit
- **No** Zillow login, API key or proxy plan

## Quick start

```bash
git clone https://github.com/pro100chok/zillow-listings-zestimate-scraper-python.git
cd zillow-listings-zestimate-scraper-python
pip install -r requirements.txt
cp .env.example .env
# paste your APIFY_API_TOKEN into .env
python main.py
```

`main.py` searches Indianapolis houses and townhomes under $350k, keeps every listing at least 8% below its Zestimate, then sends the top 25 through Zestimate mode to attach the low/high range and the 30-day trend. It also prints a gross rent yield from `rentZestimate`. Results go to `output.json` and `output.csv`.

## How it works

1. `client.actor("pro100chok/zillow-scraper-all-in-one").call(run_input=...)` starts a run on Apify and blocks until it ends.
2. The actor resolves locations to Zillow map bounds, applies your filters and paginates, splitting the map when a region is too dense.
3. Requests go out over plain HTTP with a browser-grade TLS fingerprint through rotating US residential proxies; blocked requests are retried (`maxRetries`, default 8) on a new IP.
4. `fetchDetails: true` opens each found listing's property page and merges the full record into the same row.
5. Records land in the run's default dataset; iterate them with `client.dataset(...).iterate_items()` or export CSV/Excel from the console. `flatOutput: true` flattens nested fields for spreadsheets.

## Example output

A Zestimate-mode record:

```json
{
  "zpid": "48749425",
  "streetAddress": "2114 Bigelow Ave N",
  "city": "Seattle",
  "state": "WA",
  "zipcode": "98109",
  "homeType": "SINGLE_FAMILY",
  "bedrooms": 4,
  "bathrooms": 3,
  "livingArea": 3470,
  "zestimate": 2715400,
  "zestimateLow": 2552476,
  "zestimateHigh": 2878324,
  "zestimate30DayChange": -8600,
  "rentZestimate": 8950,
  "taxAssessedValue": 2194000,
  "propertyTaxRate": 0.92
}
```

Values above are illustrative. Search cards add `price`, `address`, `area`, `daysOnZillow`, `brokerName`, `priceChange`, `priceReduction`, `hasOpenHouse` and photos; detail records add `priceHistory`, `taxHistory`, `schools`, `agentName`, `agentPhoneNumber`, `agentEmail`, `yearBuilt`, `monthlyHoaFee` and the `reso_*` fact set.

## Input parameters

| Field | Type | Notes |
|---|---|---|
| `mode` | string | `search` (default), `propertyDetail`, `zestimate`, `agent` |
| `startUrls` | array | Any Zillow URLs, routed automatically |
| `locations` / `searchUrls` | array | Search targets |
| `propertyUrls` / `zpids` | array | Property details targets |
| `zestimateItems` | array | Addresses, ZPIDs or URLs for Zestimate mode |
| `agentUrls` | array | Profile URLs or a location; `maxAgentsPerLocation` caps discovery (default 20) |
| `listingType` | string | `forSale`, `forRent`, `sold` |
| `priceMin` / `priceMax` | integer | Monthly rent when searching rentals |
| `bedsMin` / `bedsMax` / `bathsMin` / `bathsMax` | integer | Room filters |
| `sqftMin` / `sqftMax` / `lotSizeMin` / `lotSizeMax` | integer | Size filters |
| `yearBuiltMin` / `yearBuiltMax` / `hoaMax` | integer | Age and HOA limits |
| `homeTypes` | array | `houses`, `townhomes`, `condos`, `apartments`, `multiFamily`, `manufactured`, `lotsLand` |
| `daysOnZillow` | string | `1`, `7`, `14`, `30`, `90`, `6m`, `12m`, `24m`, `36m` |
| `forSaleByAgent`, `forSaleByOwner`, `newConstruction`, `comingSoon`, `auction`, `foreclosures` | boolean | For-sale category toggles |
| `hasPool`, `hasGarage`, `hasAirConditioning`, `isWaterfront`, `has3DTour`, `hasBasement`, `priceReducedOnly` | boolean | Feature filters |
| `keywords` | string | Free text, e.g. `"pool, remodeled"` |
| `sort` | string | `relevance`, `newest`, `price_desc`, `price_asc`, `priceReduced` and more |
| `fetchDetails` | boolean | Enrich search results with full details |
| `includeWalkScores` / `includeExtendedDetails` | boolean | Extra detail sections, one request each |
| `maxItems` | integer | Default 200; `0` means unlimited |

## More examples

| File | What it shows |
|---|---|
| [`examples/01_basic_usage.py`](examples/01_basic_usage.py) | Newest for-sale homes in an Atlanta ZIP with their Zestimates |
| [`examples/02_bulk_zestimate_lookup.py`](examples/02_bulk_zestimate_lookup.py) | Value a list of street addresses and total the portfolio |
| [`examples/03_agent_profiles.py`](examples/03_agent_profiles.py) | Charlotte agents ranked by past sales with phone and email |
| [`examples/04_export_to_csv.py`](examples/04_export_to_csv.py) | Six months of Boise sales to CSV with median $/sqft by home type |
| [`examples/05_export_to_google_sheets.py`](examples/05_export_to_google_sheets.py) | Weekly price-cut watchlist appended to a Google Sheet |

## Ready-made tasks

Saved, one-click configurations of the same actor:

- [Search Zillow homes for sale in any city or ZIP](https://apify.com/pro100chok/zillow-search-homes-for-sale?utm_source=github_pro100&utm_medium=readme&utm_campaign=zillow-listings-zestimate-scraper-python)
- [Look up Zestimate home values in bulk](https://apify.com/pro100chok/zillow-zestimate-value-lookup?utm_source=github_pro100&utm_medium=readme&utm_campaign=zillow-listings-zestimate-scraper-python)
- [Find foreclosures, auctions and FSBO deals](https://apify.com/pro100chok/zillow-foreclosures-and-auctions?utm_source=github_pro100&utm_medium=readme&utm_campaign=zillow-listings-zestimate-scraper-python)
- [Pull recently sold comps for a neighborhood](https://apify.com/pro100chok/zillow-sold-comps-last-6-months?utm_source=github_pro100&utm_medium=readme&utm_campaign=zillow-listings-zestimate-scraper-python)
- [Find Zillow agents with listings and past sales](https://apify.com/pro100chok/zillow-real-estate-agent-leads?utm_source=github_pro100&utm_medium=readme&utm_campaign=zillow-listings-zestimate-scraper-python)

## Pricing

Pay-per-event, proxies included. Per 1,000 records:

| Event | Free plan | Bronze | Gold and above |
|---|---|---|---|
| Listing (search result) | $2.00 | $1.50 | $1.30 |
| Property detail | $3.00 | $2.00 | $1.50 |
| Zestimate lookup | $2.00 | $1.00 | $1.00 |
| Agent profile | $5.00 | $4.00 | $3.20 |

The free $5 credit covers roughly 2,500 search listings a month.

## FAQ

**Does Zillow still have a public API?**
Not one that returns bulk listings. The remaining Zillow APIs need partner approval and expose a limited field set. The [Zillow Scraper actor](https://apify.com/pro100chok/zillow-scraper-all-in-one?utm_source=github_pro100&utm_medium=readme&utm_campaign=zillow-listings-zestimate-scraper-python) is the practical alternative.

**Can I get a Zestimate from just an address?**
Yes. Put the address in `zestimateItems` with `mode: "zestimate"`. ZPIDs and homedetails URLs work too.

**Why did my for-sale search return nothing?**
At least one of `forSaleByAgent`, `forSaleByOwner`, `newConstruction`, `comingSoon`, `auction` or `foreclosures` must be on. Also check that `homeTypes` uses the exact values listed above.

**Do I get the listing agent's phone and email?**
Detail records include `agentName`, `agentPhoneNumber`, `agentEmail` and `brokerName` when Zillow shows them. Search cards include `brokerName`; turn on `fetchDetails` to get the agent contact.

**How do I avoid spending too much?**
Keep `maxItems` small while testing, leave `fetchDetails` and the extra detail sections off unless you need them, and set a maximum charge per run in the console.

**Is it legal?**
The actor collects publicly visible data without logging in. How you store and use it — especially personal contact data — is your responsibility under your local law.

## Related actors

- [Realtor.com Scraper — listings, property data and agents](https://apify.com/pro100chok/realtor-com-scraper?utm_source=github_pro100&utm_medium=readme&utm_campaign=zillow-listings-zestimate-scraper-python) — a second US source with permits and agent reviews.
- [Apartments.com Scraper — rentals, prices and reviews](https://apify.com/pro100chok/apartments-scraper-usage?utm_source=github_pro100&utm_medium=readme&utm_campaign=zillow-listings-zestimate-scraper-python) — apartment communities and floor-plan rents.
- [Idealista Scraper API](https://apify.com/pro100chok/idealista-scraper?utm_source=github_pro100&utm_medium=readme&utm_campaign=zillow-listings-zestimate-scraper-python) — property listings in Spain and Italy.
- [ImmobilienScout24 Scraper](https://apify.com/pro100chok/immobilienscout24-scraper?utm_source=github_pro100&utm_medium=readme&utm_campaign=zillow-listings-zestimate-scraper-python) — the German market, with agent contacts.
- [Website Contact Scraper — emails, phones and socials](https://apify.com/pro100chok/extract-emails?utm_source=github_pro100&utm_medium=readme&utm_campaign=zillow-listings-zestimate-scraper-python) — find emails on brokerage websites.

## License

MIT — see [LICENSE](LICENSE).

---

Made by [pro100chok](https://apify.com/pro100chok/zillow-scraper-all-in-one?utm_source=github_pro100&utm_medium=readme&utm_campaign=zillow-listings-zestimate-scraper-python). Not affiliated with Zillow Group. Zestimate is a registered trademark of Zillow, Inc.
