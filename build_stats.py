"""
Generate stats.json — public summary of the watchlist.

Companion to build_signals.py. Provides aggregate breakdowns that the
landing page (or any third party) can pull for stats widgets.
"""
from __future__ import annotations

import json
from collections import Counter, defaultdict
from datetime import datetime
from pathlib import Path

from cards_data import CARDS
from quant_score import score_all
from parallels import PARALLELS
from sealed_products import SEALED
from catalysts import CATALYSTS
from vintage_matrix import VINTAGE_LADDER

COL = {"id":0,"sport":1,"category":2,"tier":3,"player":4,"set_year":5,"card_num":6,"grade":7,
       "price":8,"trend30d":9,"t_buy":10,"t_sell":11,"horizon":12,"conf":13,"pop":14,
       "ebay_query":15,"psa_url":16,"notes":17}


def build(out_path: str = "docs/stats.json") -> dict:
    live_prices = {}
    p = Path("live_prices.json")
    if p.exists():
        try:
            live_prices = json.loads(p.read_text(encoding="utf-8")).get("prices", {})
        except Exception:
            pass

    scores = score_all(CARDS, live_prices)
    by_id = {s.card_id: s for s in scores}

    # Per-sport breakdown
    by_sport = defaultdict(lambda: {"count": 0, "book_value": 0, "buys": 0, "avg_score": 0.0, "trend30d_avg": 0.0})
    for c in CARDS:
        sport = c[COL["sport"]]
        s = by_id.get(c[COL["id"]])
        b = by_sport[sport]
        b["count"] += 1
        b["book_value"] += c[COL["price"]]
        if s and s.verdict.endswith("BUY"):
            b["buys"] += 1
        if s:
            b["avg_score"] += s.composite
        b["trend30d_avg"] += c[COL["trend30d"]]
    for sport, b in by_sport.items():
        b["avg_score"] = round(b["avg_score"] / max(1, b["count"]), 1)
        b["trend30d_avg"] = round(b["trend30d_avg"] * 100 / max(1, b["count"]), 1)

    # Per-tier breakdown
    tier_counts = dict(Counter(c[COL["tier"]] for c in CARDS))

    # Top gainers / losers by trend30d
    sorted_by_trend = sorted(CARDS, key=lambda c: c[COL["trend30d"]], reverse=True)
    gainers = [
        {"id": c[COL["id"]], "player": c[COL["player"]], "trend30d": round(c[COL["trend30d"]] * 100, 1)}
        for c in sorted_by_trend[:5]
    ]
    losers = [
        {"id": c[COL["id"]], "player": c[COL["player"]], "trend30d": round(c[COL["trend30d"]] * 100, 1)}
        for c in sorted_by_trend[-5:]
    ]

    # Verdict counts
    verdict_counts = dict(Counter(s.verdict for s in scores))

    # Upcoming catalysts (next 30 days)
    today = datetime.now().date()
    upcoming = []
    for c in CATALYSTS:
        try:
            d = datetime.fromisoformat(c[0]).date()
            days_out = (d - today).days
            if 0 <= days_out <= 30:
                upcoming.append({
                    "date": c[0], "days_out": days_out,
                    "sport": c[1], "kind": c[2], "title": c[3],
                    "expected_move": c[5],
                })
        except Exception:
            pass

    payload = {
        "generated_at": datetime.utcnow().isoformat(timespec="seconds") + "Z",
        "card_count": len(CARDS),
        "parallel_count": len(PARALLELS),
        "sealed_count": len(SEALED),
        "vintage_grade_count": len(VINTAGE_LADDER),
        "catalyst_count": len(CATALYSTS),
        "total_book_value": sum(c[COL["price"]] for c in CARDS),
        "verdict_counts": verdict_counts,
        "by_sport": dict(by_sport),
        "by_tier": tier_counts,
        "top_gainers_30d": gainers,
        "top_losers_30d": losers,
        "upcoming_catalysts": upcoming,
    }

    out = Path(out_path)
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(payload, indent=2), encoding="utf-8")
    print(f"[build_stats] wrote stats.json — {len(CARDS)} cards, {sum(b['buys'] for b in by_sport.values())} BUYs, {len(upcoming)} upcoming catalysts")
    return payload


if __name__ == "__main__":
    build()
