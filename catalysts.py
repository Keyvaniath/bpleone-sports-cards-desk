"""
Catalysts calendar — known events that move sports card prices.

Manually curated. Update quarterly.

Schema:
  date_iso, sport, kind, title, players_affected (list of card_ids),
  expected_move, notes

kind ∈ {"draft", "release", "season", "trade_window", "playoff", "hall_of_fame", "award"}
"""

# 2026 sports calendar — events with known card-price effects
CATALYSTS = [
    # NFL
    ("2026-04-23", "Football", "draft", "2026 NFL Draft Day 1",
     ["F021", "F022", "F023", "F018", "F016"],
     "+15% to +60%",
     "Top prospects with college autos see immediate re-rate when drafted to a market. "
     "Bears/Lions/Giants picks pop hardest."),
    ("2026-09-04", "Football", "season", "NFL Season Opener",
     ["F001", "F002", "F003", "F004", "F006", "F007", "F008"],
     "+5% to +20%",
     "Rookie hype peaks Week 1; veterans rotate in based on TD prop hits."),
    ("2026-12-11", "Football", "award", "Heisman Trophy Ceremony",
     ["F016", "F018", "F021"],
     "+10% to +40%",
     "Heisman winner card spikes 30-50% same week. Travis Hunter's RC was up 38% week of."),

    # NBA
    ("2026-05-13", "Basketball", "playoff", "NBA Playoff Conference Finals",
     ["K001", "K005", "K003", "K008"],
     "+8% to +20%",
     "Wemby/Ant/JDub deep playoff runs spike cards. Game-winners trigger 10-20% pops."),
    ("2026-05-25", "Basketball", "draft", "2026 NBA Draft Lottery",
     ["K011", "K014"],
     "+10% to +30%",
     "Cooper Flagg / AJ Dybantsa landing spots determine card trajectory. "
     "Top-3 market (e.g. Wizards/Hornets) moves cards less than top-5 to a big market."),
    ("2026-06-23", "Basketball", "draft", "2026 NBA Draft",
     ["K011", "K014"],
     "+20% to +60%",
     "Draft day is the catalyst. Cooper Flagg #1 = expected. Anything else = volatility."),

    # MLB
    ("2026-07-30", "Baseball", "trade_window", "MLB Trade Deadline",
     ["B003", "B004", "B008", "B017"],
     "±10% to ±30%",
     "Star trades re-rate cards. Vlad Jr. trade rumors create volatility. "
     "Prospect call-ups (Roman Anthony likely H2) move BCP-120 +20%."),
    ("2026-09-28", "Baseball", "season", "MLB Regular Season Ends",
     ["B001", "B005", "B012", "B029", "B031"],
     "+5% to +15%",
     "MVP/Cy Young races settle. Skenes Cy = +20%."),
    ("2026-10-27", "Baseball", "playoff", "World Series Game 1",
     ["B007", "B009", "B012"],
     "+15% to +50%",
     "WS appearance moves base RC 20-30%. WS MVP = +50%."),

    # College
    ("2026-08-23", "Football", "season", "College Football Season Opener",
     ["F016", "F017", "F018", "F021", "F022", "F023"],
     "+10% to +25%",
     "Arch Manning's debut as Texas starter is the big catalyst. NIL autos spike."),
    ("2026-11-15", "Basketball", "season", "College Basketball Top-25 Matchups",
     ["K011", "K014"],
     "+5% to +20%",
     "Cooper Flagg's nationally-televised games are catalysts. Duke schedule = print money."),

    # PSA / Grading
    ("2026-04-15", "Other", "release", "PSA Q1 Pop Report Update",
     [],
     "varies",
     "Pop changes shift scarcity scores. Newly-low-pop cards re-rate. "
     "Quarterly update — fold into trend30d analysis."),

    # Releases
    ("2026-06-19", "Baseball", "release", "2026 Bowman Chrome Drops",
     [],
     "Dilutes existing prospect inventory",
     "New 1st Chrome year. 2026 prospect autos (Eli Willits #1 pick, etc.) flood market. "
     "Existing 2024/2025 1st Chrome cards see -5% to -10% week of release."),
    ("2026-12-04", "Football", "release", "2026 Panini National Treasures Football",
     ["F001", "F002", "F006"],
     "+15% to +30% (when announced)",
     "NT RPAs for Caleb/Jayden/MHJ are the apex. Box odds publicly released = pre-order frenzy."),
]
