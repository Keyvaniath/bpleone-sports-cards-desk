# Changelog

Notable changes to the bpleone Sports Cards Desk.

## [Unreleased]

### Added
- `build_stats.py` — generates `docs/stats.json` with by-sport breakdowns, top
  gainers/losers, upcoming catalysts, verdict mix. Refreshed alongside `signals.json`.
- Watchlist expanded from 98 to 114 cards. New depth:
  - **WNBA (5)**: Paige Bueckers, Cameron Brink, A'ja Wilson, Sabrina Ionescu, JuJu Watkins
  - **MLB veterans (3)**: Mookie Betts 1st Bowman, Ohtani Update RC, Spencer Strider
  - **F1 (2)**: Lando Norris, Oscar Piastri
  - **Soccer (2)**: Kylian Mbappé World Cup, Erling Haaland Donruss
  - **UFC (1)**: Israel Adesanya
  - **NHL (3)**: Sidney Crosby Young Guns, Auston Matthews YG, Macklin Celebrini YG

### Changed
- `.github/workflows/refresh.yml` now also regenerates `stats.json` alongside `signals.json` on each weekly refresh.

## [0.9.0] — 2026-05-15

### Added
- `build_signals.py` — generates `docs/signals.json` with top BUY/STRONG-BUY signals
  for public consumption by the bpleone.com/sports-cards/ landing.
- Landing page (`docs/index.html`) now fetches live signals client-side from
  `raw.githubusercontent.com/Keyvaniath/bpleone-sports-cards-desk/main/docs/signals.json`
  with 5-minute auto-refresh.

## [0.8.0] — 2026-05-15

### Added
- 36 vintage HOFer grade ladders (`vintage_matrix.py`) — PSA 4-10 prices for Mantle '52,
  Aaron '54, Clemente '55, Pete Rose '63, Payton '76, Brady '00 Bowman, Jordan '86,
  Kobe '96 Topps Chrome, LeBron '03 Topps Chrome, Gretzky '79 OPC.
- **🏛️ Vintage Grades** dashboard view — per-card grade ladder + heat-coded spread table.
- **📚 By Set** view — group cards by parent set, drill into individual sets.
- **🔎 Sidebar quick-jump** text input — type player/set, auto-route to Card Detail.
- All `use_container_width` calls migrated to `width='stretch'` (Streamlit deprecation).

## [0.7.0] — 2026-05-15

### Added
- **📈 Charts** view — 4 Altair visualizations: composite scatter, trend histogram,
  verdict mix by sport, PSA pop scarcity log-log scatter.

## [0.6.0] — 2026-05-15

### Added
- **📓 Trade Journal** — append-only buy/sell log with realized P&L tracking.

## [0.5.0] — 2026-05-15

### Added
- **📅 Catalysts Calendar** (`catalysts.py`) — 14 known 2026 events (NFL Draft,
  NBA Lottery, MLB Trade Deadline, Heisman, PSA pop refresh, NT release) with
  expected-move ranges + affected card IDs.
- Inventory page: holding-period analyzer surfaces positions within 30 days of
  the long-term tax flip (collectibles 28% cap kicks in at 365 days).

## [0.4.0] — 2026-05-15

### Added
- Card images extracted from eBay sold listings, rendered in Card Detail.
- Buy-zone alert section on Watchlist (live ≤ buy + 5%).
- CSV export from Watchlist.
- Direct "View live eBay sold comps" link on every Card Detail.

## [0.3.0] — 2026-05-15

### Added
- **🌈 Parallels** seed (`parallels.py`) — 36 color/refractor parallels with
  print-run-aware scarcity scoring. Silver, Hyper, Color, Numbered, Gold /10, RPA.
- **⚖️ Compare** view — head-to-head card-vs-card with sub-score bar chart.
- **🧮 Sizer** view — bankroll × risk × 1/2-Kelly suggested-position table.
- **📈 Price history** (`price_history.py`) — append-only JSONL snapshots on each
  refresh, charted on Card Detail.

## [0.2.0] — 2026-05-15

### Added
- **📦 Sealed Products** (`sealed_products.py`) — 17 boxes/cases (Bowman Chrome,
  Topps Chrome, Panini Prizm, NT, Optic, Mega) with EV-based scoring.
- `discord_alert.py` — webhook hook posts on BUY/SELL signal transitions.
- `trade_of_day_email.py` — SMTP digest with top BUY + runner-up + TRIM warnings.

## [0.1.0] — 2026-05-15

### Initial
- 98-card watchlist across Baseball (33), Football (31), Basketball (26), Other (8).
- `quant_score.py` — composite 0.30·MOMENTUM + 0.30·VALUE + 0.20·SCARCITY + 0.20·LIQUIDITY.
- `live_prices.py` — eBay sold-listings scraper + Browse API fallback.
- `streamlit_app.py` — 7-page dashboard (Dashboard, Watchlist, BUY Signals,
  By Sport, Inventory, Card Detail, Methodology).
- `tax_report.py` — Schedule D / Form 8949 helper with collectibles 28% cap.
- `.github/workflows/refresh.yml` — Sunday 22:00 UTC weekly eBay refresh.
