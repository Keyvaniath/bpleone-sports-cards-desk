"""
bpleone.com Sports Cards Desk
Trading dashboard for PSA-graded sports cards. Mirrors the Pokemon TCG desk.

Run:    streamlit run streamlit_app.py
Deploy: Streamlit Community Cloud -> sports-cards.bpleone.com
"""
from __future__ import annotations

import json
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path

import pandas as pd
import streamlit as st

from cards_data import CARDS
from quant_score import score_all, score_card
from sealed_products import SEALED, SEALED_COLS, score_sealed
from parallels import PARALLELS, PARALLEL_COLS, score_parallel
import price_history

# Column index map for CARDS tuples
COL = {
    "id": 0, "sport": 1, "category": 2, "tier": 3, "player": 4,
    "set_year": 5, "card_num": 6, "grade": 7, "price": 8,
    "trend30d": 9, "t_buy": 10, "t_sell": 11, "horizon": 12,
    "conf": 13, "pop": 14, "ebay_query": 15, "psa_url": 16, "notes": 17,
}

GOLD = "#f5c842"
BG_CARD = "#131826"
BORDER = "#232a3e"
TEXT_DIM = "#8b94a8"
GREEN = "#4ade80"
ORANGE = "#fb923c"
RED = "#f87171"

VERDICT_COLOR = {
    "STRONG BUY": GREEN,
    "BUY": "#86efac",
    "HOLD": TEXT_DIM,
    "TRIM": ORANGE,
    "SELL": RED,
}

# ----------------------------------------------------------------------
st.set_page_config(
    page_title="Sports Cards — bpleone.com",
    page_icon="🏀",
    layout="wide",
    initial_sidebar_state="expanded",
)


st.markdown(
    f"""
    <style>
    .stApp {{ background: #0a0e1a; }}
    .block-container {{ padding-top: 1.5rem; padding-bottom: 3rem; }}
    h1, h2, h3, h4 {{ color: #e8ecf4; }}
    [data-testid="stSidebar"] {{ background: #0d1220; border-right: 1px solid {BORDER}; }}

    .stat-card {{
        background: {BG_CARD}; border: 1px solid {BORDER};
        border-radius: 12px; padding: 18px; height: 100%;
    }}
    .stat-card .label {{ color: {TEXT_DIM}; font-size: 11px; text-transform: uppercase; letter-spacing: 0.08em; }}
    .stat-card .value {{ color: #e8ecf4; font-size: 28px; font-weight: 700; margin-top: 6px; }}
    .stat-card .sub {{ color: {TEXT_DIM}; font-size: 12px; margin-top: 4px; }}

    .verdict-pill {{
        display: inline-block; padding: 4px 10px; border-radius: 4px;
        font-family: 'JetBrains Mono', monospace;
        font-size: 11px; font-weight: 700; letter-spacing: 0.06em;
    }}
    </style>
    """,
    unsafe_allow_html=True,
)


# ----------------------------------------------------------------------
@st.cache_data(ttl=300, show_spinner=False)
def load_live_prices() -> dict:
    p = Path("live_prices.json")
    if not p.exists():
        return {}
    try:
        return json.loads(p.read_text(encoding="utf-8")).get("prices", {})
    except Exception:
        return {}


@st.cache_data(ttl=300, show_spinner=False)
def load_live_meta() -> dict:
    p = Path("live_prices.json")
    if not p.exists():
        return {}
    try:
        return {k: v for k, v in json.loads(p.read_text(encoding="utf-8")).items() if k != "prices"}
    except Exception:
        return {}


live_prices = load_live_prices()
live_meta = load_live_meta()
scores_list = score_all(CARDS, live_prices)
scores_by_id = {s.card_id: s for s in scores_list}


def card_dict(card: tuple) -> dict:
    return {k: card[v] for k, v in COL.items()}


def card_to_row(card: tuple) -> dict:
    d = card_dict(card)
    s = scores_by_id.get(d["id"])
    live = live_prices.get(d["id"])
    return {
        "ID": d["id"],
        "Sport": d["sport"],
        "Player": d["player"],
        "Set / Year": d["set_year"],
        "Card #": d["card_num"],
        "Grade": d["grade"],
        "Tier": d["tier"],
        "Category": d["category"],
        "Anchor $": d["price"],
        "Live $": s.live_price if s else None,
        "30d %": round(d["trend30d"] * 100, 1),
        "Buy <": d["t_buy"],
        "Sell >": d["t_sell"],
        "Pop": d["pop"],
        "Conf": d["conf"],
        "Horizon": d["horizon"],
        "Score": s.composite if s else None,
        "Verdict": s.verdict if s else None,
    }


# ----------------------------------------------------------------------
# Sidebar
# ----------------------------------------------------------------------
with st.sidebar:
    st.markdown("### 🏆 Sports Cards Desk")
    st.caption("PSA-graded · NBA · NFL · MLB · more")
    st.markdown("---")

    view = st.radio(
        "View",
        ["🏠 Dashboard", "🔍 Watchlist", "🎯 BUY Signals", "📊 By Sport", "🌈 Parallels",
         "📦 Sealed", "⚖️ Compare", "🧮 Sizer", "💼 Inventory", "🃏 Card Detail", "ℹ️ Methodology"],
        index=0,
        label_visibility="collapsed",
    )

    st.markdown("---")
    st.caption(f"Cards: {len(CARDS)}")
    refreshed = live_meta.get("refreshed_at")
    if refreshed:
        try:
            dt = datetime.fromisoformat(refreshed.replace("Z", "+00:00"))
            st.caption(f"Prices: {dt.strftime('%Y-%m-%d %H:%M')} UTC")
        except Exception:
            pass
    else:
        st.caption("Prices: not yet refreshed")
    n_live = len(live_prices)
    st.caption(f"Live cards: {n_live}/{len(CARDS)}")
    if st.button("🔄 Reload prices", use_container_width=True):
        st.cache_data.clear()
        st.rerun()


# ----------------------------------------------------------------------
def verdict_pill(verdict: str) -> str:
    color = VERDICT_COLOR.get(verdict, TEXT_DIM)
    return f"<span class='verdict-pill' style='background:{color};color:#0a0e1a'>{verdict}</span>"


def render_dataframe(df: pd.DataFrame, *, show_live_only: bool = False) -> None:
    """Color-coded watchlist."""
    if df.empty:
        st.info("No cards match these filters.")
        return
    if show_live_only:
        df = df[df["Live $"].notna()]
    # Style: highlight Score column with verdict color
    def color_verdict(val):
        return f"background-color: {VERDICT_COLOR.get(val, '#232a3e')}; color: #0a0e1a; font-weight: 700"
    styled = df.style
    if "Verdict" in df.columns:
        styled = styled.map(color_verdict, subset=["Verdict"])
    # Format $ columns
    for col in ("Anchor $", "Live $", "Buy <", "Sell >"):
        if col in df.columns:
            styled = styled.format({col: lambda v: f"${v:,.0f}" if v is not None and not pd.isna(v) else "—"})
    styled = styled.format({"30d %": lambda v: f"{v:+.1f}%" if not pd.isna(v) else "—"})
    if "Score" in df.columns:
        styled = styled.format({"Score": lambda v: f"{v:.1f}" if not pd.isna(v) else "—"})
    st.dataframe(styled, use_container_width=True, hide_index=True, height=600)


# ----------------------------------------------------------------------
# Pages
# ----------------------------------------------------------------------
def page_dashboard():
    st.markdown("## Sports Cards Desk")
    st.caption("Apply the Pokemon TCG playbook to PSA-graded sports cards. Quant scoring, live eBay comps, BUY/SELL verdicts.")

    # Headline stats
    cols = st.columns(4)
    n_cards = len(CARDS)
    book_value = sum(c[COL["price"]] for c in CARDS)
    n_buy = sum(1 for s in scores_list if s.verdict.endswith("BUY"))
    n_trim = sum(1 for s in scores_list if s.verdict in ("TRIM", "SELL"))
    with cols[0]:
        st.markdown(f"<div class='stat-card'><div class='label'>Watchlist</div>"
                    f"<div class='value'>{n_cards}</div>"
                    f"<div class='sub'>cards tracked</div></div>", unsafe_allow_html=True)
    with cols[1]:
        st.markdown(f"<div class='stat-card'><div class='label'>Book Notional</div>"
                    f"<div class='value'>${book_value:,.0f}</div>"
                    f"<div class='sub'>anchor prices summed</div></div>", unsafe_allow_html=True)
    with cols[2]:
        st.markdown(f"<div class='stat-card'><div class='label'>Active BUYs</div>"
                    f"<div class='value' style='color:{GREEN}'>{n_buy}</div>"
                    f"<div class='sub'>STRONG BUY + BUY</div></div>", unsafe_allow_html=True)
    with cols[3]:
        st.markdown(f"<div class='stat-card'><div class='label'>TRIM/SELL</div>"
                    f"<div class='value' style='color:{ORANGE}'>{n_trim}</div>"
                    f"<div class='sub'>de-risk candidates</div></div>", unsafe_allow_html=True)

    st.markdown("---")

    # Verdict breakdown
    col_l, col_r = st.columns([2, 3])
    with col_l:
        st.markdown("##### Verdict Distribution")
        breakdown = Counter(s.verdict for s in scores_list)
        for v in ("STRONG BUY", "BUY", "HOLD", "TRIM", "SELL"):
            count = breakdown.get(v, 0)
            pct = 100 * count / max(1, n_cards)
            st.markdown(
                f"<div style='display:flex;justify-content:space-between;align-items:center;padding:6px 0;border-bottom:1px solid {BORDER}'>"
                f"{verdict_pill(v)}"
                f"<span style='color:{TEXT_DIM}'>{count} · {pct:.0f}%</span></div>",
                unsafe_allow_html=True,
            )

    with col_r:
        st.markdown("##### By Sport")
        sport_df = pd.DataFrame([
            {"Sport": sport,
             "Cards": cnt,
             "Book $": sum(c[COL["price"]] for c in CARDS if c[COL["sport"]] == sport),
             "Median $": sorted(c[COL["price"]] for c in CARDS if c[COL["sport"]] == sport)[cnt // 2] if cnt else 0,
             "BUYs": sum(1 for s in scores_list if any(c[COL["id"]] == s.card_id and c[COL["sport"]] == sport for c in CARDS) and s.verdict.endswith("BUY")),
            }
            for sport, cnt in Counter(c[COL["sport"]] for c in CARDS).most_common()
        ])
        styled = sport_df.style.format({"Book $": "${:,.0f}", "Median $": "${:,.0f}"})
        st.dataframe(styled, use_container_width=True, hide_index=True)

    st.markdown("---")
    st.markdown("##### Top 10 STRONG BUYs / BUYs")
    top10 = [s for s in scores_list if s.verdict.endswith("BUY")][:10]
    if not top10:
        st.caption("No active BUY signals — try refreshing live prices.")
    else:
        rows = []
        for s in top10:
            card = next(c for c in CARDS if c[COL["id"]] == s.card_id)
            d = card_dict(card)
            rows.append({
                "ID": s.card_id,
                "Player": d["player"],
                "Set": d["set_year"],
                "Grade": d["grade"],
                "Anchor $": d["price"],
                "Live $": s.live_price,
                "Score": s.composite,
                "Verdict": s.verdict,
            })
        df = pd.DataFrame(rows)
        render_dataframe(df)


def page_watchlist():
    st.markdown("## Full Watchlist")
    fcols = st.columns(4)
    with fcols[0]:
        sport_filter = st.multiselect(
            "Sport",
            options=sorted({c[COL["sport"]] for c in CARDS}),
            default=sorted({c[COL["sport"]] for c in CARDS}),
        )
    with fcols[1]:
        cat_filter = st.multiselect(
            "Category",
            options=sorted({c[COL["category"]] for c in CARDS}),
            default=sorted({c[COL["category"]] for c in CARDS}),
        )
    with fcols[2]:
        tier_filter = st.multiselect(
            "Tier",
            options=sorted({c[COL["tier"]] for c in CARDS}),
            default=sorted({c[COL["tier"]] for c in CARDS}),
        )
    with fcols[3]:
        verdict_filter = st.multiselect(
            "Verdict",
            options=["STRONG BUY", "BUY", "HOLD", "TRIM", "SELL"],
            default=["STRONG BUY", "BUY", "HOLD", "TRIM", "SELL"],
        )
    search = st.text_input("Search player / set", placeholder="e.g. Mantle, Caleb, Bowman")

    rows = []
    for card in CARDS:
        d = card_dict(card)
        s = scores_by_id.get(d["id"])
        if d["sport"] not in sport_filter:
            continue
        if d["category"] not in cat_filter:
            continue
        if d["tier"] not in tier_filter:
            continue
        if s and s.verdict not in verdict_filter:
            continue
        if search:
            blob = f"{d['player']} {d['set_year']} {d['card_num']} {d['notes']}".lower()
            if search.lower() not in blob:
                continue
        rows.append(card_to_row(card))
    df = pd.DataFrame(rows)
    if df.empty:
        st.info("No matches. Loosen filters.")
        return
    st.caption(f"{len(df)} cards · book ${df['Anchor $'].sum():,.0f}")
    render_dataframe(df)


def page_buy_signals():
    st.markdown("## BUY Signals")
    st.caption("Composite ≥ 70 from momentum + value + scarcity + liquidity.")

    buys = [s for s in scores_list if s.verdict in ("STRONG BUY", "BUY")]
    if not buys:
        st.info("No active BUY signals. Refresh prices or wait for the next pricing cycle.")
        return

    rows = []
    for s in buys:
        card = next(c for c in CARDS if c[COL["id"]] == s.card_id)
        d = card_dict(card)
        rows.append({
            "ID": s.card_id,
            "Sport": d["sport"],
            "Player": d["player"],
            "Set / Year": d["set_year"],
            "Grade": d["grade"],
            "Tier": d["tier"],
            "Anchor $": d["price"],
            "Live $": s.live_price,
            "Buy <": d["t_buy"],
            "Sell >": d["t_sell"],
            "30d %": round(d["trend30d"] * 100, 1),
            "Pop": d["pop"],
            "Score": s.composite,
            "Verdict": s.verdict,
        })
    df = pd.DataFrame(rows)
    render_dataframe(df)


def page_by_sport():
    st.markdown("## By Sport")
    for sport in sorted({c[COL["sport"]] for c in CARDS}):
        cards = [c for c in CARDS if c[COL["sport"]] == sport]
        cards_book = sum(c[COL["price"]] for c in cards)
        st.markdown(f"### {sport}")
        st.caption(f"{len(cards)} cards · book ${cards_book:,.0f}")
        rows = [card_to_row(c) for c in cards]
        df = pd.DataFrame(rows).sort_values("Score", ascending=False, na_position="last")
        render_dataframe(df)
        st.markdown("---")


def page_inventory():
    st.markdown("## Inventory & P&L")
    st.caption("Track your actual holdings — what you paid, what they're worth now, unrealized P&L.")

    inv_file = Path("inventory.json")
    inv = {}
    if inv_file.exists():
        try:
            inv = json.loads(inv_file.read_text(encoding="utf-8"))
        except Exception:
            pass

    st.markdown("#### Add / Update Position")
    with st.form("add_position"):
        cols = st.columns([2, 1, 1, 1])
        with cols[0]:
            card_pick = st.selectbox(
                "Card",
                options=[c[COL["id"]] for c in CARDS],
                format_func=lambda cid: f"{cid}  ·  {next(c[COL['player']] for c in CARDS if c[COL['id']]==cid)} — {next(c[COL['set_year']] for c in CARDS if c[COL['id']]==cid)}",
            )
        with cols[1]:
            qty = st.number_input("Qty", min_value=1, max_value=100, value=1, step=1)
        with cols[2]:
            cost = st.number_input("Cost basis (each)", min_value=0.0, value=0.0, step=10.0)
        with cols[3]:
            buy_date = st.date_input("Buy date", value=datetime.today())
        submit = st.form_submit_button("Add / Update")
        if submit and cost > 0:
            inv[card_pick] = {"qty": int(qty), "cost": float(cost), "buy_date": buy_date.isoformat()}
            inv_file.write_text(json.dumps(inv, indent=2), encoding="utf-8")
            st.success(f"Saved {card_pick}: {qty} @ ${cost:,.2f} on {buy_date}")
            st.rerun()

    if not inv:
        st.info("No positions yet — add one above.")
        return

    rows = []
    total_cost = 0
    total_value = 0
    for cid, pos in inv.items():
        card = next((c for c in CARDS if c[COL["id"]] == cid), None)
        if not card:
            continue
        d = card_dict(card)
        s = scores_by_id.get(cid)
        live = s.live_price if s and s.live_price else d["price"]
        qty = pos["qty"]
        cost = pos["cost"]
        pos_cost = qty * cost
        pos_value = qty * live
        pnl = pos_value - pos_cost
        pnl_pct = (pnl / pos_cost * 100) if pos_cost > 0 else 0
        total_cost += pos_cost
        total_value += pos_value
        rows.append({
            "ID": cid,
            "Player": d["player"],
            "Grade": d["grade"],
            "Qty": qty,
            "Cost $": cost,
            "Live $": live,
            "Pos Cost": pos_cost,
            "Pos Value": pos_value,
            "P&L $": pnl,
            "P&L %": pnl_pct,
            "Verdict": s.verdict if s else "—",
            "Buy Date": pos.get("buy_date", ""),
        })
    if rows:
        df = pd.DataFrame(rows)
        total_pnl = total_value - total_cost
        total_pct = (total_pnl / total_cost * 100) if total_cost else 0

        c1, c2, c3 = st.columns(3)
        with c1:
            st.markdown(f"<div class='stat-card'><div class='label'>Cost Basis</div>"
                        f"<div class='value'>${total_cost:,.0f}</div></div>", unsafe_allow_html=True)
        with c2:
            st.markdown(f"<div class='stat-card'><div class='label'>Current Value</div>"
                        f"<div class='value'>${total_value:,.0f}</div></div>", unsafe_allow_html=True)
        with c3:
            color = GREEN if total_pnl >= 0 else RED
            st.markdown(f"<div class='stat-card'><div class='label'>Unrealized P&L</div>"
                        f"<div class='value' style='color:{color}'>${total_pnl:,.0f}</div>"
                        f"<div class='sub' style='color:{color}'>{total_pct:+.1f}%</div></div>", unsafe_allow_html=True)

        styled = df.style.format({
            "Cost $": "${:,.2f}",
            "Live $": "${:,.2f}",
            "Pos Cost": "${:,.0f}",
            "Pos Value": "${:,.0f}",
            "P&L $": "${:+,.0f}",
            "P&L %": "{:+.1f}%",
        })
        st.dataframe(styled, use_container_width=True, hide_index=True)


def page_card_detail():
    st.markdown("## Card Detail")
    card_pick = st.selectbox(
        "Pick a card",
        options=[c[COL["id"]] for c in CARDS],
        format_func=lambda cid: f"{cid}  ·  {next(c[COL['player']] for c in CARDS if c[COL['id']]==cid)} — {next(c[COL['set_year']] for c in CARDS if c[COL['id']]==cid)} {next(c[COL['grade']] for c in CARDS if c[COL['id']]==cid)}",
    )
    card = next(c for c in CARDS if c[COL["id"]] == card_pick)
    d = card_dict(card)
    s = scores_by_id.get(card_pick)
    live = live_prices.get(card_pick) or {}

    st.markdown(f"### {d['player']} — {d['set_year']}")
    st.caption(f"#{d['card_num']} · {d['grade']} · Tier {d['tier']} · {d['sport']} / {d['category']}")

    cols = st.columns(4)
    with cols[0]:
        st.markdown(f"<div class='stat-card'><div class='label'>Anchor</div>"
                    f"<div class='value'>${d['price']:,.0f}</div>"
                    f"<div class='sub'>seed baseline</div></div>", unsafe_allow_html=True)
    with cols[1]:
        live_str = f"${s.live_price:,.0f}" if s and s.live_price else "—"
        st.markdown(f"<div class='stat-card'><div class='label'>Live Median</div>"
                    f"<div class='value'>{live_str}</div>"
                    f"<div class='sub'>{live.get('n_samples',0)} sales</div></div>", unsafe_allow_html=True)
    with cols[2]:
        st.markdown(f"<div class='stat-card'><div class='label'>Buy / Sell</div>"
                    f"<div class='value' style='font-size:18px'>${d['t_buy']:,.0f} / ${d['t_sell']:,.0f}</div>"
                    f"<div class='sub'>entry / exit zones</div></div>", unsafe_allow_html=True)
    with cols[3]:
        verdict = s.verdict if s else "—"
        score = f"{s.composite:.1f}" if s else "—"
        color = VERDICT_COLOR.get(verdict, TEXT_DIM)
        st.markdown(f"<div class='stat-card'><div class='label'>Verdict</div>"
                    f"<div class='value' style='color:{color}'>{verdict}</div>"
                    f"<div class='sub'>composite {score}</div></div>", unsafe_allow_html=True)

    if s:
        st.markdown("##### Sub-score breakdown")
        sub_cols = st.columns(4)
        labels = [("Momentum", s.momentum), ("Value", s.value), ("Scarcity", s.scarcity), ("Liquidity", s.liquidity)]
        for col, (lbl, v) in zip(sub_cols, labels):
            with col:
                bar_color = GREEN if v >= 70 else (TEXT_DIM if v >= 50 else (ORANGE if v >= 30 else RED))
                col.markdown(f"<div class='stat-card'><div class='label'>{lbl}</div>"
                             f"<div class='value' style='color:{bar_color}'>{v:.1f}</div></div>",
                             unsafe_allow_html=True)

    st.markdown("---")
    st.markdown("##### Notes")
    st.write(d["notes"])
    st.markdown(f"**Horizon:** {d['horizon']} · **Conviction:** {d['conf']}/5 · **PSA Pop:** {d['pop']}")
    st.markdown(f"**eBay query:** `{d['ebay_query']}`")
    if d.get("psa_url"):
        st.markdown(f"**PSA pop report:** [{d['psa_url']}]({d['psa_url']})")

    # Price history chart
    history = price_history.load_history(card_pick)
    if len(history) >= 2:
        st.markdown("##### Price History")
        hist_df = pd.DataFrame(history)
        hist_df["date"] = pd.to_datetime(hist_df["date"])
        hist_df = hist_df.set_index("date")
        st.line_chart(hist_df["median"], height=240)

    sales = live.get("last_sales") or []
    if sales:
        st.markdown("##### Recent eBay Sales")
        sdf = pd.DataFrame(sales)
        if "title" in sdf.columns:
            sdf["title"] = sdf["title"].str.slice(0, 90)
        st.dataframe(sdf, use_container_width=True, hide_index=True)
    else:
        st.info("No live sales loaded for this card yet. Run `python live_prices.py` to refresh.")


def page_sealed():
    st.markdown("## Sealed Product")
    st.caption("Boxes / cases — longer-duration sealed-product holds. Different scoring "
               "than singles: trend + risk-adjusted upside (top-quartile rip EV vs floor).")

    rows = []
    for prod in SEALED:
        scored = score_sealed(prod)
        d = {k: prod[i] for k, i in SEALED_COLS.items()}
        rows.append({
            "ID": d["id"],
            "Sport": d["sport"],
            "Product": d["product"],
            "Brand": d["brand"],
            "Set / Year": d["set_year"],
            "Config": d["config"],
            "MSRP $": d["msrp"],
            "Market $": d["market"],
            "Apprec %": scored["appreciation_pct"],
            "30d %": round(d["trend30d"] * 100, 1),
            "EV Floor": d["ev_floor"],
            "EV Top": d["ev_top"],
            "Up %": scored["upside_pct"],
            "Down %": scored["downside_pct"],
            "R:R": scored["risk_reward"],
            "Score": scored["composite"],
            "Verdict": scored["verdict"],
        })
    df = pd.DataFrame(rows)

    fcols = st.columns(3)
    with fcols[0]:
        sport_filter = st.multiselect(
            "Sport",
            options=sorted({p[SEALED_COLS["sport"]] for p in SEALED}),
            default=sorted({p[SEALED_COLS["sport"]] for p in SEALED}),
            key="sealed_sport",
        )
    with fcols[1]:
        product_filter = st.multiselect(
            "Product type",
            options=sorted({p[SEALED_COLS["product"]] for p in SEALED}),
            default=sorted({p[SEALED_COLS["product"]] for p in SEALED}),
            key="sealed_product",
        )
    with fcols[2]:
        verdict_filter = st.multiselect(
            "Verdict",
            options=["STRONG BUY", "BUY", "HOLD", "TRIM", "SELL"],
            default=["STRONG BUY", "BUY", "HOLD"],
            key="sealed_verdict",
        )

    df = df[df["Sport"].isin(sport_filter)
            & df["Product"].isin(product_filter)
            & df["Verdict"].isin(verdict_filter)]
    if df.empty:
        st.info("No sealed product matches these filters.")
        return

    df = df.sort_values("Score", ascending=False)
    styled = df.style.format({
        "MSRP $": "${:,.0f}",
        "Market $": "${:,.0f}",
        "EV Floor": "${:,.0f}",
        "EV Top": "${:,.0f}",
        "Apprec %": "{:+.1f}%",
        "30d %": "{:+.1f}%",
        "Up %": "{:+.1f}%",
        "Down %": "{:.1f}%",
        "R:R": "{:.2f}",
        "Score": "{:.1f}",
    })
    if "Verdict" in df.columns:
        styled = styled.map(
            lambda v: f"background-color: {VERDICT_COLOR.get(v, '#232a3e')}; color: #0a0e1a; font-weight: 700",
            subset=["Verdict"],
        )

    # Headline totals
    cols = st.columns(3)
    with cols[0]:
        st.markdown(f"<div class='stat-card'><div class='label'>Products tracked</div>"
                    f"<div class='value'>{len(df)}</div></div>", unsafe_allow_html=True)
    with cols[1]:
        st.markdown(f"<div class='stat-card'><div class='label'>Market notional</div>"
                    f"<div class='value'>${df['Market $'].sum():,.0f}</div></div>", unsafe_allow_html=True)
    with cols[2]:
        avg_apprec = df["Apprec %"].mean()
        color = GREEN if avg_apprec >= 0 else RED
        st.markdown(f"<div class='stat-card'><div class='label'>Avg appreciation vs MSRP</div>"
                    f"<div class='value' style='color:{color}'>{avg_apprec:+.1f}%</div></div>",
                    unsafe_allow_html=True)

    st.dataframe(styled, use_container_width=True, hide_index=True, height=500)


def page_parallels():
    st.markdown("## Color / Refractor Parallels")
    st.caption("Beyond base — the parallel ladder where most of the upside lives. "
               "Silver → Hyper → Color → Numbered → Gold /10 → 1/1. "
               "Each parallel is scored independently (momentum + value + scarcity from print run).")

    rows = []
    for p in PARALLELS:
        scored = score_parallel(p, live_prices.get(p[0], {}).get("median") if live_prices else None)
        base_card = next((c for c in CARDS if c[0] == p[1]), None)
        base_player = base_card[COL["player"]] if base_card else "?"
        rows.append({
            "ID": p[PARALLEL_COLS["id"]],
            "Base Card": f"{p[PARALLEL_COLS['base_id']]} · {base_player}",
            "Sport": p[PARALLEL_COLS["sport"]],
            "Parallel": p[PARALLEL_COLS["parallel_name"]],
            "Print Run": p[PARALLEL_COLS["print_run"]],
            "Grade": p[PARALLEL_COLS["grade"]],
            "Anchor $": p[PARALLEL_COLS["price"]],
            "30d %": round(p[PARALLEL_COLS["trend30d"]] * 100, 1),
            "Buy <": p[PARALLEL_COLS["t_buy"]],
            "Sell >": p[PARALLEL_COLS["t_sell"]],
            "Pop": p[PARALLEL_COLS["pop"]],
            "Score": scored["composite"],
            "Verdict": scored["verdict"],
        })
    df = pd.DataFrame(rows)

    fcols = st.columns(3)
    with fcols[0]:
        sport_pf = st.multiselect(
            "Sport",
            options=sorted(df["Sport"].unique()),
            default=sorted(df["Sport"].unique()),
            key="par_sport",
        )
    with fcols[1]:
        parallel_pf = st.multiselect(
            "Parallel type",
            options=sorted(df["Parallel"].unique()),
            default=sorted(df["Parallel"].unique()),
            key="par_parallel",
        )
    with fcols[2]:
        verdict_pf = st.multiselect(
            "Verdict",
            options=["STRONG BUY", "BUY", "HOLD", "TRIM", "SELL"],
            default=["STRONG BUY", "BUY", "HOLD"],
            key="par_verdict",
        )

    df = df[df["Sport"].isin(sport_pf) & df["Parallel"].isin(parallel_pf) & df["Verdict"].isin(verdict_pf)]
    df = df.sort_values("Score", ascending=False)
    if df.empty:
        st.info("No parallels match these filters.")
        return

    cols = st.columns(3)
    with cols[0]:
        st.markdown(f"<div class='stat-card'><div class='label'>Parallels tracked</div>"
                    f"<div class='value'>{len(df)}</div></div>", unsafe_allow_html=True)
    with cols[1]:
        st.markdown(f"<div class='stat-card'><div class='label'>Notional</div>"
                    f"<div class='value'>${df['Anchor $'].sum():,.0f}</div></div>", unsafe_allow_html=True)
    with cols[2]:
        n_buy = (df["Verdict"].isin(["STRONG BUY", "BUY"])).sum()
        st.markdown(f"<div class='stat-card'><div class='label'>BUYs</div>"
                    f"<div class='value' style='color:{GREEN}'>{n_buy}</div></div>", unsafe_allow_html=True)

    styled = df.style.format({
        "Anchor $": "${:,.0f}",
        "Buy <": "${:,.0f}",
        "Sell >": "${:,.0f}",
        "30d %": "{:+.1f}%",
        "Score": "{:.1f}",
    })
    styled = styled.map(
        lambda v: f"background-color: {VERDICT_COLOR.get(v, '#232a3e')}; color: #0a0e1a; font-weight: 700",
        subset=["Verdict"],
    )
    st.dataframe(styled, use_container_width=True, hide_index=True, height=550)


def page_compare():
    st.markdown("## Compare Cards Head-to-Head")
    st.caption("Pick two cards. See which has the better composite, where it lives in its buy/sell band, "
               "and how their sub-scores stack up.")

    options = {c[COL["id"]]: f"{c[COL['id']]}  ·  {c[COL['player']]} — {c[COL['set_year']]} {c[COL['grade']]}" for c in CARDS}
    cols = st.columns(2)
    with cols[0]:
        a_id = st.selectbox("Card A", options=list(options.keys()),
                            format_func=lambda k: options[k], key="cmp_a")
    with cols[1]:
        b_id = st.selectbox("Card B", options=list(options.keys()),
                            format_func=lambda k: options[k], index=1, key="cmp_b")

    if a_id == b_id:
        st.warning("Pick two different cards.")
        return

    a_card = next(c for c in CARDS if c[COL["id"]] == a_id)
    b_card = next(c for c in CARDS if c[COL["id"]] == b_id)
    a_score = scores_by_id.get(a_id)
    b_score = scores_by_id.get(b_id)

    def card_block(card, score, color: str):
        d = card_dict(card)
        return (
            f"<div class='stat-card' style='border-left:4px solid {color}'>"
            f"<div class='label'>{d['sport']} · {d['set_year']}</div>"
            f"<div class='value' style='font-size:20px'>{d['player']}</div>"
            f"<div class='sub'>#{d['card_num']} · {d['grade']} · T{d['tier']}</div>"
            f"<div style='display:flex;justify-content:space-between;margin-top:14px;'>"
            f"<span style='color:{TEXT_DIM}'>Anchor</span><strong>${d['price']:,.0f}</strong></div>"
            f"<div style='display:flex;justify-content:space-between;'>"
            f"<span style='color:{TEXT_DIM}'>Live</span><strong>{'${:,.0f}'.format(score.live_price) if score and score.live_price else '—'}</strong></div>"
            f"<div style='display:flex;justify-content:space-between;'>"
            f"<span style='color:{TEXT_DIM}'>Buy/Sell</span><strong>${d['t_buy']:,.0f} / ${d['t_sell']:,.0f}</strong></div>"
            f"<div style='display:flex;justify-content:space-between;'>"
            f"<span style='color:{TEXT_DIM}'>PSA Pop</span><strong>{d['pop']}</strong></div>"
            f"<div style='display:flex;justify-content:space-between;margin-top:10px;border-top:1px solid {BORDER};padding-top:10px'>"
            f"<span style='color:{TEXT_DIM}'>COMPOSITE</span>"
            f"<strong style='color:{VERDICT_COLOR.get(score.verdict if score else 'HOLD', TEXT_DIM)};font-size:18px'>"
            f"{score.composite:.1f} {score.verdict}</strong></div>"
            f"<div style='color:{TEXT_DIM};margin-top:10px;font-size:13px'>{d['notes']}</div>"
            f"</div>"
        )

    cols = st.columns(2)
    with cols[0]:
        st.markdown(card_block(a_card, a_score, "#60a5fa"), unsafe_allow_html=True)
    with cols[1]:
        st.markdown(card_block(b_card, b_score, "#f5c842"), unsafe_allow_html=True)

    # Sub-score bars
    if a_score and b_score:
        st.markdown("##### Sub-score breakdown")
        sub = pd.DataFrame({
            "Metric": ["Momentum", "Value", "Scarcity", "Liquidity", "Composite"],
            f"{a_card[COL['player']]} (A)": [a_score.momentum, a_score.value, a_score.scarcity, a_score.liquidity, a_score.composite],
            f"{b_card[COL['player']]} (B)": [b_score.momentum, b_score.value, b_score.scarcity, b_score.liquidity, b_score.composite],
        }).set_index("Metric")
        st.bar_chart(sub, height=320)

        winner = a_card[COL["player"]] if a_score.composite > b_score.composite else b_card[COL["player"]]
        diff = abs(a_score.composite - b_score.composite)
        st.success(f"📊 **{winner}** wins on composite by {diff:.1f} points.")


def page_sizer():
    st.markdown("## Position Sizer")
    st.caption("Risk-managed allocation: given your bankroll and per-trade risk tolerance, "
               "the max position size per card. Kelly-lite formula — 1/2 Kelly given a probabilistic edge.")

    cols = st.columns(3)
    with cols[0]:
        bankroll = st.number_input("Total bankroll ($)", min_value=100.0, value=10000.0, step=500.0)
    with cols[1]:
        risk_pct = st.slider("Max risk per position (%)", min_value=1.0, max_value=15.0, value=5.0, step=0.5)
    with cols[2]:
        edge_assumed = st.slider("Assumed edge (%)", min_value=5.0, max_value=40.0, value=15.0, step=1.0,
                                 help="Your conviction that the card is undervalued. Higher = larger position.")

    max_per_position = bankroll * risk_pct / 100
    half_kelly_pct = 0.5 * (edge_assumed / 100) / max(0.01, 1.0)  # simplification
    kelly_size = bankroll * half_kelly_pct

    cols = st.columns(3)
    with cols[0]:
        st.markdown(f"<div class='stat-card'><div class='label'>Bankroll</div>"
                    f"<div class='value'>${bankroll:,.0f}</div></div>", unsafe_allow_html=True)
    with cols[1]:
        st.markdown(f"<div class='stat-card'><div class='label'>Max per position</div>"
                    f"<div class='value' style='color:{GOLD}'>${max_per_position:,.0f}</div>"
                    f"<div class='sub'>{risk_pct:.1f}% of bankroll</div></div>", unsafe_allow_html=True)
    with cols[2]:
        st.markdown(f"<div class='stat-card'><div class='label'>1/2 Kelly target</div>"
                    f"<div class='value' style='color:{GREEN}'>${kelly_size:,.0f}</div>"
                    f"<div class='sub'>{half_kelly_pct*100:.1f}% of bankroll</div></div>", unsafe_allow_html=True)

    st.markdown("##### Suggested entries — current BUY signals")
    buys = [s for s in scores_list if s.verdict in ("STRONG BUY", "BUY")]
    if not buys:
        st.info("No active BUY signals.")
        return

    rows = []
    for s in buys:
        card = next(c for c in CARDS if c[COL["id"]] == s.card_id)
        d = card_dict(card)
        unit_price = s.live_price or d["price"]
        cap = min(max_per_position, kelly_size)
        max_qty = int(cap // unit_price) if unit_price > 0 else 0
        if max_qty < 1:
            max_qty = 1 if unit_price <= bankroll else 0
        suggested_dollars = max_qty * unit_price
        rows.append({
            "ID": s.card_id,
            "Player": d["player"],
            "Grade": d["grade"],
            "Verdict": s.verdict,
            "Score": s.composite,
            "Unit $": unit_price,
            "Max Qty": max_qty,
            "Suggested $": suggested_dollars,
            "% of bankroll": (suggested_dollars / bankroll * 100) if bankroll else 0,
        })
    df = pd.DataFrame(rows).sort_values("Score", ascending=False)
    styled = df.style.format({
        "Unit $": "${:,.0f}",
        "Suggested $": "${:,.0f}",
        "Score": "{:.1f}",
        "% of bankroll": "{:.1f}%",
    })
    styled = styled.map(
        lambda v: f"background-color: {VERDICT_COLOR.get(v, '#232a3e')}; color: #0a0e1a; font-weight: 700",
        subset=["Verdict"],
    )
    st.dataframe(styled, use_container_width=True, hide_index=True)

    total_deployed = df["Suggested $"].sum()
    cash_remaining = bankroll - total_deployed
    cols = st.columns(2)
    with cols[0]:
        st.markdown(f"<div class='stat-card'><div class='label'>Total deployable</div>"
                    f"<div class='value'>${total_deployed:,.0f}</div>"
                    f"<div class='sub'>{total_deployed/bankroll*100:.0f}% of bankroll</div></div>",
                    unsafe_allow_html=True)
    with cols[1]:
        st.markdown(f"<div class='stat-card'><div class='label'>Cash remaining</div>"
                    f"<div class='value' style='color:{TEXT_DIM}'>${cash_remaining:,.0f}</div></div>",
                    unsafe_allow_html=True)


def page_methodology():
    st.markdown("## Methodology")
    st.markdown("""
The Sports Cards desk uses the same quant framework as the Pokemon TCG desk:

#### Composite score (0-100)
```
COMPOSITE = 0.30 * MOMENTUM
          + 0.30 * VALUE
          + 0.20 * SCARCITY
          + 0.20 * LIQUIDITY
```

#### Sub-scores

**Momentum** — 30-day trend in the watchlist (curated) + delta between live median and anchor price.
Strong upward trend (+15% in 30d) gives ~85+ momentum.

**Value** — Where the live median sits between the *buy zone* and *sell zone*.
At the buy zone: 100. At the anchor (fair): 50. At the sell zone: 0.

**Scarcity** — PSA pop count at this exact grade. Lower pop = scarcer = higher score.
- <100 pop → 95 (institutional grail tier)
- <500 pop → 80 (tight float)
- 1500-3000 → 40 (mass-grade)
- 6000+ → 15 (commodity)

**Liquidity** — Recent eBay sold-comp count. More samples = easier to exit.
- ≥8 sales/month → 95
- 2-3 sales → 40
- ≤1 sale → 20

#### Verdict ladder
- ≥85 → **STRONG BUY**
- 70-84 → **BUY**
- 50-69 → **HOLD**
- 30-49 → **TRIM**
- <30 → **SELL**

#### Conviction adjustment
Cards with `conf >= 5` get +5 to composite; `conf <= 2` get -5. Reflects how much I trust the underlying thesis.

#### Data sources
- **eBay sold listings** — primary truth for graded prices, refreshed weekly
- **PSA pop reports** — seeded manually (Cloudflare blocks scraping). Update quarterly.

No paid APIs in v1.
""")


# Router
if view.startswith("🏠"):
    page_dashboard()
elif view.startswith("🔍"):
    page_watchlist()
elif view.startswith("🎯"):
    page_buy_signals()
elif view.startswith("📊"):
    page_by_sport()
elif view.startswith("🌈"):
    page_parallels()
elif view.startswith("📦"):
    page_sealed()
elif view.startswith("⚖️"):
    page_compare()
elif view.startswith("🧮"):
    page_sizer()
elif view.startswith("💼"):
    page_inventory()
elif view.startswith("🃏"):
    page_card_detail()
elif view.startswith("ℹ️"):
    page_methodology()


# Footer
st.markdown("---")
st.caption(
    f"Data: eBay sold comps · {len(CARDS)} cards tracked · "
    f"sports-cards.bpleone.com · {datetime.now(timezone.utc).strftime('%Y-%m-%d %H:%M UTC')}"
)
