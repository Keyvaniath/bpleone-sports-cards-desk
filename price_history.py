"""
Append-only price history for the Sports Cards desk.

Each call to `append_snapshot()` reads `live_prices.json` and appends one
JSON row per card to `price_history.jsonl`. Streamlit can then chart trend
lines per card.

Schema (one JSON object per line):
  {"card_id": "F001", "date": "2026-05-14", "median": 220.0, "n": 8, "source": "ebay"}
"""
from __future__ import annotations

import json
from datetime import date
from pathlib import Path

HISTORY_PATH = Path("price_history.jsonl")


def append_snapshot(live_prices_path: str = "live_prices.json", today: str | None = None) -> int:
    """Append today's price snapshot. Returns count written."""
    p = Path(live_prices_path)
    if not p.exists():
        return 0
    try:
        data = json.loads(p.read_text(encoding="utf-8"))
    except Exception:
        return 0
    prices = data.get("prices", {}) or {}
    today = today or date.today().isoformat()
    n = 0
    with HISTORY_PATH.open("a", encoding="utf-8") as f:
        for cid, info in prices.items():
            row = {
                "card_id": cid,
                "date": today,
                "median": info.get("median"),
                "n": info.get("n_samples"),
                "source": info.get("source"),
            }
            f.write(json.dumps(row) + "\n")
            n += 1
    return n


def load_history(card_id: str | None = None) -> list[dict]:
    """Load history rows. If card_id given, filter to that card."""
    if not HISTORY_PATH.exists():
        return []
    out = []
    with HISTORY_PATH.open(encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            try:
                row = json.loads(line)
            except Exception:
                continue
            if card_id is None or row.get("card_id") == card_id:
                out.append(row)
    out.sort(key=lambda r: r.get("date") or "")
    return out


def latest_per_card() -> dict[str, dict]:
    """Latest row for each card."""
    out: dict[str, dict] = {}
    for row in load_history():
        out[row["card_id"]] = row
    return out


def trend(card_id: str, days: int = 30) -> float | None:
    """Compute % change in median over last `days` of history.
    Returns None if not enough data."""
    rows = load_history(card_id)
    if len(rows) < 2:
        return None
    latest = rows[-1]["median"]
    # Find row from `days` ago (or oldest within window)
    from datetime import datetime, timedelta
    cutoff = datetime.fromisoformat(rows[-1]["date"]) - timedelta(days=days)
    earlier = None
    for r in rows:
        try:
            d = datetime.fromisoformat(r["date"])
        except Exception:
            continue
        if d <= cutoff:
            earlier = r["median"]
    if earlier is None:
        # Fall back to oldest sample
        earlier = rows[0]["median"]
    if earlier is None or latest is None or earlier <= 0:
        return None
    return (latest - earlier) / earlier


if __name__ == "__main__":
    import sys
    if len(sys.argv) > 1 and sys.argv[1] == "snapshot":
        n = append_snapshot()
        print(f"[price_history] wrote {n} rows for {date.today().isoformat()}")
    else:
        # Default: dump all history
        rows = load_history()
        print(f"[price_history] {len(rows)} rows in {HISTORY_PATH}")
