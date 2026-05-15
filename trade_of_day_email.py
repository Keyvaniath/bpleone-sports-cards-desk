"""
Trade-of-the-day email digest for the Sports Cards desk.

Picks the single highest-composite BUY each morning, plus a runner-up and any
TRIM warnings. Sends via SMTP (Gmail app password recommended).

Env vars:
  SMTP_USER          your Gmail
  SMTP_PASSWORD      Gmail app password
  EMAIL_TO           recipient (defaults to SMTP_USER)
"""
from __future__ import annotations

import json
import os
import smtplib
import sys
from datetime import date
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from pathlib import Path

from cards_data import CARDS
from quant_score import score_all

SMTP_HOST = "smtp.gmail.com"
SMTP_PORT = 587


def load_live_prices() -> dict:
    p = Path("live_prices.json")
    if not p.exists():
        return {}
    try:
        return json.loads(p.read_text(encoding="utf-8")).get("prices", {})
    except Exception:
        return {}


def card_meta(card_id: str) -> dict:
    card = next((c for c in CARDS if c[0] == card_id), None)
    if not card:
        return {}
    return {
        "id": card[0], "sport": card[1], "category": card[2], "tier": card[3],
        "player": card[4], "set_year": card[5], "card_num": card[6], "grade": card[7],
        "anchor": card[8], "t_buy": card[10], "t_sell": card[11],
        "horizon": card[12], "conf": card[13], "pop": card[14],
        "ebay_query": card[15], "psa_url": card[16], "notes": card[17],
    }


def render_html(top_buy, runner_up, trims) -> str:
    """Render a clean HTML email."""
    def card_section(s, title):
        meta = card_meta(s.card_id)
        ebay = f"https://www.ebay.com/sch/i.html?_nkw={meta['ebay_query'].replace(' ','+')}&LH_Sold=1&LH_Complete=1"
        live = f"${s.live_price:,.0f}" if s.live_price else "—"
        return f"""
        <div style="background:#131826;border:1px solid #232a3e;border-radius:8px;padding:18px;margin:12px 0;">
          <div style="color:#f5c842;font-family:monospace;font-size:11px;letter-spacing:0.1em;text-transform:uppercase;">{title}</div>
          <h2 style="color:#e8ecf4;margin:6px 0 2px;font-size:22px;">{meta['player']} — <span style="color:#8b94a8">{s.verdict}</span></h2>
          <div style="color:#8b94a8;font-size:13px;">{meta['sport']} · {meta['set_year']} #{meta['card_num']} · {meta['grade']} · Tier {meta['tier']}</div>
          <div style="display:flex;gap:24px;margin-top:14px;">
            <div><div style="color:#8b94a8;font-size:11px;text-transform:uppercase;">Anchor</div><div style="color:#e8ecf4;font-weight:600">${meta['anchor']:,.0f}</div></div>
            <div><div style="color:#8b94a8;font-size:11px;text-transform:uppercase;">Live</div><div style="color:#e8ecf4;font-weight:600">{live}</div></div>
            <div><div style="color:#8b94a8;font-size:11px;text-transform:uppercase;">Buy / Sell</div><div style="color:#e8ecf4;font-weight:600">${meta['t_buy']:,.0f} / ${meta['t_sell']:,.0f}</div></div>
            <div><div style="color:#8b94a8;font-size:11px;text-transform:uppercase;">Score</div><div style="color:#4ade80;font-weight:700;font-size:18px;">{s.composite:.1f}</div></div>
          </div>
          <div style="margin-top:14px;color:#8b94a8;font-size:13px;line-height:1.5;">{meta['notes']}</div>
          <div style="margin-top:14px;">
            <a href="{ebay}" style="background:#f5c842;color:#0a0e1a;padding:8px 16px;border-radius:6px;text-decoration:none;font-weight:700;font-size:13px;">View eBay sold comps →</a>
          </div>
        </div>"""

    sections = [card_section(top_buy, "Trade of the Day")] if top_buy else []
    if runner_up:
        sections.append(card_section(runner_up, "Runner-Up"))

    trim_html = ""
    if trims:
        trim_rows = ""
        for s in trims[:3]:
            meta = card_meta(s.card_id)
            trim_rows += f"<li style='color:#fb923c;margin:6px 0;'>{meta['player']} ({meta['grade']}) — composite {s.composite:.1f}</li>"
        trim_html = f"""
        <div style="background:#131826;border:1px solid #232a3e;border-left:4px solid #fb923c;border-radius:8px;padding:14px 18px;margin:12px 0;">
          <div style="color:#fb923c;font-family:monospace;font-size:11px;letter-spacing:0.1em;text-transform:uppercase;">De-risk Candidates</div>
          <ul style="margin:8px 0 0;padding-left:18px;">{trim_rows}</ul>
        </div>"""

    return f"""<!doctype html>
<html><body style="background:#0a0e1a;color:#e8ecf4;font-family:-apple-system,BlinkMacSystemFont,sans-serif;padding:20px;">
  <div style="max-width:720px;margin:0 auto;">
    <div style="color:#f5c842;font-family:monospace;font-size:12px;letter-spacing:0.15em;text-transform:uppercase;">bpleone.com · sports cards desk</div>
    <h1 style="color:#e8ecf4;margin:6px 0 14px;font-size:28px;letter-spacing:-0.02em;">Trade of the Day — {date.today().strftime('%a, %b %d')}</h1>
    {"".join(sections)}
    {trim_html}
    <div style="color:#8b94a8;font-size:11px;margin-top:24px;">
      Powered by your quant scoring engine (0.30·momentum + 0.30·value + 0.20·scarcity + 0.20·liquidity).<br/>
      <a href="https://sports-cards.bpleone.com" style="color:#f5c842;">sports-cards.bpleone.com</a> · 98 cards · sealed product · inventory P&amp;L
    </div>
  </div>
</body></html>"""


def main() -> int:
    user = os.environ.get("SMTP_USER", "").strip()
    pwd = os.environ.get("SMTP_PASSWORD", "").strip()
    to = os.environ.get("EMAIL_TO", "").strip() or user
    if not user or not pwd:
        print("[trade_of_day_email] missing SMTP_USER / SMTP_PASSWORD env vars", file=sys.stderr)
        return 1

    live = load_live_prices()
    scores = score_all(CARDS, live)
    buys = [s for s in scores if s.verdict in ("STRONG BUY", "BUY")]
    trims = [s for s in scores if s.verdict in ("TRIM", "SELL")]

    if not buys:
        print("[trade_of_day_email] no BUY signals — skipping")
        return 0

    top_buy = buys[0]
    runner_up = buys[1] if len(buys) > 1 else None

    html = render_html(top_buy, runner_up, trims)
    meta = card_meta(top_buy.card_id)
    subject = f"[Sports Cards] {top_buy.verdict}: {meta['player']} — composite {top_buy.composite:.1f}"

    msg = MIMEMultipart("alternative")
    msg["Subject"] = subject
    msg["From"] = user
    msg["To"] = to
    msg.attach(MIMEText(html, "html"))

    try:
        with smtplib.SMTP(SMTP_HOST, SMTP_PORT) as srv:
            srv.starttls()
            srv.login(user, pwd)
            srv.sendmail(user, [to], msg.as_string())
        print(f"[trade_of_day_email] sent: {subject}")
        return 0
    except Exception as e:
        print(f"[trade_of_day_email] ERR {e}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    sys.exit(main())
