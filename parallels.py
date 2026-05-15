"""
Color / refractor / numbered parallel seed for the top modern cards.

In sports cards, the same RC exists in dozens of variants. A base Prizm
Wemby is $720 PSA 10; a Silver Prizm is $2,200; a Gold /10 is $25K+.

Parallel tiers (Panini Prizm convention):
  Base           — common refractor
  Silver         — 1 per box, 3-5x base
  Hyper          — colored refractor, 5-8x base
  Mojo / Choice  — 10-15x base
  Numbered (/49, /25, /10, /5, /3)  — scarcity-driven
  Gold (/10)     — usually 30-60x base
  Black (/1)     — superfractor / true 1/1, varies wildly

For each anchor card I track 2-4 of the most-liquid parallels above base.

Schema mirrors cards_data.py with one twist: `base_id` references the
underlying card in cards_data.CARDS.

  id, base_id, sport, parallel_name, print_run (str), grade,
  price, trend30d, t_buy, t_sell, pop, ebay_query, notes
"""

# print_run = "unnumbered" / "/49" / "/25" / "/10" / "/5" / "/3" / "/1" / "RPA /99"

PARALLELS = [
    # ============================================================
    # Wemby — most-traded parallel tower in basketball
    # ============================================================
    ("P001", "K001", "Basketball", "Silver Prizm",          "unnumbered", "PSA 10",  2200,  0.08, 1700, 3800,  980,
     "2023 Panini Prizm Silver Victor Wembanyama RC PSA 10",
     "Step-up from base. Most-bought Wemby parallel. Liquid in PSA 10."),
    ("P002", "K001", "Basketball", "Hyper Prizm",           "unnumbered", "PSA 10",  3400,  0.10, 2600, 5500,  420,
     "2023 Panini Prizm Hyper Victor Wembanyama RC PSA 10",
     "Color refractor. 4-5x base. Tighter pop than silver."),
    ("P003", "K001", "Basketball", "Gold Prizm",            "/10",        "PSA 10",  85000, 0.05, 65000, 130000, 8,
     "2023 Panini Prizm Gold Victor Wembanyama RC /10 PSA 10",
     "Gold /10. Top of base Prizm pyramid. Institutional grail."),
    ("P004", "K001", "Basketball", "Black Finite",          "/1",         "PSA 10", 450000, 0.10, 350000, 700000, 1,
     "2023 Panini Prizm Black Wembanyama RC 1/1 PSA 10",
     "1/1. Most recent sale: $750K Feb 2026. Unique."),

    # ============================================================
    # Caleb Williams — top NFL rookie parallel ladder
    # ============================================================
    ("P005", "F001", "Football", "Silver Prizm",            "unnumbered", "PSA 10",   720,  0.08,  550, 1300, 1100,
     "2024 Panini Prizm Silver Caleb Williams RC PSA 10",
     "Silver. 3x base. Liquid in PSA 10."),
    ("P006", "F001", "Football", "Hyper Prizm",             "unnumbered", "PSA 10",  1300,  0.15,  950, 2400,  480,
     "2024 Panini Prizm Hyper Caleb Williams RC PSA 10",
     "Hyper refractor. Bears collector base + USC alumni love this."),
    ("P007", "F001", "Football", "Red Prizm",               "/199",       "PSA 10",  2400,  0.10, 1800, 4200,  120,
     "2024 Panini Prizm Red Caleb Williams RC /199 PSA 10",
     "Red /199. Mid-tier numbered. Strong USC color matching."),
    ("P008", "F001", "Football", "Gold Prizm",              "/10",        "PSA 10", 28000,  0.05, 22000, 45000,  3,
     "2024 Panini Prizm Gold Caleb Williams RC /10 PSA 10",
     "Gold /10. Final base-set tier before NT auto."),

    # ============================================================
    # Marvin Harrison Jr — most-loved WR parallel
    # ============================================================
    ("P009", "F006", "Football", "Silver Prizm",            "unnumbered", "PSA 10",   480,  0.10,  360,  850,  920,
     "2024 Panini Prizm Silver Marvin Harrison Jr RC PSA 10",
     "Silver. HOF dad creates emotional premium."),
    ("P010", "F006", "Football", "Red White Blue",          "unnumbered", "PSA 10",   850,  0.15,  650, 1400,  580,
     "2024 Panini Prizm Red White Blue Marvin Harrison Jr RC PSA 10",
     "RWB pulsar — cult favorite parallel. Limited per box."),
    ("P011", "F006", "Football", "Green Prizm",             "/10",        "PSA 10", 14000,  0.08, 11000, 22000,  4,
     "2024 Panini Prizm Green Marvin Harrison Jr RC /10 PSA 10",
     "Green /10. Cards highest base parallel."),

    # ============================================================
    # Jayden Daniels — OROY parallel chase
    # ============================================================
    ("P012", "F002", "Football", "Silver Prizm",            "unnumbered", "PSA 10",   650,  0.20,  480, 1200,  850,
     "2024 Panini Prizm Silver Jayden Daniels RC PSA 10",
     "Silver. OROY winner. Commanders momentum."),
    ("P013", "F002", "Football", "Hyper Prizm",             "unnumbered", "PSA 10",  1100,  0.25,  800, 2000,  420,
     "2024 Panini Prizm Hyper Jayden Daniels RC PSA 10",
     "Hyper. Best risk:reward in 2024 class."),

    # ============================================================
    # Brock Bowers — top TE parallel
    # ============================================================
    ("P014", "F008", "Football", "Silver Prizm",            "unnumbered", "PSA 10",   420,  0.40,  300,  780,  680,
     "2024 Panini Prizm Silver Brock Bowers RC PSA 10",
     "Silver. Broke rookie TE records. Generational TE."),
    ("P015", "F008", "Football", "Pink Prizm",              "unnumbered", "PSA 10",   650,  0.45,  480, 1200,  410,
     "2024 Panini Prizm Pink Brock Bowers RC PSA 10",
     "Pink. Limited print. Color popular for TEs."),

    # ============================================================
    # Paul Skenes — top MLB rookie parallel
    # ============================================================
    ("P016", "B001", "Baseball", "Refractor",               "unnumbered", "PSA 10",   480,  0.10,  360,  850,  650,
     "2024 Topps Chrome Update Refractor Paul Skenes RC PSA 10",
     "Refractor. Anatomy of Topps Chrome parallel ladder starts here."),
    ("P017", "B001", "Baseball", "Pink Refractor",          "/199",       "PSA 10",  1400,  0.15, 1050, 2400,  140,
     "2024 Topps Chrome Update Pink Refractor Paul Skenes RC /199 PSA 10",
     "Pink /199. Mid-tier Topps numbered. Strong float."),
    ("P018", "B001", "Baseball", "Gold Refractor",          "/50",        "PSA 10",  6500,  0.08, 5000, 10500,  18,
     "2024 Topps Chrome Update Gold Refractor Paul Skenes RC /50 PSA 10",
     "Gold /50. Top of numbered ladder before 1/1."),

    # ============================================================
    # Anthony Edwards — base Prizm grail tier
    # ============================================================
    ("P019", "K005", "Basketball", "Silver Prizm",          "unnumbered", "PSA 10",  1100,  0.12,  850, 1900, 1800,
     "2020 Panini Prizm Silver Anthony Edwards RC PSA 10",
     "Silver. Wolves face of NBA. SB run boosts."),
    ("P020", "K005", "Basketball", "Red Prizm",             "/299",       "PSA 10",  2800,  0.15, 2200, 4800,  140,
     "2020 Panini Prizm Red Anthony Edwards RC /299 PSA 10",
     "Red /299. Strong numbered float for Ant."),

    # ============================================================
    # Bowman 1st Prospects — Roman Anthony has the hottest chrome
    # ============================================================
    ("P021", "B017", "Baseball", "Refractor",               "unnumbered", "PSA 10",   240,  0.30,  180,  430,  450,
     "2023 Bowman Chrome Prospects Refractor Roman Anthony BCP-120 PSA 10",
     "Refractor. Top-3 farm prospect callup-imminent."),
    ("P022", "B017", "Baseball", "Gold Refractor",          "/50",        "PSA 10",  2200,  0.35, 1700, 3800,  22,
     "2023 Bowman Chrome Prospects Gold Refractor Roman Anthony BCP-120 /50 PSA 10",
     "Gold /50. Best risk:reward in MiLB prospect parallel."),

    # ============================================================
    # Caitlin Clark — WNBA Prizm parallel ladder
    # ============================================================
    ("P023", "K010", "Basketball", "Silver Prizm WNBA",     "unnumbered", "PSA 10",   850,  0.40,  650, 1500,  720,
     "2024 Panini Prizm WNBA Silver Caitlin Clark RC PSA 10",
     "WNBA Silver. Cultural phenomenon. Carries momentum."),
    ("P024", "K010", "Basketball", "Pink Prizm WNBA",       "unnumbered", "PSA 10",  1200,  0.50,  900, 2200,  380,
     "2024 Panini Prizm WNBA Pink Caitlin Clark RC PSA 10",
     "Pink WNBA. Most-collected female athlete card."),

    # ============================================================
    # Cooper Flagg — college parallel scarcity play
    # ============================================================
    ("P025", "K011", "Basketball", "Refractor",             "unnumbered", "PSA 10",   850,  0.65,  650, 1500,  380,
     "2024 Bowman University Chrome Refractor Cooper Flagg PSA 10",
     "Refractor. Pre-NBA-draft moonshot. Top-rated HS PF."),
    ("P026", "K011", "Basketball", "Gold Refractor",        "/50",        "PSA 10",  5500,  0.55, 4200, 9500,  18,
     "2024 Bowman University Chrome Gold Refractor Cooper Flagg /50 PSA 10",
     "Gold /50 Bowman U. The bet of 2025."),

    # ============================================================
    # AUTOGRAPH TIER — National Treasures / Topps Dynasty / Bowman 1st Auto
    # These are the apex parallels. RPAs (Rookie Patch Auto) are 1-of-99 or rarer.
    # ============================================================
    ("P027", "K001", "Basketball", "NT RPA",                 "/99",        "PSA 10", 78000, 0.05, 60000, 120000, 22,
     "2023 Panini National Treasures Victor Wembanyama RPA Auto /99 PSA 10",
     "Wemby NT RPA. The Spurs grail. /99 = scarce. Patch + auto on a single card."),
    ("P028", "F001", "Football", "NT RPA",                   "/99",        "PSA 10", 45000, 0.10, 35000, 75000, 18,
     "2024 Panini National Treasures Caleb Williams RPA Auto /99 PSA 10",
     "Caleb NT RPA. Bears collector base + USC bonus. Apex card."),
    ("P029", "F002", "Football", "NT RPA",                   "/99",        "PSA 10", 32000, 0.20, 25000, 55000, 15,
     "2024 Panini National Treasures Jayden Daniels RPA Auto /99 PSA 10",
     "OROY RPA. Commanders run-up boosts. Apex."),
    ("P030", "F006", "Football", "NT RPA",                   "/99",        "PSA 10", 28000, 0.15, 22000, 48000, 12,
     "2024 Panini National Treasures Marvin Harrison Jr RPA Auto /99 PSA 10",
     "MHJ RPA. HOF dad emotional premium. Apex WR card of class."),
    ("P031", "B001", "Baseball", "Topps Dynasty Auto",       "/10",        "PSA 10", 18000, 0.12, 14000, 32000,  8,
     "2024 Topps Dynasty Paul Skenes Auto /10 PSA 10",
     "Dynasty = MLB equivalent of NT. /10 print. Skenes apex."),
    ("P032", "B017", "Baseball", "Bowman 1st Chrome Auto",   "unnumbered", "PSA 10",   650, 0.40,  480, 1150,  280,
     "2023 Bowman Chrome Prospects Roman Anthony 1st Chrome Auto PSA 10",
     "Bowman 1st Chrome Auto base. Top prospect auto market mover."),
    ("P033", "B015", "Baseball", "Bowman 1st Chrome Auto",   "unnumbered", "PSA 10",   850, 0.30,  650, 1450,  220,
     "2024 Bowman Chrome Prospects Walker Jenkins 1st Chrome Auto PSA 10",
     "Twins #5-pick auto. Strong A-ball production tailwind."),
    ("P034", "B020", "Baseball", "Bowman 1st Chrome Auto",   "/99",        "PSA 10",  1400, 0.50, 1050, 2400,   95,
     "2024 Bowman Chrome Prospects Travis Bazzana 1st Chrome Auto /99 PSA 10",
     "Bazzana #1 overall 2024 Auto /99. Card #BCP-1 collector premium."),
    ("P035", "K011", "Basketball", "Bowman U Chrome Auto",   "unnumbered", "PSA 10",  1200, 0.60,  900, 2100,  240,
     "2024 Bowman University Chrome Cooper Flagg Auto PSA 10",
     "Bowman U Auto. Pre-NBA-draft moonshot. The 2025 chase."),
    ("P036", "F016", "Football", "Bowman U Chrome Auto",     "unnumbered", "PSA 10",   850, 0.50,  650, 1500,  280,
     "2023 Bowman University Chrome Arch Manning Auto PSA 10",
     "Arch's only on-card auto until NFL. Dynasty premium."),
]

PARALLEL_COLS = {
    "id": 0, "base_id": 1, "sport": 2, "parallel_name": 3, "print_run": 4,
    "grade": 5, "price": 6, "trend30d": 7, "t_buy": 8, "t_sell": 9, "pop": 10,
    "ebay_query": 11, "notes": 12,
}


def score_parallel(p: tuple, live_med: float | None) -> dict:
    """Simple scoring: trend + value vs anchor + pop scarcity."""
    (pid, base_id, sport, name, print_run, grade, anchor,
     trend30d, t_buy, t_sell, pop, query, notes) = p

    price = live_med if live_med is not None else anchor
    if t_sell > t_buy:
        value_pct = (t_sell - price) / (t_sell - t_buy)
    else:
        value_pct = 0.5
    value_pct = max(0.0, min(1.0, value_pct))

    momentum = 50 + 250 * trend30d
    momentum = max(0, min(100, momentum))

    # Scarcity from print run
    pr_score = 50  # unnumbered default
    if "/1" in print_run and print_run.strip() == "/1":
        pr_score = 100
    elif "/5" in print_run or "/3" in print_run:
        pr_score = 95
    elif "/10" in print_run:
        pr_score = 90
    elif "/25" in print_run or "/49" in print_run or "/50" in print_run:
        pr_score = 80
    elif "/99" in print_run or "/199" in print_run or "/299" in print_run:
        pr_score = 65
    # Boost by low pop
    if pop and pop < 50:
        pr_score += 10
    pr_score = min(100, pr_score)

    composite = 0.30 * momentum + 0.35 * (100 * value_pct) + 0.35 * pr_score
    composite = max(0.0, min(100.0, composite))
    verdict = ("STRONG BUY" if composite >= 85 else
               "BUY" if composite >= 70 else
               "HOLD" if composite >= 50 else
               "TRIM" if composite >= 30 else "SELL")

    return {
        "id": pid,
        "base_id": base_id,
        "composite": round(composite, 1),
        "momentum": round(momentum, 1),
        "value": round(100 * value_pct, 1),
        "scarcity": round(pr_score, 1),
        "verdict": verdict,
        "live_price": live_med,
    }
