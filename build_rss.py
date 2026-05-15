"""
Generate an RSS feed of current BUY signals so anyone can subscribe.

Output: docs/feed.xml
Refreshed alongside signals.json + stats.json on each weekly cycle.
"""
from __future__ import annotations

import json
import xml.sax.saxutils as sax
from datetime import datetime, timezone
from email.utils import format_datetime
from pathlib import Path


SITE = "https://bpleone.com/sports-cards/"
FEED_URL = "https://raw.githubusercontent.com/Keyvaniath/bpleone-sports-cards-desk/main/docs/feed.xml"


def build(signals_path: str = "docs/signals.json", out_path: str = "docs/feed.xml") -> str:
    sp = Path(signals_path)
    if not sp.exists():
        print(f"[build_rss] {signals_path} not found, skipping")
        return ""
    data = json.loads(sp.read_text(encoding="utf-8"))
    now = datetime.now(timezone.utc)
    pub_date = format_datetime(now)

    items_xml = []
    for s in data.get("top_buys", []):
        title = f"{s['verdict']}: {s['player']} ({s['grade']}) — composite {s['composite']:.1f}"
        desc = (
            f"<![CDATA[<p><strong>{s['player']}</strong> · {s['sport']} · {s['set_year']} · {s['grade']}</p>"
            f"<ul>"
            f"<li>Anchor: ${s['anchor']:,}"
            + (f" / Live: ${s['live']:,}" if s.get('live') is not None else "")
            + "</li>"
            f"<li>30d trend: {s['trend30d']:+.0f}%</li>"
            f"<li>PSA pop: {s['pop']:,}</li>"
            f"<li>Buy zone &lt; ${s['t_buy']:,} · Sell zone &gt; ${s['t_sell']:,}</li>"
            f"<li>eBay: <a href=\"https://www.ebay.com/sch/i.html?_nkw={s['ebay_query'].replace(' ', '+')}&amp;LH_Sold=1&amp;LH_Complete=1\">view sold comps</a></li>"
            f"</ul>]]>"
        )
        guid = f"sc-{s['id']}-{data['generated_at']}"
        items_xml.append(f"""    <item>
      <title>{sax.escape(title)}</title>
      <link>{SITE}#{s['id']}</link>
      <description>{desc}</description>
      <guid isPermaLink="false">{guid}</guid>
      <pubDate>{pub_date}</pubDate>
      <category>{s['sport']}</category>
    </item>""")

    feed = f"""<?xml version="1.0" encoding="UTF-8"?>
<rss version="2.0" xmlns:atom="http://www.w3.org/2005/Atom">
  <channel>
    <title>bpleone Sports Cards — BUY Signals</title>
    <link>{SITE}</link>
    <atom:link href="{FEED_URL}" rel="self" type="application/rss+xml"/>
    <description>Top BUY signals from the bpleone Sports Cards trading desk. Refreshed weekly.</description>
    <language>en-us</language>
    <lastBuildDate>{pub_date}</lastBuildDate>
    <generator>bpleone-sports-cards-desk build_rss.py</generator>
{chr(10).join(items_xml)}
  </channel>
</rss>
"""
    out = Path(out_path)
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(feed, encoding="utf-8")
    print(f"[build_rss] wrote {len(items_xml)} items to {out_path}")
    return feed


if __name__ == "__main__":
    build()
