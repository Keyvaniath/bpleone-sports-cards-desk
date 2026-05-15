# bpleone Sports Cards Desk

PSA-graded sports cards trading framework. Composite quant scoring on a curated multi-sport watchlist, refreshed weekly off eBay sold-comps.

**Live at** [bpleone.com/sports-cards/](https://bpleone.com/sports-cards/) and [keyvaniath.github.io/bpleone-sports-cards-desk/](https://keyvaniath.github.io/bpleone-sports-cards-desk/) (fallback)

## What's tracked

**143 cards** across 8 sports:

- 🏈 **Football (43)** — 2024 Panini Prizm class (Caleb Williams, Jayden Daniels, MHJ, Malik Nabers, Brock Bowers), 2017-2023 Prizm bedrocks (Mahomes NT auto, Burrow, Allen, Lamar, Hurts), 2020 Prizm WR1s (Jefferson, Lamb, Chase), College NIL (Arch Manning, Shedeur Sanders, Travis Hunter, Bryce Underwood, Cam Ward), vintage (Brady SP Auth, Walter Payton, Joe Montana)
- ⚾ **Baseball (41)** — 2024 Topps Chrome Update class (Skenes, Wood, Holliday, Witt, Henderson), Bowman 1st Chrome prospects (Salas, Walker Jenkins, Konnor Griffin, Bazzana, Roman Anthony, Roki Sasaki), veterans (Trout, Judge, Acuña, Soto, Vladdy, Ohtani, Mookie 1st Bowman), vintage HOFers ('52 Mantle, '54 Aaron, '55 Clemente, '63 Pete Rose)
- 🏀 **Basketball (39)** — Wemby base + Silver Prizm + Gold /10 + Select, current stars (Anthony Edwards, Jalen Williams, Cade Cunningham, Paolo Banchero), All-Stars (Tatum, Mitchell, Booker, Jaylen Brown, Trae Young, Luka), WNBA (Caitlin Clark, Angel Reese, A'ja Wilson, Paige Bueckers, Sabrina Ionescu, JuJu Watkins), college (Cooper Flagg, AJ Dybantsa, VJ Edgecombe), vintage ('86 Fleer Jordan, '96 Topps Chrome Kobe, '03 Topps Chrome LeBron)
- 🏒 **Other (20)** — Hockey (Gretzky '79 OPC, Crosby YG, Auston Matthews YG, Bedard YG, Celebrini YG), UFC (McGregor, Adesanya), F1 (Verstappen, Hamilton, Leclerc, Norris, Piastri), soccer (Messi '04 Megacracks, Mbappé, Vinicius Jr, Bellingham, Haaland, Cole Palmer), tennis (Carlos Alcaraz)

Plus:
- **36 color/refractor parallels** — Silver → Hyper → Color → Numbered → Gold /10 → NT RPA /99 (Wemby NT RPA $78K apex)
- **17 sealed boxes/cases** — Bowman Chrome HTA case, Topps Chrome Update, Panini Prizm Football, Wemby NT case, 2024 Bowman University Cooper Flagg chase
- **36 vintage grade ladders** — per-card PSA 4-10 prices for 11 vintage HOFers
- **14 catalysts** — known 2026 events that move cards (NFL Draft, NBA Lottery + Draft, MLB Trade Deadline, Heisman, PSA pop refresh, NT release)

## Quant methodology

```
COMPOSITE = 0.30 * MOMENTUM
          + 0.30 * VALUE
          + 0.20 * SCARCITY
          + 0.20 * LIQUIDITY
```

Verdict ladder:
- ≥85 → **STRONG BUY**
- 70-84 → **BUY**
- 50-69 → **HOLD**
- 30-49 → **TRIM**
- <30 → **SELL**

Conviction ≥5 → +5 to composite. Conviction ≤2 → -5.

Full math: [bpleone.com/sports-cards/methodology/](https://bpleone.com/sports-cards/methodology/)

## Streamlit dashboard — 16 views

| View | What it does |
|---|---|
| 🏠 Dashboard | Headline stats, verdict mix, top BUYs, sport breakdown |
| 🔍 Watchlist | Full table with filters, buy-zone alerts, CSV export |
| 🎯 BUY Signals | Composite ≥70 only |
| 📊 By Sport | Per-sport tables sorted by score |
| 🌈 Parallels | 36 parallels filtered by sport / type / verdict |
| 📦 Sealed | Boxes/cases with EV-based scoring |
| 🏛️ Vintage Grades | Per-card PSA grade ladders + heat-coded spreads |
| 📚 By Set | Group cards by parent set, drill-down |
| ⚖️ Compare | Head-to-head card-vs-card with sub-score bars |
| 🧮 Sizer | Bankroll × risk × 1/2 Kelly suggested table |
| 📈 Charts | Altair scatter, trend distribution, verdict mix, pop scarcity |
| 📅 Catalysts | Upcoming events with urgency color coding |
| 💼 Inventory | Single + bulk CSV import, holding-period analyzer |
| 📓 Journal | Append-only buy/sell log with realized P&L |
| 🃏 Card Detail | Price history chart, eBay sales, image, direct search link |
| ℹ️ Methodology | Full scoring explanation |

Plus sidebar quick-jump search.

## Public JSON API

CORS-open, no auth, refreshed weekly. Full docs at [/sports-cards/api/](https://bpleone.com/sports-cards/api/).

| Endpoint | What |
|---|---|
| [signals.json](https://raw.githubusercontent.com/Keyvaniath/bpleone-sports-cards-desk/main/docs/signals.json) | Top BUY signals |
| [stats.json](https://raw.githubusercontent.com/Keyvaniath/bpleone-sports-cards-desk/main/docs/stats.json) | By-sport breakdowns, gainers/losers, catalysts |
| [feed.xml](https://raw.githubusercontent.com/Keyvaniath/bpleone-sports-cards-desk/main/docs/feed.xml) | RSS 2.0 feed of BUY signals |
| [widget.html](https://bpleone.com/sports-cards/widget.html) | Embeddable ticker (iframe-able) |

## Data sources

- **eBay sold-listings** — primary price truth, weekly refresh. Outlier-rejected median over recent comps. Image extraction. Optional Browse-API path bypasses Akamai (set `EBAY_OAUTH_TOKEN`).
- **PSA pop reports** — seeded manually per card (Cloudflare blocks scraping). Quarterly refresh.

**Zero paid subscriptions.**

## Local dev

```
pip install -r requirements.txt
streamlit run streamlit_app.py
```

## Refresh data

```
python live_prices.py       # eBay sold-comp refresh → live_prices.json + price_history.jsonl
python build_signals.py     # → docs/signals.json
python build_stats.py       # → docs/stats.json
python build_rss.py         # → docs/feed.xml
```

Or wait for the **Sunday 22:00 UTC** GitHub Action (`.github/workflows/refresh.yml`) — all of the above in one cycle.

## Deploy

```
python DEPLOY.py
```

Pushes to `Keyvaniath/bpleone-sports-cards-desk`. Streamlit Community Cloud auto-rebuilds the connected app within ~60s.

## Files

```
streamlit_app.py      ─ main dashboard, 16 pages
cards_data.py         ─ 143-card watchlist (single source of truth)
parallels.py          ─ 36 color/refractor parallels
sealed_products.py    ─ 17 sealed boxes/cases
vintage_matrix.py     ─ 36 vintage HOFer grade ladders
catalysts.py          ─ 14 known 2026 events
quant_score.py        ─ composite scoring engine
live_prices.py        ─ eBay scraper + Browse API
price_history.py      ─ append-only JSONL of price snapshots
build_signals.py      ─ regenerates docs/signals.json
build_stats.py        ─ regenerates docs/stats.json
build_rss.py          ─ regenerates docs/feed.xml
tax_report.py         ─ Schedule D / Form 8949 (collectibles 28% cap)
discord_alert.py      ─ webhook on BUY/SELL signal flips
trade_of_day_email.py ─ SMTP daily digest
DEPLOY.py / DEPLOY.bat─ one-click push to repo
.github/workflows/    ─ weekly refresh cron
docs/                 ─ static site served at GH Pages + mirrored to bpleone.com
  index.html             landing
  methodology.html       quant deep-dive
  api.html               public API docs
  widget.html            embeddable ticker
  signals.json           top BUY signals
  stats.json             aggregate stats
  feed.xml               RSS 2.0
```

## Tax handling

Sports cards are **collectibles** under IRC §408(m)(2)(A). Long-term gains capped at the 28% rate (higher than the 20% LTCG cap). `tax_report.py` generates Schedule D summary + Form 8949 rows from `sales.json`.

## Roadmap

- [ ] Player-level deep dive (career stats, recent form) inside Streamlit
- [ ] Discord webhook live on STRONG BUY signal flips (code exists, needs `DISCORD_WEBHOOK_URL` secret)
- [ ] Trade-of-the-day email enabled (code exists, needs `SMTP_USER` + `SMTP_PASSWORD`)
- [ ] Streamlit Community Cloud deploy at sports-cards.bpleone.com (needs DNS CNAME at Squarespace)
- [ ] Historic head-to-head splits
- [ ] Cross-asset correlation: card price vs. player WAR / passer rating

## Changelog

See [CHANGELOG.md](./CHANGELOG.md).
