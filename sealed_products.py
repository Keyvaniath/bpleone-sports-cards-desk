"""
Sealed product (boxes / cases) watchlist for the Sports Cards desk.

Different thesis than singles: sealed product is a long-duration vintage-style
hold. EV math is driven by the underlying card distribution × grading hit-rate,
but the simple play is just buy sealed at MSRP and wait.

Schema:
  id           SB### (sports box) prefix
  sport        Baseball | Football | Basketball
  product      Box / Case / Hobby Box / Jumbo / Hanger
  brand        Topps / Bowman / Panini / Upper Deck
  set_year     '2024 Topps Chrome', '2024 Bowman Chrome Hobby', etc.
  config       boxes per case, packs per box, cards per pack
  msrp         original MSRP
  market       current sealed market price
  trend30d     market trend
  ev_floor     bottom-quartile EV per box (downside)
  ev_top       top-quartile EV per box (rip-ribbon hits)
  notes        thesis
"""

SEALED = [
    # ============================================================
    # BASEBALL
    # ============================================================
    ("SB001", "Baseball", "Hobby Box", "Bowman",
     "2024 Bowman Chrome", "12 boxes/case · 12 packs · 4 cards", 290, 380, 0.15,
     220, 600, "Top 1st Bowman year for the 2024 rookie class. Walker Jenkins/Konnor Griffin chase."),
    ("SB002", "Baseball", "Hobby Box", "Topps",
     "2024 Topps Chrome", "12 boxes/case · 24 packs · 4 cards", 220, 280, 0.05,
     150, 450, "Topps Chrome flagship. Skenes/Holliday/Wood RC chase. Stable hold."),
    ("SB003", "Baseball", "Hobby Box", "Topps",
     "2024 Topps Chrome Update", "12 boxes/case · 24 packs · 4 cards", 240, 320, 0.10,
     180, 500, "Update set = where the rookie cards live. Higher RC density."),
    ("SB004", "Baseball", "Jumbo Box", "Topps",
     "2024 Topps Chrome", "8 boxes/case · 12 packs · 13 cards", 320, 410, 0.08,
     250, 550, "Jumbo = more cards, fewer hits per pack but cheaper per card."),
    ("SB005", "Baseball", "Case", "Bowman",
     "2024 Bowman Chrome HTA", "12 boxes/case · HTA = hobby-shop allocated", 5000, 6800, 0.12,
     4500, 9500, "HTA case — sealed institutional play. 5-10 year hold."),

    # ============================================================
    # FOOTBALL
    # ============================================================
    ("SB006", "Football", "Hobby Box", "Panini",
     "2024 Panini Prizm", "12 boxes/case · 12 packs · 12 cards", 280, 350, 0.20,
     200, 600, "Caleb Williams / Jayden Daniels / MHJ rookie class. Best-loved set."),
    ("SB007", "Football", "Hobby Box", "Panini",
     "2024 Panini Donruss Optic", "20 boxes/case · 20 packs · 4 cards", 110, 145, 0.05,
     80, 230, "Optic = budget Prizm. Solid floor, cheaper entry."),
    ("SB008", "Football", "Mega Box", "Panini",
     "2024 Panini Prizm Mega (Walmart)", "Retail mega box · pink/purple variants", 60, 95, 0.30,
     40, 180, "Walmart mega. Pink/purple variants only here. Hot due to retail scarcity."),
    ("SB009", "Football", "Hobby Box", "Panini",
     "2024 Panini Select", "12 boxes/case · 12 packs · 5 cards", 320, 410, 0.10,
     240, 650, "Select = mid-tier hobby chase. Concourse/Premier/Field Level tiering."),
    ("SB010", "Football", "Case", "Panini",
     "2024 Panini National Treasures", "8 boxes/case · 5 packs · 5 cards", 18000, 22000, 0.05,
     14000, 32000, "NT = grail tier. Patch autos. 8-box case. Pro flippers only."),

    # ============================================================
    # BASKETBALL
    # ============================================================
    ("SB011", "Basketball", "Hobby Box", "Panini",
     "2023-24 Panini Prizm", "12 boxes/case · 12 packs · 12 cards", 480, 580, 0.05,
     350, 950, "Wemby rookie year. The most-printed Wemby card lives here."),
    ("SB012", "Basketball", "Hobby Box", "Panini",
     "2023-24 Panini Donruss Optic", "20 boxes/case · 20 packs · 4 cards", 180, 220, 0.02,
     130, 380, "Optic Wemby chase. Budget alternative to Prizm."),
    ("SB013", "Basketball", "Hobby Box", "Panini",
     "2023-24 Panini Select", "12 boxes/case · 12 packs · 5 cards", 540, 650, 0.08,
     400, 1100, "Wemby Select. Concourse/Premier/Courtside parallels."),
    ("SB014", "Basketball", "Mega Box", "Panini",
     "2023-24 Panini Prizm Mega (Target)", "Target mega · green/pink variants", 80, 115, 0.25,
     55, 220, "Target mega. Green/pink Wemby parallels. Retail premium."),
    ("SB015", "Basketball", "Case", "Panini",
     "2023-24 Panini National Treasures", "8 boxes/case · 7 cards", 36000, 44000, 0.10,
     28000, 65000, "Wemby NT RC patch auto = $400K+ pull potential. Pro tier."),

    # ============================================================
    # COLLEGE / DRAFT
    # ============================================================
    ("SB016", "Basketball", "Hobby Box", "Bowman",
     "2024 Bowman University Chrome", "8 boxes/case · 16 packs · 3 cards", 280, 360, 0.20,
     200, 600, "Cooper Flagg / AJ Dybantsa / Robert Wright Jr. Pre-NBA-draft college chase."),
    ("SB017", "Football", "Hobby Box", "Panini",
     "2024 Panini Prizm Draft Picks", "16 boxes/case · 24 packs · 6 cards", 220, 280, 0.15,
     150, 450, "Pre-NFL college autos. Dylan Raiola, Quinn Ewers, Carson Beck."),
]


# Optional: separate scoring for sealed products
def score_sealed(product: tuple) -> dict:
    """Simple EV-based sealed score: (market - msrp) vs (ev_top - market) upside."""
    (pid, sport, prod, brand, set_year, config, msrp, market, trend30d,
     ev_floor, ev_top, notes) = product
    appreciation_pct = (market - msrp) / msrp if msrp > 0 else 0
    upside_pct = (ev_top - market) / market if market > 0 else 0
    downside_pct = (market - ev_floor) / market if market > 0 else 0
    risk_reward = upside_pct / max(0.05, downside_pct)
    # Composite: trend + risk-adjusted upside
    composite = 50 + 200 * trend30d + 30 * risk_reward
    composite = max(0.0, min(100.0, composite))
    verdict = ("STRONG BUY" if composite >= 85 else
               "BUY" if composite >= 70 else
               "HOLD" if composite >= 50 else
               "TRIM" if composite >= 30 else "SELL")
    return {
        "id": pid, "composite": round(composite, 1), "verdict": verdict,
        "appreciation_pct": round(100 * appreciation_pct, 1),
        "upside_pct": round(100 * upside_pct, 1),
        "downside_pct": round(100 * downside_pct, 1),
        "risk_reward": round(risk_reward, 2),
    }


SEALED_COLS = {
    "id": 0, "sport": 1, "product": 2, "brand": 3, "set_year": 4, "config": 5,
    "msrp": 6, "market": 7, "trend30d": 8, "ev_floor": 9, "ev_top": 10, "notes": 11,
}
