"""
Generate signals.json from the watchlist + live prices.

Produces a small public JSON consumed by the bpleone.com/sports-cards/ landing.
Refreshed on every eBay price refresh cycle (or manually via `python build_signals.py`).

Output schema:
{
  "generated_at": "2026-05-15T05:00:00Z",
  "card_count": 98,
  "verdict_counts": {"STRONG BUY": 0, "BUY": 9, "HOLD": 66, "TRIM": 23, "SELL": 0},
  "top_buys": [
    {"id":"F023","player":"Bryce Underwood","sport":"Football",
     "set_year":"2025 Panini Prizm Draft Picks","grade":"PSA 10",
     "anchor":95,"live":null,"trend30d":60,"pop":300,"verdict":"BUY","composite":76.2}
  ]
}
"""
from __future__ import annotations

import json
from datetime import datetime
from pathlib import Path

from cards_data import CARDS
from quant_score import score_all

COL = {"id":0,"sport":1,"category":2,"tier":3,"player":4,"set_year":5,"card_num":6,"grade":7,
       "price":8,"trend30d":9,"t_buy":10,"t_sell":11,"horizon":12,"conf":13,"pop":14,
       "ebay_query":15,"psa_url":16,"notes":17}


def build(live_prices_path: str = "live_prices.json", out_path: str = "docs/signals.json", top_n: int = 12) -> dict:
    live = {}
    p = Path(live_prices_path)
    if p.exists():
        try:
            live = json.loads(p.read_text(encoding="utf-8")).get("prices", {})
        except Exception:
            pass

    scores = score_all(CARDS, live)

    verdict_counts = {"STRONG BUY": 0, "BUY": 0, "HOLD": 0, "TRIM": 0, "SELL": 0}
    for s in scores:
        if s.verdict in verdict_counts:
            verdict_counts[s.verdict] += 1

    top = [s for s in scores if s.verdict in ("STRONG BUY", "BUY")][:top_n]
    top_buys = []
    for s in top:
        card = next(c for c in CARDS if c[COL["id"]] == s.card_id)
        top_buys.append({
            "id": card[COL["id"]],
            "player": card[COL["player"]],
            "sport": card[COL["sport"]],
            "set_year": card[COL["set_year"]],
            "grade": card[COL["grade"]],
            "anchor": card[COL["price"]],
            "live": s.live_price,
            "trend30d": round(card[COL["trend30d"]] * 100, 1),
            "t_buy": card[COL["t_buy"]],
            "t_sell": card[COL["t_sell"]],
            "pop": card[COL["pop"]],
            "verdict": s.verdict,
            "composite": s.composite,
            "ebay_query": card[COL["ebay_query"]],
        })

    payload = {
        "generated_at": datetime.utcnow().isoformat(timespec="seconds") + "Z",
        "card_count": len(CARDS),
        "live_count": len(live),
        "verdict_counts": verdict_counts,
        "top_buys": top_buys,
    }

    out = Path(out_path)
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(payload, indent=2), encoding="utf-8")
    print(f"[build_signals] wrote {len(top_buys)} top buys to {out_path} | verdicts: {verdict_counts}")
    return payload


if __name__ == "__main__":
    build()
