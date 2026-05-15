# bpleone Sports Cards Desk

PSA-graded sports cards trading desk. Applies the Pokemon TCG framework (momentum + value + scarcity + liquidity) to NBA, NFL, MLB, and a few other markets.

Live at **sports-cards.bpleone.com**.

## What it tracks

98 cards in v1, weighted toward:

- **Baseball (33)** — 2020+ ultra-modern Topps Chrome Update RCs (Skenes, Wood, Holliday, Witt), Bowman 1st Chrome prospect autos (Salas, Walker Jenkins, Konnor Griffin, Bazzana), plus vintage HOFers (Mantle, Aaron, Clemente)
- **Football (31)** — 2024 Panini Prizm rookie class (Caleb Williams, Jayden Daniels, Marvin Harrison Jr, Malik Nabers, Brock Bowers), 2017-2023 Prizm bedrocks (Mahomes NT auto, Burrow, Allen, Lamar), College NIL (Arch Manning, Shedeur, Travis Hunter, Dylan Raiola, Bryce Underwood)
- **Basketball (26)** — Wemby base + Silver Prizm, Anthony Edwards, JDub, Caitlin Clark + Angel Reese WNBA, Cooper Flagg + AJ Dybantsa college, plus '86 Fleer Jordan, '96 Topps Chrome Kobe, '03 Topps Chrome LeBron
- **Other (8)** — Gretzky '79 OPC, Bedard Young Guns, Conor McGregor 2011 UFC, Messi '04 Megacracks, Verstappen/Hamilton/Leclerc F1 Topps Chrome, Haaland Bundesliga

## Quant methodology

```
COMPOSITE = 0.30 * MOMENTUM
          + 0.30 * VALUE
          + 0.20 * SCARCITY
          + 0.20 * LIQUIDITY
```

See the in-app **Methodology** page for full detail.

Verdict ladder:
- ≥85 → **STRONG BUY**
- 70-84 → **BUY**
- 50-69 → **HOLD**
- 30-49 → **TRIM**
- <30 → **SELL**

Cards with conviction ≥5 get +5 to composite; conviction ≤2 get −5.

## Data sources

- **eBay sold-listings** (`ebay.com/sch/i.html?LH_Sold=1`) — primary price truth, weekly refresh. Adapts the Pokemon project's scraper.
- **eBay Browse API** (optional, free OAuth at developer.ebay.com) — bypasses Akamai entirely. Set `$env:EBAY_OAUTH_TOKEN`.
- **PSA pop reports** — seeded manually per card (Cloudflare blocks scraping). Refresh quarterly.

No paid subscriptions.

## Views

- **Dashboard** — headline stats, verdict distribution, top BUYs, sport breakdown
- **Watchlist** — full 98-card table with sport / category / tier / verdict filters and player search
- **BUY Signals** — composite ≥70 cards only, sorted by score
- **By Sport** — separate watchlist per sport, sorted by score
- **Inventory** — your actual positions, cost basis, live mark-to-market, unrealized P&L
- **Card Detail** — per-card deep dive: sub-scores, recent eBay sales, eBay query string, PSA pop link, notes
- **Methodology** — full scoring explanation

## Local dev

```
pip install -r requirements.txt
python live_prices.py 10            # refresh first 10 cards (smoke test)
python live_prices.py                # refresh all 98 cards
streamlit run streamlit_app.py
```

## Refreshing prices

```
python live_prices.py                # writes live_prices.json
```

Or set up the cron in `.github/workflows/refresh.yml` (mirrors the Pokemon project pattern).

**Important — eBay blocking:** Akamai (eBay's bot wall) frequently blocks data-center IPs. The scraper will work fine from your home IP. For Streamlit Cloud / GH Actions runners, set `EBAY_OAUTH_TOKEN` and the code switches to the official Browse API path (no blocking).

## Deploy

```
python DEPLOY.py    # pushes to Keyvaniath/bpleone-sports-cards-desk
```

Then connect that repo in Streamlit Community Cloud, point CNAME `sports-cards.bpleone.com` to the Streamlit app.

## Files

- `streamlit_app.py` — dashboard, 7 views
- `cards_data.py` — 98-card seed watchlist (single source of truth)
- `live_prices.py` — eBay scraper + API path, writes `live_prices.json`
- `quant_score.py` — composite scoring engine
- `requirements.txt` — `streamlit`, `pandas`, `requests`
- `inventory.json` — your positions (created on first save in Inventory view)

## Roadmap

- [ ] Daily price refresh GitHub Action
- [ ] Discord alert on STRONG BUY signal flip
- [ ] Pop tracking changes (manual JSON, snapshot quarterly)
- [ ] Sealed product (boxes/cases) section — Bowman Chrome / Topps Chrome / Prizm
- [ ] Cross-asset correlation: card price vs. player WAR / passer rating
- [ ] Tax report (Schedule D / Form 8949) — mirror Pokemon desk's `tax_report.py`
- [ ] Trade-of-the-day email
