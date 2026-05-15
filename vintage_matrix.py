"""
Vintage HOFer condition matrix — PSA grade-by-grade price ladder.

For the highest-conviction vintage cards, the grade premium varies hugely:
  '52 Topps Mantle PSA 4 ~ $90K   PSA 7 ~ $285K   PSA 8 ~ $1.2M   PSA 9 ~ $5M+

This module surfaces the ladder so Brandon can pick the right entry grade
for his bankroll, then back-fill with higher grades over time.

Schema (one tuple per (card, grade) cell):
  vintage_id, base_id, player, set_year, grade, market_price, n_recent_sales,
  spread_pct (vs next-lower grade), entry_appeal (T1=blue chip / T2=value / T3=spec)
"""

VINTAGE_LADDER = [
    # ============================================================
    # '52 Topps Mickey Mantle
    # ============================================================
    ("VL001", "B025", "Mickey Mantle", "1952 Topps", "PSA 4",  90000,  18, None,  "T2"),
    ("VL002", "B025", "Mickey Mantle", "1952 Topps", "PSA 5", 150000,  12, 0.67,  "T2"),
    ("VL003", "B025", "Mickey Mantle", "1952 Topps", "PSA 6", 195000,   8, 0.30,  "T1"),
    ("VL004", "B025", "Mickey Mantle", "1952 Topps", "PSA 7", 285000,   5, 0.46,  "T1"),
    ("VL005", "B025", "Mickey Mantle", "1952 Topps", "PSA 8",1200000,   2, 3.21,  "T1"),

    # ============================================================
    # '54 Topps Hank Aaron RC
    # ============================================================
    ("VL006", "B026", "Hank Aaron",    "1954 Topps", "PSA 5",  2400,  35, None,  "T3"),
    ("VL007", "B026", "Hank Aaron",    "1954 Topps", "PSA 6",  3800,  22, 0.58,  "T2"),
    ("VL008", "B026", "Hank Aaron",    "1954 Topps", "PSA 7",  7500,  14, 0.97,  "T1"),
    ("VL009", "B026", "Hank Aaron",    "1954 Topps", "PSA 8", 22000,   6, 1.93,  "T1"),
    ("VL010", "B026", "Hank Aaron",    "1954 Topps", "PSA 9",125000,   1, 4.68,  "T1"),

    # ============================================================
    # '55 Topps Roberto Clemente RC
    # ============================================================
    ("VL011", "B027", "Roberto Clemente","1955 Topps","PSA 5", 2000, 32, None, "T3"),
    ("VL012", "B027", "Roberto Clemente","1955 Topps","PSA 6", 3500, 18, 0.75, "T2"),
    ("VL013", "B027", "Roberto Clemente","1955 Topps","PSA 7", 6500, 12, 0.86, "T1"),
    ("VL014", "B027", "Roberto Clemente","1955 Topps","PSA 8",24000,  4, 2.69, "T1"),

    # ============================================================
    # '63 Topps Pete Rose RC
    # ============================================================
    ("VL015", "B028", "Pete Rose",     "1963 Topps", "PSA 6",  1200, 28, None,  "T3"),
    ("VL016", "B028", "Pete Rose",     "1963 Topps", "PSA 7",  2400, 18, 1.00,  "T2"),
    ("VL017", "B028", "Pete Rose",     "1963 Topps", "PSA 8",  4200, 10, 0.75,  "T2"),
    ("VL018", "B028", "Pete Rose",     "1963 Topps", "PSA 9", 18000,  3, 3.29,  "T1"),

    # ============================================================
    # '76 Topps Walter Payton RC
    # ============================================================
    ("VL019", "F026", "Walter Payton", "1976 Topps", "PSA 7",  1400, 24, None,  "T3"),
    ("VL020", "F026", "Walter Payton", "1976 Topps", "PSA 8",  4800, 14, 2.43,  "T1"),
    ("VL021", "F026", "Walter Payton", "1976 Topps", "PSA 9", 16500,  4, 2.44,  "T1"),

    # ============================================================
    # '86 Fleer Michael Jordan RC
    # ============================================================
    ("VL022", "K015", "Michael Jordan", "1986 Fleer", "PSA 7",  6500,  42, None, "T2"),
    ("VL023", "K016", "Michael Jordan", "1986 Fleer", "PSA 9", 16500,  18, 1.54, "T1"),
    ("VL024", "K015", "Michael Jordan", "1986 Fleer", "PSA 10", 290000, 4, 16.6, "T1"),

    # ============================================================
    # '96 Topps Chrome Kobe Bryant RC
    # ============================================================
    ("VL025", "K017", "Kobe Bryant",   "1996 Topps Chrome","PSA 8",   850,  38, None, "T3"),
    ("VL026", "K017", "Kobe Bryant",   "1996 Topps Chrome","PSA 9",  2400,  24, 1.82, "T2"),
    ("VL027", "K017", "Kobe Bryant",   "1996 Topps Chrome","PSA 10", 9500,   8, 2.96, "T1"),

    # ============================================================
    # '03 Topps Chrome LeBron James RC
    # ============================================================
    ("VL028", "K018", "LeBron James",  "2003 Topps Chrome","PSA 9",  3800,  46, None, "T2"),
    ("VL029", "K018", "LeBron James",  "2003 Topps Chrome","PSA 10",35000,  12, 8.21, "T1"),

    # ============================================================
    # '00 Bowman Chrome Tom Brady RC
    # ============================================================
    ("VL030", "F025", "Tom Brady",     "2000 Bowman Chrome","PSA 8",  1400, 32, None, "T3"),
    ("VL031", "F025", "Tom Brady",     "2000 Bowman Chrome","PSA 9",  3200, 18, 1.29, "T2"),
    ("VL032", "F025", "Tom Brady",     "2000 Bowman Chrome","PSA 10", 8500,  6, 1.66, "T1"),

    # ============================================================
    # '79 OPC Wayne Gretzky RC
    # ============================================================
    ("VL033", "X001", "Wayne Gretzky", "1979 O-Pee-Chee", "PSA 6",  4500,  32, None, "T2"),
    ("VL034", "X001", "Wayne Gretzky", "1979 O-Pee-Chee", "PSA 7", 11000,  18, 1.44, "T1"),
    ("VL035", "X001", "Wayne Gretzky", "1979 O-Pee-Chee", "PSA 8", 28000,   8, 1.55, "T1"),
    ("VL036", "X001", "Wayne Gretzky", "1979 O-Pee-Chee", "PSA 9",125000,   2, 3.46, "T1"),
]

VL_COLS = {
    "id": 0, "base_id": 1, "player": 2, "set_year": 3, "grade": 4,
    "market_price": 5, "n_recent": 6, "spread_pct": 7, "entry_appeal": 8,
}
