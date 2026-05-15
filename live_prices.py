"""
eBay sold-comp scraper for the Sports Cards desk.

Adapted from the Pokemon project's scraper. Two paths:

  1. eBay Browse API (free OAuth) — preferred. Set $env:EBAY_OAUTH_TOKEN.
  2. eBay sold-listings HTML scrape — fallback. Warms a session against the
     homepage to grab Akamai bot-detection cookies, then queries /sch/i.html
     with realistic headers. Includes retry + outlier rejection.

Output for each card: {price, n_samples, low, high, median, last_sales, source}.

Writes the consolidated map to `live_prices.json` for the dashboard to read.
Also kept compatible with GitHub Actions / cron usage.
"""
from __future__ import annotations

import json
import os
import random
import re
import statistics
import sys
import time
from datetime import datetime
from pathlib import Path
from urllib.parse import quote_plus

import requests

from cards_data import CARDS

USER_AGENTS = [
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36 Edg/122.0.0.0",
]


def _ua_headers() -> dict:
    return {
        "User-Agent": random.choice(USER_AGENTS),
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
        "Accept-Language": "en-US,en;q=0.9",
        "Accept-Encoding": "gzip, deflate, br",
        "Cache-Control": "no-cache",
        "Pragma": "no-cache",
        "Sec-Ch-Ua": '"Not_A Brand";v="8", "Chromium";v="120"',
        "Sec-Fetch-Dest": "document",
        "Sec-Fetch-Mode": "navigate",
        "Sec-Fetch-Site": "none",
        "Sec-Fetch-User": "?1",
        "Upgrade-Insecure-Requests": "1",
        "Referer": "https://www.google.com/",
    }


_SESSION: requests.Session | None = None


def _session() -> requests.Session:
    """Warmed session — first hit on ebay.com homepage picks up Akamai cookies."""
    global _SESSION
    if _SESSION is not None:
        return _SESSION
    s = requests.Session()
    s.headers.update(_ua_headers())
    try:
        s.get("https://www.ebay.com/", timeout=15)
    except Exception:
        pass
    _SESSION = s
    return s


# -----------------------------------------------------------------
# eBay Browse API (free OAuth path)
# -----------------------------------------------------------------
EBAY_OAUTH_TOKEN = os.environ.get("EBAY_OAUTH_TOKEN", "").strip()


def ebay_api_query(query: str, max_results: int = 8) -> dict | None:
    """Calls eBay Browse API. Returns same shape as ebay_scrape() or None if not configured."""
    if not EBAY_OAUTH_TOKEN:
        return None
    try:
        url = "https://api.ebay.com/buy/browse/v1/item_summary/search"
        r = requests.get(
            url,
            headers={
                "Authorization": f"Bearer {EBAY_OAUTH_TOKEN}",
                "X-EBAY-C-MARKETPLACE-ID": "EBAY_US",
                "Accept": "application/json",
            },
            params={"q": query, "limit": max(15, max_results * 3)},
            timeout=20,
        )
        if r.status_code != 200:
            return None
        items = (r.json() or {}).get("itemSummaries", []) or []
        sales = []
        for it in items:
            title = (it.get("title") or "")[:160]
            try:
                price = float((it.get("price") or {}).get("value", 0))
            except (TypeError, ValueError):
                continue
            if price < 5.0:
                continue
            sales.append({"price": price, "date": "", "title": title})
            if len(sales) >= max_results:
                break
        return _summarize(sales, query, source="ebay_api")
    except Exception:
        return None


# -----------------------------------------------------------------
# eBay scrape fallback
# -----------------------------------------------------------------
_STATS = {"requests": 0, "ok": 0, "blocked": 0, "empty": 0, "matched": 0, "streak_blocked": 0}


def _is_blocked(status: int, html: str) -> bool:
    if status in (403, 429, 503):
        return True
    if not html or len(html) < 2000:
        return True
    bad = ("Pardon Our Interruption", "Service Unavailable", "Just a moment")
    if any(b in html for b in bad):
        return True
    if "Access Denied" in html and "akamai" in html.lower():
        return True
    return False


def ebay_scrape(query: str, max_results: int = 8, min_price: float = 5.0,
                retries: int = 2) -> dict | None:
    _STATS["requests"] += 1
    if os.environ.get("SKIP_EBAY", "").strip() in ("1", "true", "yes"):
        return None

    # Stop hammering after 5 consecutive blocks
    if _STATS["streak_blocked"] >= 5:
        return None

    url = ("https://www.ebay.com/sch/i.html"
           f"?_nkw={quote_plus(query)}&LH_Sold=1&LH_Complete=1&_sop=13&_ipg=60")

    html = ""
    status = 0
    sess = _session()
    for attempt in range(retries + 1):
        try:
            r = sess.get(url, headers=_ua_headers(), timeout=20)
            status = r.status_code
            html = r.text or ""
            if not _is_blocked(status, html):
                break
            time.sleep(2 + random.uniform(0, 2) + attempt * 3)
        except Exception:
            time.sleep(1 + attempt)

    if _is_blocked(status, html):
        _STATS["blocked"] += 1
        _STATS["streak_blocked"] += 1
        return None

    _STATS["streak_blocked"] = 0
    _STATS["ok"] += 1
    sales = _parse_sales(html, min_price, max_results)
    if not sales:
        _STATS["empty"] += 1
        return None
    if len(sales) < 2:
        return None
    _STATS["matched"] += 1
    return _summarize(sales, query, source="ebay")


def _parse_sales(html: str, min_price: float, max_results: int) -> list[dict]:
    blocks: list[int] = []
    for m in re.finditer(r'<li[^>]*class=["\']?[^"\'>]*\bs-item\b', html):
        blocks.append(m.start())
    for m in re.finditer(r'<(?:li|div)[^>]*class=["\']?[^"\'>]*\b(?:su-card-container|s-card)\b', html):
        blocks.append(m.start())
    if not blocks:
        return []
    blocks = sorted(set(blocks))
    ends = blocks[1:] + [len(html)]
    sales: list[dict] = []
    seen = set()
    for start, end in zip(blocks, ends):
        blk = html[start:end]
        title = _extract_title(blk)
        if not title or title.lower() in seen:
            continue
        seen.add(title.lower())
        price = _extract_price(blk)
        if price is None or price < min_price:
            continue
        date = _extract_date(blk)
        sales.append({"price": price, "date": date, "title": title})
        if len(sales) >= max_results:
            break
    return sales


def _extract_title(blk: str) -> str:
    container = re.search(
        r'class=["\']?[^"\'>]*\bs-(?:item|card)__title\b[^"\'>]*["\']?[^>]*>([\s\S]{0,800}?)</div>',
        blk,
    )
    if not container:
        return ""
    inner = container.group(1)
    for sm in re.finditer(r'<span[^>]*>([^<]+)</span>', inner):
        t = sm.group(1).strip()
        if not t:
            continue
        if t.lower() in ("new listing", "opens in a new window or tab", "shop on ebay"):
            continue
        return t
    return ""


def _extract_price(blk: str) -> float | None:
    # Pattern: <span class="s-item__price">$1,234.56</span>
    m = re.search(r'class=["\']?[^"\'>]*\bs-(?:item|card)__price\b[^"\'>]*["\']?[^>]*>([^<]+)<', blk)
    if not m:
        m = re.search(r'class=["\']?[^"\'>]*\bs-card__price\b[^"\'>]*["\']?[^>]*>([^<]+)<', blk)
    if not m:
        return None
    raw = m.group(1).strip()
    nums = re.findall(r'\$([0-9,]+(?:\.[0-9]{1,2})?)', raw)
    if not nums:
        return None
    try:
        return float(nums[0].replace(",", ""))
    except ValueError:
        return None


def _extract_date(blk: str) -> str:
    m = re.search(r'(?:Sold|Ended)\s+([A-Z][a-z]+\s+\d{1,2},?\s+\d{4})', blk)
    if m:
        try:
            return datetime.strptime(m.group(1).replace(",", ""), "%b %d %Y").strftime("%Y-%m-%d")
        except ValueError:
            return ""
    return ""


# -----------------------------------------------------------------
# Aggregation
# -----------------------------------------------------------------
def _summarize(sales: list[dict], query: str, source: str) -> dict | None:
    if not sales:
        return None
    raw_prices = [s["price"] for s in sales]
    if len(raw_prices) >= 4:
        med = statistics.median(raw_prices)
        kept = [s for s in sales if 0.5 * med <= s["price"] <= 2.0 * med]
        if len(kept) >= 2:
            sales = kept
    prices = [s["price"] for s in sales]
    median = round(statistics.median(prices), 2)
    return {
        "last_sales": sales[:8],
        "last_sale_price": sales[0]["price"],
        "last_sale_date": sales[0]["date"],
        "median": median,
        "mean": round(sum(prices) / len(prices), 2),
        "low": min(prices),
        "high": max(prices),
        "n_samples": len(sales),
        "source": source,
        "query": query,
    }


def fetch_card(query: str) -> dict | None:
    """Try API first, then scrape. Returns None on full failure."""
    if EBAY_OAUTH_TOKEN:
        result = ebay_api_query(query)
        if result:
            return result
    return ebay_scrape(query)


# -----------------------------------------------------------------
# Main refresh loop
# -----------------------------------------------------------------
def refresh_all(output_path: str = "live_prices.json", limit: int | None = None) -> dict:
    out: dict[str, dict] = {}
    count = 0
    fail = 0
    for card in CARDS:
        if limit and count >= limit:
            break
        cid = card[0]
        query = card[15]
        try:
            data = fetch_card(query)
        except Exception as e:
            print(f"  {cid:5s} ERR {e}", file=sys.stderr)
            data = None
        if data:
            data["card_id"] = cid
            data["fetched_at"] = datetime.utcnow().isoformat() + "Z"
            out[cid] = data
            print(f"  {cid:5s} OK   median=${data['median']:>8,.0f}  n={data['n_samples']}")
        else:
            fail += 1
            print(f"  {cid:5s} FAIL  query={query[:60]}")
        count += 1
        # be polite
        time.sleep(random.uniform(0.8, 1.6))

    Path(output_path).write_text(json.dumps({
        "refreshed_at": datetime.utcnow().isoformat() + "Z",
        "card_count": len(out),
        "fail_count": fail,
        "stats": _STATS,
        "prices": out,
    }, indent=2), encoding="utf-8")
    print(f"\nRefreshed {len(out)}/{count} cards. Failed: {fail}. Stats: {_STATS}")

    # Append today's snapshot to price history for trendlines
    try:
        import price_history
        n_hist = price_history.append_snapshot(output_path)
        print(f"Appended {n_hist} rows to price_history.jsonl")
    except Exception as e:
        print(f"[price_history] append failed: {e}", file=sys.stderr)

    return out


if __name__ == "__main__":
    limit = None
    if len(sys.argv) > 1:
        try:
            limit = int(sys.argv[1])
        except ValueError:
            pass
    refresh_all(limit=limit)
