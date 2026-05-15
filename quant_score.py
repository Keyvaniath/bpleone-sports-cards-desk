"""
Composite quant score for the Sports Cards desk.

Mirrors the Pokemon TCG desk methodology, adapted for sports:

  COMPOSITE = 0.30 * MOMENTUM
            + 0.30 * VALUE
            + 0.20 * SCARCITY
            + 0.20 * LIQUIDITY

Each sub-score is 0-100. Higher = stronger BUY signal.

  MOMENTUM   from 30d trend in cards_data + recent eBay median delta
  VALUE      live_median vs t_buy / t_sell anchors
  SCARCITY   PSA pop at this grade (lower = scarcer = higher score)
  LIQUIDITY  n_samples in last 30 days of eBay sold comps

Verdict ladder, anchored to the COMPOSITE:
  >= 85   STRONG BUY
  70-84   BUY
  50-69   HOLD
  30-49   TRIM
  < 30    SELL
"""
from __future__ import annotations

from dataclasses import dataclass


@dataclass
class CardScore:
    card_id: str
    composite: float
    verdict: str
    momentum: float
    value: float
    scarcity: float
    liquidity: float
    live_price: float | None
    spread_to_buy: float | None     # % above buy zone (negative = below = STRONG BUY)
    spread_to_sell: float | None    # % below sell zone (negative = above = TRIM/SELL)


def _clip(x: float, lo: float = 0.0, hi: float = 100.0) -> float:
    return max(lo, min(hi, x))


def _momentum_score(trend30d: float, live_med: float | None, anchor: float) -> float:
    """Trend in cards_data is hand-curated; we cross-check vs live median if available.
    Score = 50 + 250 * trend30d, with a small bonus/penalty if live > or < anchor."""
    score = 50.0 + 250.0 * trend30d
    if live_med and anchor and anchor > 0:
        live_delta = (live_med - anchor) / anchor
        # If live is +10% above anchor, add ~10 points to momentum
        score += 100.0 * live_delta
    return _clip(score)


def _value_score(live_med: float | None, t_buy: float, t_sell: float, anchor: float) -> float:
    """Score 0-100 by where live_med sits between t_buy and t_sell.
       At t_buy: 100 (perfect entry)
       At anchor: 50 (fair)
       At t_sell: 0 (at exit)
       Below t_buy: > 100 (clamped to 100)
       Above t_sell: < 0 (clamped to 0)"""
    price = live_med if live_med is not None else anchor
    if t_sell == t_buy:
        return 50.0
    # Linear interp: t_buy -> 100, t_sell -> 0
    pct = (t_sell - price) / (t_sell - t_buy)
    return _clip(100.0 * pct)


def _scarcity_score(pop: int) -> float:
    """Pop counts vary wildly across grades. Use log-style bins:
         <100  : 95  (institutional)
         <500  : 80
         <1500 : 60
         <3000 : 40
         <6000 : 25
         else  : 15"""
    if pop is None:
        return 30.0
    if pop < 100:
        return 95.0
    if pop < 500:
        return 80.0
    if pop < 1500:
        return 60.0
    if pop < 3000:
        return 40.0
    if pop < 6000:
        return 25.0
    return 15.0


def _liquidity_score(n_samples: int | None) -> float:
    """How easy is it to actually exit? 0-100 from recent sold-comp count:
         >= 8 : 95 (very liquid)
         >= 5 : 80
         >= 3 : 60
         >= 2 : 40
         == 1 : 20
         none : 10"""
    if not n_samples:
        return 10.0
    if n_samples >= 8:
        return 95.0
    if n_samples >= 5:
        return 80.0
    if n_samples >= 3:
        return 60.0
    if n_samples >= 2:
        return 40.0
    return 20.0


def _verdict(composite: float) -> str:
    if composite >= 85:
        return "STRONG BUY"
    if composite >= 70:
        return "BUY"
    if composite >= 50:
        return "HOLD"
    if composite >= 30:
        return "TRIM"
    return "SELL"


def score_card(card: tuple, live: dict | None) -> CardScore:
    """`card` is a row from CARDS. `live` is the matching entry in live_prices.json (or None)."""
    (cid, sport, category, tier, player, set_year, card_num, grade,
     anchor, trend30d, t_buy, t_sell, horizon, conf, pop, ebay_q, psa_url, notes) = card

    live_med = (live or {}).get("median") if live else None
    n_samples = (live or {}).get("n_samples") if live else 0

    momentum = _momentum_score(trend30d, live_med, anchor)
    value = _value_score(live_med, t_buy, t_sell, anchor)
    scarcity = _scarcity_score(pop)
    liquidity = _liquidity_score(n_samples)

    composite = 0.30 * momentum + 0.30 * value + 0.20 * scarcity + 0.20 * liquidity
    composite = _clip(composite)
    verdict = _verdict(composite)

    # Conviction multiplier nudges the verdict — high-conviction cards get +5, low get -5
    if conf and conf >= 5:
        composite = _clip(composite + 5)
    elif conf and conf <= 2:
        composite = _clip(composite - 5)
    verdict = _verdict(composite)

    spread_to_buy = None
    spread_to_sell = None
    if live_med:
        spread_to_buy = (live_med - t_buy) / t_buy * 100
        spread_to_sell = (t_sell - live_med) / t_sell * 100

    return CardScore(
        card_id=cid,
        composite=round(composite, 1),
        verdict=verdict,
        momentum=round(momentum, 1),
        value=round(value, 1),
        scarcity=round(scarcity, 1),
        liquidity=round(liquidity, 1),
        live_price=round(live_med, 2) if live_med else None,
        spread_to_buy=round(spread_to_buy, 1) if spread_to_buy is not None else None,
        spread_to_sell=round(spread_to_sell, 1) if spread_to_sell is not None else None,
    )


def score_all(cards: list[tuple], live_prices: dict) -> list[CardScore]:
    """Returns scores sorted by composite descending (best buys first)."""
    out = []
    for card in cards:
        cid = card[0]
        live = live_prices.get(cid)
        out.append(score_card(card, live))
    out.sort(key=lambda s: s.composite, reverse=True)
    return out
