"""
IRS Schedule D / Form 8949 helper for the Sports Cards desk.

Reads `inventory.json` (positions saved from the Streamlit dashboard) plus
realized sales from `sales.json`, and emits a Schedule D summary plus the
detailed Form 8949 rows for each disposed lot.

Conventions (matches Pokemon desk's tax_report.py):

  inventory.json — open positions
    { "B001": {"qty": 1, "cost": 280.0, "buy_date": "2026-05-01"}, ... }

  sales.json     — closed lots (manual entry when a card sells)
    [
      {"card_id": "B001", "qty": 1, "cost": 280.0, "buy_date": "2026-05-01",
       "sell_date": "2026-09-15", "proceeds": 425.0, "fees": 25.50}
    ]

Holding period:
  - ≥1 year between buy_date and sell_date → long-term (28% collectibles rate)
  - <1 year → short-term (ordinary income)

NOTE: cards are "collectibles" under §408(m)(2)(A), capped at 28% LTCG rate.
"""
from __future__ import annotations

import json
from dataclasses import dataclass
from datetime import date, datetime
from pathlib import Path

LONG_TERM_RATE = 0.28
SHORT_TERM_RATE = 0.37  # top ordinary income rate; adjust to your bracket


@dataclass
class Lot:
    card_id: str
    qty: int
    cost_basis: float
    proceeds: float
    fees: float
    buy_date: date
    sell_date: date
    holding_days: int
    is_long_term: bool
    gain_loss: float


def _parse_date(s: str) -> date:
    return datetime.fromisoformat(s.split("T")[0]).date()


def load_sales(path: str = "sales.json") -> list[dict]:
    p = Path(path)
    if not p.exists():
        return []
    try:
        return json.loads(p.read_text(encoding="utf-8"))
    except Exception:
        return []


def compute_lots(sales: list[dict]) -> list[Lot]:
    out: list[Lot] = []
    for s in sales:
        buy_d = _parse_date(s["buy_date"])
        sell_d = _parse_date(s["sell_date"])
        days = (sell_d - buy_d).days
        proceeds = float(s.get("proceeds", 0)) * int(s.get("qty", 1))
        fees = float(s.get("fees", 0))
        cost = float(s.get("cost", 0)) * int(s.get("qty", 1))
        net_proceeds = proceeds - fees
        out.append(Lot(
            card_id=s["card_id"],
            qty=int(s.get("qty", 1)),
            cost_basis=cost,
            proceeds=net_proceeds,
            fees=fees,
            buy_date=buy_d,
            sell_date=sell_d,
            holding_days=days,
            is_long_term=(days >= 365),
            gain_loss=net_proceeds - cost,
        ))
    return out


def schedule_d_summary(lots: list[Lot]) -> dict:
    st_lots = [l for l in lots if not l.is_long_term]
    lt_lots = [l for l in lots if l.is_long_term]
    st_gain = sum(l.gain_loss for l in st_lots)
    lt_gain = sum(l.gain_loss for l in lt_lots)
    return {
        "short_term": {
            "lots": len(st_lots),
            "proceeds": round(sum(l.proceeds for l in st_lots), 2),
            "cost_basis": round(sum(l.cost_basis for l in st_lots), 2),
            "gain_loss": round(st_gain, 2),
            "est_tax": round(max(0, st_gain) * SHORT_TERM_RATE, 2),
        },
        "long_term": {
            "lots": len(lt_lots),
            "proceeds": round(sum(l.proceeds for l in lt_lots), 2),
            "cost_basis": round(sum(l.cost_basis for l in lt_lots), 2),
            "gain_loss": round(lt_gain, 2),
            "est_tax": round(max(0, lt_gain) * LONG_TERM_RATE, 2),
            "rate_note": "Collectibles cap (28%) applies to cards under IRC §408(m)(2)(A)",
        },
        "total_gain_loss": round(st_gain + lt_gain, 2),
        "total_est_tax": round(max(0, st_gain) * SHORT_TERM_RATE + max(0, lt_gain) * LONG_TERM_RATE, 2),
    }


def form_8949_rows(lots: list[Lot]) -> list[dict]:
    """Emits rows in Form 8949 layout."""
    rows = []
    for l in lots:
        rows.append({
            "description": f"Sports card lot {l.card_id} (qty {l.qty})",
            "date_acquired": l.buy_date.isoformat(),
            "date_sold": l.sell_date.isoformat(),
            "proceeds": round(l.proceeds, 2),
            "cost_basis": round(l.cost_basis, 2),
            "gain_loss": round(l.gain_loss, 2),
            "term": "Long" if l.is_long_term else "Short",
        })
    rows.sort(key=lambda r: r["date_sold"])
    return rows


if __name__ == "__main__":
    import sys
    sales = load_sales()
    if not sales:
        print("No sales found in sales.json. Add disposed lots to begin tax reporting.")
        sys.exit(0)
    lots = compute_lots(sales)
    summary = schedule_d_summary(lots)
    rows = form_8949_rows(lots)
    print("=" * 60)
    print("SCHEDULE D SUMMARY")
    print("=" * 60)
    print(json.dumps(summary, indent=2))
    print()
    print("=" * 60)
    print("FORM 8949 ROWS")
    print("=" * 60)
    for r in rows:
        print(f"  {r['date_sold']}  {r['description']:40s}  proceeds ${r['proceeds']:>8,.2f}  basis ${r['cost_basis']:>8,.2f}  G/L ${r['gain_loss']:+,.2f}  ({r['term']})")
