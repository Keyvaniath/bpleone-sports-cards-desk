"""
Discord webhook alerts for the Sports Cards desk.

Compares the latest scores against a snapshot of the previous run and posts:
  - Any flips into STRONG BUY (cards crossing 85 composite)
  - Any newly-actionable BUY signals
  - Any flips into TRIM / SELL (de-risk warnings)

Setup:
  1. Create a Discord webhook (Server Settings -> Integrations -> Webhooks)
  2. Set $env:DISCORD_WEBHOOK_URL = "https://discord.com/api/webhooks/..."
  3. Run `python discord_alert.py` (cron weekly after the eBay refresh)

State stored in `score_snapshot.json` so we only alert on transitions.
"""
from __future__ import annotations

import json
import os
import sys
from datetime import datetime
from pathlib import Path

import requests

from cards_data import CARDS
from quant_score import score_all

WEBHOOK_URL = os.environ.get("DISCORD_WEBHOOK_URL", "").strip()
SNAPSHOT_PATH = "score_snapshot.json"


def load_snapshot() -> dict:
    p = Path(SNAPSHOT_PATH)
    if not p.exists():
        return {}
    try:
        return json.loads(p.read_text(encoding="utf-8")).get("verdicts", {})
    except Exception:
        return {}


def save_snapshot(scores: list) -> None:
    Path(SNAPSHOT_PATH).write_text(json.dumps({
        "snapshot_at": datetime.utcnow().isoformat() + "Z",
        "verdicts": {s.card_id: s.verdict for s in scores},
        "composites": {s.card_id: s.composite for s in scores},
    }, indent=2), encoding="utf-8")


def detect_flips(scores: list, prior: dict) -> dict:
    promotions = []   # to STRONG BUY or BUY
    demotions = []    # to TRIM or SELL
    for s in scores:
        old = prior.get(s.card_id, "HOLD")
        if old == s.verdict:
            continue
        if s.verdict in ("STRONG BUY", "BUY") and old not in ("STRONG BUY", "BUY"):
            promotions.append((s, old))
        if s.verdict in ("TRIM", "SELL") and old not in ("TRIM", "SELL"):
            demotions.append((s, old))
    return {"promotions": promotions, "demotions": demotions}


def _card_meta(card_id: str) -> dict:
    card = next((c for c in CARDS if c[0] == card_id), None)
    if not card:
        return {}
    return {
        "id": card[0], "sport": card[1], "player": card[4],
        "set_year": card[5], "card_num": card[6], "grade": card[7],
        "ebay_query": card[15],
    }


def _embed(score, old_verdict: str, kind: str) -> dict:
    """Build a Discord embed for one signal flip."""
    meta = _card_meta(score.card_id)
    color = 0x4ade80 if kind == "promotion" else 0xfb923c
    title = f"{score.verdict}: {meta.get('player','?')}"
    desc = f"**{meta.get('sport','?')}** · {meta.get('set_year','?')} · #{meta.get('card_num','?')} · {meta.get('grade','?')}"
    fields = [
        {"name": "Composite", "value": f"{score.composite:.1f}", "inline": True},
        {"name": "Was", "value": old_verdict, "inline": True},
        {"name": "Live $", "value": f"${score.live_price:,.0f}" if score.live_price else "—", "inline": True},
        {"name": "Sub-scores", "value": f"M{score.momentum:.0f} / V{score.value:.0f} / S{score.scarcity:.0f} / L{score.liquidity:.0f}", "inline": False},
    ]
    ebay_url = f"https://www.ebay.com/sch/i.html?_nkw={meta.get('ebay_query','').replace(' ','+')}&LH_Sold=1&LH_Complete=1"
    return {
        "title": title,
        "description": desc,
        "url": ebay_url,
        "color": color,
        "fields": fields,
        "footer": {"text": f"Card {score.card_id} · sports-cards.bpleone.com"},
    }


def post(text: str, embeds: list[dict] | None = None) -> bool:
    if not WEBHOOK_URL:
        print("[discord_alert] no DISCORD_WEBHOOK_URL set — skipping", file=sys.stderr)
        return False
    payload = {"content": text}
    if embeds:
        payload["embeds"] = embeds[:10]  # Discord caps at 10 embeds per message
    try:
        r = requests.post(WEBHOOK_URL, json=payload, timeout=15)
        return r.status_code in (200, 204)
    except Exception as e:
        print(f"[discord_alert] {e}", file=sys.stderr)
        return False


def main():
    # Load latest live prices
    live_prices: dict = {}
    lp_path = Path("live_prices.json")
    if lp_path.exists():
        try:
            live_prices = json.loads(lp_path.read_text(encoding="utf-8")).get("prices", {})
        except Exception:
            pass

    scores = score_all(CARDS, live_prices)
    prior = load_snapshot()
    flips = detect_flips(scores, prior)

    promos = flips["promotions"]
    demos = flips["demotions"]

    if not prior:
        # First run — just save snapshot, no alerts
        save_snapshot(scores)
        print("[discord_alert] no prior snapshot — recorded baseline, exiting")
        return

    if not promos and not demos:
        save_snapshot(scores)
        print("[discord_alert] no flips this cycle")
        return

    # Build the message
    lines = ["🏆 **Sports Cards Desk — signal update**"]
    if promos:
        strong = [s for s, _ in promos if s.verdict == "STRONG BUY"]
        if strong:
            lines.append(f"🔥 **{len(strong)} STRONG BUY** signal(s)")
        any_buy = [s for s, _ in promos if s.verdict == "BUY"]
        if any_buy:
            lines.append(f"📈 {len(any_buy)} new BUY signal(s)")
    if demos:
        lines.append(f"📉 {len(demos)} TRIM/SELL warning(s)")
    text = "\n".join(lines)

    embeds = []
    for s, old in (promos + demos)[:10]:
        kind = "promotion" if s.verdict in ("STRONG BUY", "BUY") else "demotion"
        embeds.append(_embed(s, old, kind))

    posted = post(text, embeds=embeds)
    if posted:
        save_snapshot(scores)
        print(f"[discord_alert] posted {len(promos)} promotions, {len(demos)} demotions")
    else:
        print("[discord_alert] post failed; snapshot NOT updated so we'll retry next cycle", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
