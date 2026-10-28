from pathlib import Path
import re

ROOT = Path("/app")

def insert_once(path, anchor, payload, marker, label):
    s = path.read_text()
    if marker in s:
        return
    if anchor not in s:
        raise RuntimeError(f"Cannot install {label}: anchor not found")
    path.write_text(s.replace(anchor, payload + anchor, 1))

# Add missing workflows without changing the archived CoinDCX application/repository.
html = ROOT / "templates" / "index.html"
nav = '''    <button class="nav-link" data-view="portfolio-lab"><span class="nav-ico">↗</span> Portfolio Lab</button>
    <button class="nav-link" data-view="profit-tax"><span class="nav-ico">₹</span> Profit & Tax Centre</button>
    <button class="nav-link" data-view="strategy-watch"><span class="nav-ico">◉</span> Strategy Tax Watch</button>
'''
insert_once(html, '    <button class="nav-link" data-view="reports">', nav, 'data-view="profit-tax"', "navigation")

pages = r"""
    <section class="view" id="view-portfolio-lab">
      <div class="section-heading"><div><div class="eyebrow">EVIDENCE-BASED ALLOCATION</div><h2>Portfolio Lab</h2><p>Build a paper-only multi-trader allocation from stored portfolio data and stress-test the historical return profile.</p></div><span class="tag blue">PAPER ONLY · NO ORDERS</span></div>
      <div class="kpi-grid">
        <article class="kpi-card"><div class="kpi-head"><span>Candidate portfolios</span></div><div class="kpi-value" id="pl-count">—</div><div class="kpi-foot">Current risk-screen output</div></article>
        <article class="kpi-card"><div class="kpi-head"><span>Allocation used</span></div><div class="kpi-value" id="pl-used">—</div><div class="kpi-foot">Remaining capital stays unallocated</div></article>
        <article class="kpi-card"><div class="kpi-head"><span>30D historical scaling</span></div><div class="kpi-value" id="pl-30d">—</div><div class="kpi-foot">Illustrative, not a forecast</div></article>
        <article class="kpi-card"><div class="kpi-head"><span>30D after-tax reserve scenario</span></div><div class="kpi-value" id="pl-after-tax">—</div><div class="kpi-foot">30% reserve on positive strategy gains</div></article>
      </div>
      <article class="panel"><div class="panel-header"><div><div class="eyebrow">SCENARIO CONTROLS</div><h3>Capital and risk screen</h3></div><span class="tag purple">CONFIGURABLE</span></div>
        <div class="field-row"><label>Market<select id="pl-market"><option value="FUTURES">Futures</option><option value="SPOT">Spot</option></select></label><label>Paper capital (USDT)<input id="pl-capital" type="number" min="10" step="10" value="150"></label></div>
        <div class="field-row"><label>Maximum selected portfolios<select id="pl-max"><option>1</option><option>2</option><option selected>3</option><option>5</option><option>8</option></select></label><label>Minimum stored closed trades<input id="pl-min-trades" type="number" min="1" max="500" value="10"></label></div>
        <div class="button-row"><button class="btn primary" id="pl-run">Run portfolio analysis</button><button class="btn secondary" id="pl-refresh">Refresh stored data</button></div>
        <p class="help-text">This scales lead-trader profile ROI for a scenario only. Copy ratios, fees, funding, slippage, margin mode, leverage, and follower fill differences can make actual copier returns materially different. Past results cannot guarantee profits.</p>
      </article>
      <article class="panel"><div class="panel-header"><div><div class="eyebrow">PAPER ALLOCATION</div><h3>Candidate-by-candidate outcome</h3></div><span class="tag gray" id="pl-asof">Not evaluated</span></div><div class="table-scroll"><table><thead><tr><th>Portfolio</th><th>Duration (days)</th><th>Copier PnL</th><th>Score</th><th>Weight</th><th>Capital</th><th>ROI 7D</th><th>ROI 30D</th><th>ROI 90D</th><th>30D scaled PnL</th><th>30D tax reserve</th><th>Evidence / decision</th></tr></thead><tbody id="pl-rows"><tr><td colspan="12" class="empty-state">Run analysis to load stored portfolio metrics.</td></tr></tbody></table></div></article>
      <div id="pl-alert" class="notice-box">This page is a paper research tool. It does not copy, place, or close trades.</div>
    </section>

    <section class="view" id="view-profit-tax">
      <div class="section-heading"><div><div class="eyebrow">PERSONAL ACCOUNT LEDGER</div><h2>Profit & Tax Centre</h2><p>Track imported Binance income records, visible losses, a conservative 30% tax reserve on positive realised-PnL records, and estimated INR cash-out value.</p></div><span class="tag blue">ACCOUNT DATA ONLY</span></div>
      <div class="notice-box">Only your imported/account-synced records appear here. Public lead-trader history and paper estimates are not your personal trades. This centre is a planning estimate, not a tax return. For futures/derivatives classification and filing, confirm with an Indian tax professional.</div>
      <div class="kpi-grid">
        <article class="kpi-card"><div class="kpi-head"><span>Gross positive realised PnL</span></div><div class="kpi-value" id="pt-positive">—</div><div class="kpi-foot" id="pt-positive-inr">INR: —</div></article>
        <article class="kpi-card"><div class="kpi-head"><span>Conservative tax reserve · 30%</span></div><div class="kpi-value" id="pt-tax">—</div><div class="kpi-foot" id="pt-tax-inr">INR: —</div></article>
        <article class="kpi-card"><div class="kpi-head"><span>Economic PnL before reserve</span></div><div class="kpi-value" id="pt-net">—</div><div class="kpi-foot" id="pt-net-inr">INR: —</div></article>
        <article class="kpi-card"><div class="kpi-head"><span>Estimated PnL after reserve</span></div><div class="kpi-value" id="pt-after">—</div><div class="kpi-foot" id="pt-after-inr">INR: —</div></article>
      </div>
      <div class="content-grid two-col">
        <article class="panel"><div class="panel-header"><div><div class="eyebrow">REQUEST ACCOUNT DATA</div><h3>Sync Binance Futures income</h3></div><span class="tag purple">READ ONLY</span></div>
          <label>Read-only API key<input id="pt-api-key" type="text" autocomplete="off" placeholder="Paste API key"></label>
          <label>API secret (used once, never saved)<input id="pt-api-secret" type="password" autocomplete="new-password" placeholder="Paste API secret"></label>
          <div class="field-row"><label>History range<select id="pt-days"><option value="7">7 days</option><option value="30" selected>30 days</option><option value="60">60 days</option><option value="90">90 days</option></select></label><label>Strategy label<input id="pt-strategy-sync" type="text" value="Unattributed Binance Futures" maxlength="100"></label></div>
          <button class="btn primary" id="pt-sync">Request Binance income history</button>
          <p class="help-text">Create an API key with read-only/Enable Reading and Futures access only. Do not enable trading, withdrawals, transfers, or universal transfer. The key and secret are sent only for this request; the app stores returned records, not the credentials. Futures income history may not identify which copy-trading leader caused each record.</p>
        </article>
        <article class="panel"><div class="panel-header"><div><div class="eyebrow">IMPORT ACCOUNT EXPORT</div><h3>Upload realised-PnL CSV</h3></div><span class="tag gray">SPOT / FUTURES</span></div>
          <label>Strategy or copy portfolio label<input id="pt-strategy-csv" type="text" value="Imported Binance records" maxlength="100"></label>
          <div class="field-row"><label>Market<select id="pt-market-csv"><option value="FUTURES">Futures</option><option value="SPOT">Spot</option></select></label><label>Binance CSV file<input id="pt-csv" type="file" accept=".csv,text/csv"></label></div>
          <button class="btn secondary" id="pt-import">Import CSV records</button>
          <p class="help-text">Use a Binance realised PnL / income-history export with an income type and income amount, or a trade ledger that includes a realised/closed PnL column. Raw spot fills without acquisition cost and disposal proceeds are not enough for a reliable taxable-gain calculation. Duplicate rows are deduplicated.</p>
        </article>
      </div>
      <article class="panel"><div class="panel-header"><div><div class="eyebrow">CONVERSION</div><h3>Current Binance P2P reference rate</h3></div><span class="tag gray" id="pt-rate-status">Rate not loaded</span></div>
        <div class="field-row"><label>Reference buy quote (INR per USDT)<input id="pt-buy-rate" type="number" step="0.01" min="0" readonly placeholder="Loading…"></label><label>Reference sell quote (INR per USDT)<input id="pt-sell-rate" type="number" step="0.01" min="0" readonly placeholder="Loading…"></label><label>Cash-out conversion rate (INR per USDT)<input id="pt-rate" type="number" step="0.01" min="0" value="" placeholder="Enter current P2P sell rate"></label></div>
        <div class="button-row"><button class="btn secondary" id="pt-refresh-rate">Refresh P2P rates</button><span class="help-text">Past trades are converted using the selected current rate, not a historical P2P price. P2P ads, payment method, order limits, and merchant spread affect the actual executed price.</span></div>
      </article>
      <article class="panel"><div class="panel-header"><div><div class="eyebrow">TAX & LOSS RESERVE</div><h3>Ledger totals and data gaps</h3></div><span class="tag gray" id="pt-ledger-status">No account records loaded</span></div><div id="pt-warning" class="notice-box">Import or sync your personal records to calculate the account ledger.</div><div class="table-scroll"><table><thead><tr><th>Strategy / label</th><th>Records</th><th>Positive realised PnL</th><th>Gross losses (not offset)</th><th>Fees</th><th>Funding</th><th>30% tax reserve</th><th>Economic PnL</th><th>After-reserve PnL</th><th>Status</th></tr></thead><tbody id="pt-strategy-rows"><tr><td colspan="10" class="empty-state">No imported personal trade records.</td></tr></tbody></table></div></article>
      <article class="panel table-panel"><div class="panel-header"><div><div class="eyebrow">RECENT ACCOUNT RECORDS</div><h3>Trade / income entries with estimated tax reserve</h3></div><span class="tag gray" id="pt-row-count">0 records</span></div><div class="table-scroll"><table><thead><tr><th>Time (UTC)</th><th>Strategy label</th><th>Market</th><th>Symbol</th><th>Record type</th><th>Income asset / amount</th><th>Realised PnL (USDT)</th><th>Fees (USDT)</th><th>Funding (USDT)</th><th>Tax reserve</th><th>Entry net after reserve</th></tr></thead><tbody id="pt-ledger-rows"><tr><td colspan="11" class="empty-state">No imported personal trade records.</td></tr></tbody></table></div></article>
      <div class="notice-box">Tax method: the default conservative reserve applies 30% to each positive realised-PnL ledger record and does not use losing records to reduce that reserve. India’s Income-tax Act, 2025 section 194 specifies a 30% rate for income from transfer of a virtual digital asset and restricts loss set-off/carry-forward for that income. This simple reserve is not a legal conclusion that every futures PnL record is a VDA transfer; surcharge/cess, transaction classification, acquisition cost, TDS, and other facts require separate review. The conversion is a current P2P reference, not actual historic INR proceeds.</div>
    </section>

    <section class="view" id="view-strategy-watch">
      <div class="section-heading"><div><div class="eyebrow">AFTER-TAX STRATEGY DIAGNOSTICS</div><h2>Strategy Tax Watch</h2><p>Identify strategies where realised gains do not cover losses, fees, funding, and the conservative tax reserve.</p></div><span class="tag blue">NO PROFIT GUARANTEE</span></div>
      <div class="kpi-grid">
        <article class="kpi-card"><div class="kpi-head"><span>Strategies with records</span></div><div class="kpi-value" id="stw-count">—</div><div class="kpi-foot">From personal imports only</div></article>
        <article class="kpi-card"><div class="kpi-head"><span>Positive after reserve</span></div><div class="kpi-value" id="stw-positive">—</div><div class="kpi-foot">After recorded costs and reserve</div></article>
        <article class="kpi-card"><div class="kpi-head"><span>Non-positive / high-loss</span></div><div class="kpi-value" id="stw-risk">—</div><div class="kpi-foot">Review before new allocation</div></article>
        <article class="kpi-card"><div class="kpi-head"><span>Overall after-reserve PnL</span></div><div class="kpi-value" id="stw-net">—</div><div class="kpi-foot" id="stw-net-inr">INR: —</div></article>
      </div>
      <div id="stw-alert" class="notice-box">No personal strategy ledger imported yet. The app will not invent trades or project a guaranteed profit.</div>
      <article class="panel"><div class="panel-header"><div><div class="eyebrow">STRATEGY STATUS</div><h3>Warning list</h3></div><span class="tag gray">Recomputed from ledger</span></div><div class="table-scroll"><table><thead><tr><th>Strategy</th><th>Records</th><th>Positive realised gains</th><th>Gross losses</th><th>Loss / gain ratio</th><th>Fees + funding</th><th>Tax reserve</th><th>Economic PnL</th><th>After-reserve PnL</th><th>Warning / next check</th></tr></thead><tbody id="stw-rows"><tr><td colspan="10" class="empty-state">Import personal trade records to begin.</td></tr></tbody></table></div></article>
      <div class="notice-box">A strategy can become unprofitable after fees, funding, slippage, and a tax reserve even when its headline ROI is positive. A warning is a reason to investigate or pause new allocation, not an automatic order action. No system can guarantee that you will always remain profitable.</div>
    </section>
"""
insert_once(html, '    <section class="view" id="view-reports">', pages, 'id="view-profit-tax"', "page sections")

# Add resilient API endpoints. The public research tables are deliberately not used as personal tax records.
app = ROOT / "app.py"
backend = r'''
# ---- Profit & Tax Centre, account-ledger, trade-behaviour and portfolio policy ----
import csv as _it_csv
import hashlib as _it_hashlib
import hmac as _it_hmac
import io as _it_io
import json as _it_json
import math as _it_math
import time as _it_time
import datetime as _it_dt
import urllib.error as _it_urlerror
import urllib.parse as _it_urlparse
import urllib.request as _it_urlrequest
import sqlalchemy as _it_sa

_IT_TAX_RATE = 0.30

def _it_ensure_ledger():
    with SessionLocal() as db:
        dialect = db.get_bind().dialect.name
        id_type = "BIGSERIAL PRIMARY KEY" if dialect == "postgresql" else "INTEGER PRIMARY KEY AUTOINCREMENT"
        ddl = """
        CREATE TABLE IF NOT EXISTS account_trade_ledger (
          id %s,
          external_id TEXT NOT NULL UNIQUE,
          strategy_name TEXT NOT NULL DEFAULT 'Unattributed Binance Futures',
          market_type TEXT NOT NULL DEFAULT 'FUTURES',
          symbol TEXT,
          trade_id TEXT,
          income_type TEXT NOT NULL DEFAULT 'REALIZED_PNL',
          transaction_time TEXT,
          asset TEXT NOT NULL DEFAULT 'USDT',
          amount_asset DOUBLE PRECISION,
          amount_usdt DOUBLE PRECISION,
          realized_pnl_usdt DOUBLE PRECISION NOT NULL DEFAULT 0,
          commission_usdt DOUBLE PRECISION NOT NULL DEFAULT 0,
          funding_usdt DOUBLE PRECISION NOT NULL DEFAULT 0,
          source TEXT NOT NULL DEFAULT 'CSV_IMPORT',
          raw_json TEXT NOT NULL DEFAULT '{}',
          created_at TIMESTAMP WITHOUT TIME ZONE DEFAULT CURRENT_TIMESTAMP
        )
        """ % id_type
        db.execute(_it_sa.text(ddl))
        db.execute(_it_sa.text("CREATE INDEX IF NOT EXISTS ix_account_trade_ledger_time ON account_trade_ledger(transaction_time)"))
        db.commit()

def _it_float(value, default=0.0):
    try:
        if value is None: return default
        raw = str(value).strip().replace(",", "").replace("$", "").replace("USDT", "").replace(" ", "")
        if not raw or raw in ("-", "—", "N/A", "null", "None"): return default
        number = float(raw)
        return number if _it_math.isfinite(number) else default
    except (TypeError, ValueError, OverflowError):
        return default

def _it_clean_time(value):
    raw = str(value or "").strip()
    if not raw: return None
    try:
        if raw.isdigit():
            n = int(raw)
            if n > 10**14: n = n / 1000.0
            if n > 10**11:
                return _it_dt.datetime.fromtimestamp(n / 1000.0, _it_dt.timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
            if n > 10**8:
                return _it_dt.datetime.fromtimestamp(n, _it_dt.timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
        parsed = _it_dt.datetime.fromisoformat(raw.replace("Z", "+00:00"))
        if parsed.tzinfo is None: parsed = parsed.replace(tzinfo=_it_dt.timezone.utc)
        return parsed.astimezone(_it_dt.timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
    except Exception:
        return raw[:80]

def _it_upsert(records):
    if not records: return 0
    _it_ensure_ledger()
    sql = _it_sa.text("""
      INSERT INTO account_trade_ledger
        (external_id,strategy_name,market_type,symbol,trade_id,income_type,transaction_time,asset,amount_asset,amount_usdt,realized_pnl_usdt,commission_usdt,funding_usdt,source,raw_json)
      VALUES
        (:external_id,:strategy_name,:market_type,:symbol,:trade_id,:income_type,:transaction_time,:asset,:amount_asset,:amount_usdt,:realized_pnl_usdt,:commission_usdt,:funding_usdt,:source,:raw_json)
      ON CONFLICT(external_id) DO NOTHING
    """)
    inserted = 0
    with SessionLocal() as db:
        for item in records:
            result = db.execute(sql, item)
            if result.rowcount and result.rowcount > 0: inserted += result.rowcount
        db.commit()
    return inserted

def _it_summary_data():
    with SessionLocal() as db:
        dialect = db.get_bind().dialect.name
        if dialect == "postgresql":
            exists = db.execute(_it_sa.text("SELECT EXISTS (SELECT 1 FROM information_schema.tables WHERE table_schema='public' AND table_name='account_trade_ledger')")).scalar()
        else:
            exists = db.execute(_it_sa.text("SELECT EXISTS (SELECT 1 FROM sqlite_master WHERE type='table' AND name='account_trade_ledger')")).scalar()
        if not exists:
            return {"has_personal_records":False,"record_count":0,"included_usdt_record_count":0,"excluded_non_usdt_or_unconverted_count":0,
              "tax_method":"Conservative planning reserve: 30% of each positive realised-PnL ledger event; negative events do not reduce the reserve.",
              "ledger_table_available":False,
              "summary":{"record_count":0,"realized_pnl_usdt":0,"positive_realized_pnl_usdt":0,"gross_loss_usdt":0,"commission_usdt":0,"funding_usdt":0,
                "economic_net_pnl_usdt":0,"tax_rate":_IT_TAX_RATE,"tax_reserve_usdt":0,"net_after_tax_reserve_usdt":0},
              "by_strategy":[],"recent":[],"generated_at_utc":_it_dt.datetime.now(_it_dt.timezone.utc).isoformat()}
        mappings = db.execute(_it_sa.text("""
          SELECT id,external_id,strategy_name,market_type,symbol,trade_id,income_type,transaction_time,asset,amount_asset,amount_usdt,
                 realized_pnl_usdt,commission_usdt,funding_usdt,source,created_at
          FROM account_trade_ledger ORDER BY transaction_time DESC NULLS LAST, id DESC LIMIT 20000
        """)).mappings().all()
    rows = [dict(x) for x in mappings]
    included = [r for r in rows if str(r.get("asset") or "").upper() == "USDT" and r.get("amount_usdt") is not None]
    def f(v): return _it_float(v, 0.0)
    def aggregate(items):
        pnl = sum(f(r.get("realized_pnl_usdt")) for r in items if str(r.get("income_type") or "").upper() == "REALIZED_PNL")
        positive = sum(max(0.0, f(r.get("realized_pnl_usdt"))) for r in items if str(r.get("income_type") or "").upper() == "REALIZED_PNL")
        loss = sum(abs(min(0.0, f(r.get("realized_pnl_usdt"))) ) for r in items if str(r.get("income_type") or "").upper() == "REALIZED_PNL")
        commission = sum(f(r.get("commission_usdt")) for r in items)
        funding = sum(f(r.get("funding_usdt")) for r in items)
        reserve = positive * _IT_TAX_RATE
        return {"record_count":len(items),"realized_pnl_usdt":round(pnl,8),"positive_realized_pnl_usdt":round(positive,8),
          "gross_loss_usdt":round(loss,8),"commission_usdt":round(commission,8),"funding_usdt":round(funding,8),
          "economic_net_pnl_usdt":round(pnl+commission+funding,8),"tax_rate":_IT_TAX_RATE,
          "tax_reserve_usdt":round(reserve,8),"net_after_tax_reserve_usdt":round(pnl+commission+funding-reserve,8)}
    overall = aggregate(included)
    by = {}
    for r in included: by.setdefault(str(r.get("strategy_name") or "Unlabelled"), []).append(r)
    strategies = []
    for name, group in by.items():
        v = aggregate(group); v["strategy_name"] = name
        v["loss_to_gain_ratio"] = round(v["gross_loss_usdt"] / v["positive_realized_pnl_usdt"],4) if v["positive_realized_pnl_usdt"] > 0 else None
        v["fee_funding_usdt"] = round(v["commission_usdt"] + v["funding_usdt"],8)
        if v["net_after_tax_reserve_usdt"] <= 0: v["status"] = "NON_POSITIVE_AFTER_RESERVE"
        elif v["gross_loss_usdt"] >= v["positive_realized_pnl_usdt"]: v["status"] = "LOSSES_MATCH_OR_EXCEED_GAINS"
        elif v["fee_funding_usdt"] < -v["positive_realized_pnl_usdt"] * 0.1: v["status"] = "HIGH_COST_DRAG"
        else: v["status"] = "POSITIVE_IN_IMPORTED_RECORDS"
        strategies.append(v)
    strategies.sort(key=lambda x:x["net_after_tax_reserve_usdt"])
    recent = []
    for r in rows[:500]:
        asset = str(r.get("asset") or "").upper()
        included_row = asset == "USDT" and r.get("amount_usdt") is not None
        pnl = f(r.get("realized_pnl_usdt")) if included_row and str(r.get("income_type") or "").upper() == "REALIZED_PNL" else 0.0
        commission = f(r.get("commission_usdt")) if included_row else 0.0
        funding = f(r.get("funding_usdt")) if included_row else 0.0
        reserve = max(0.0,pnl)*_IT_TAX_RATE
        recent.append({"id":r.get("id"),"time":r.get("transaction_time"),"strategy_name":r.get("strategy_name"),"market_type":r.get("market_type"),
          "symbol":r.get("symbol"),"trade_id":r.get("trade_id"),"income_type":r.get("income_type"),"asset":asset,"amount_asset":r.get("amount_asset"),
          "realized_pnl_usdt":round(pnl,8),"commission_usdt":round(commission,8),"funding_usdt":round(funding,8),
          "tax_reserve_usdt":round(reserve,8),"net_after_reserve_usdt":round(pnl+commission+funding-reserve,8),"source":r.get("source"),"included_in_usdt_totals":included_row})
    return {"has_personal_records":bool(rows),"record_count":len(rows),"included_usdt_record_count":len(included),
      "excluded_non_usdt_or_unconverted_count":max(0,len(rows)-len(included)),"tax_method":"Conservative planning reserve: 30% of each positive realised-PnL ledger event; negative events do not reduce the reserve.",
      "summary":overall,"by_strategy":strategies,"recent":recent,"generated_at_utc":_it_dt.datetime.now(_it_dt.timezone.utc).isoformat()}

def _it_p2p_quote(trade_type):
    query = _it_urlparse.urlencode({"fiat":"INR","asset":"USDT","tradeType":trade_type})
    url = "https://www.binance.com/bapi/c2c/v1/public/c2c/agent/quote-price?" + query
    req = _it_urlrequest.Request(url, headers={"User-Agent":"Mozilla/5.0","Accept":"application/json"})
    try:
        with _it_urlrequest.urlopen(req, timeout=6) as response:
            payload = _it_json.loads(response.read(500000).decode("utf-8", "replace"))
        data = payload.get("data") if isinstance(payload,dict) else None
        candidates = data if isinstance(data,list) else ([data] if isinstance(data,dict) else [])
        for item in candidates:
            if not isinstance(item,dict): continue
            for key in ("price","referencePrice","reference_price","marketPrice","value"):
                val = _it_float(item.get(key),0)
                if val > 0: return val
        return None
    except Exception:
        return None

@app.get("/api/profit-tax/rates")
def api_it_p2p_rates():
    buy = _it_p2p_quote("BUY")
    sell = _it_p2p_quote("SELL")
    return jsonify({"source":"Binance P2P public quote-price endpoint","fiat":"INR","asset":"USDT",
      "buy_quote_inr_per_usdt":buy,"sell_quote_inr_per_usdt":sell,"as_of_utc":_it_dt.datetime.now(_it_dt.timezone.utc).isoformat(),
      "note":"Reference quotes only. Actual P2P prices depend on payment method, advertisement, limits, and counterparty; the app does not place P2P orders."})

@app.get("/api/profit-tax/summary")
def api_it_tax_summary():
    try: return jsonify(_it_summary_data())
    except Exception as exc: return jsonify({"error":"Unable to read personal trade ledger: "+str(exc)[:300]}),500

def _it_parse_binance_income(row, strategy_name, market_type, source):
    typ = str(row.get("incomeType") or row.get("income_type") or "").upper()
    if typ not in ("REALIZED_PNL","COMMISSION","FUNDING_FEE"): return None
    asset = str(row.get("asset") or "USDT").upper()
    amount = _it_float(row.get("income"),0.0)
    amount_usdt = amount if asset == "USDT" else None
    realised = amount if typ == "REALIZED_PNL" and asset == "USDT" else 0.0
    commission = amount if typ == "COMMISSION" and asset == "USDT" else 0.0
    funding = amount if typ == "FUNDING_FEE" and asset == "USDT" else 0.0
    tran = str(row.get("tranId") or row.get("tradeId") or "")
    time_value = row.get("time")
    symbol = str(row.get("symbol") or "")
    ext = source + ":" + (tran or _it_hashlib.sha256(_it_json.dumps(row,sort_keys=True).encode()).hexdigest()) + ":" + typ
    return {"external_id":ext,"strategy_name":strategy_name,"market_type":market_type,"symbol":symbol,"trade_id":str(row.get("tradeId") or ""),
      "income_type":typ,"transaction_time":_it_clean_time(time_value),"asset":asset,"amount_asset":amount,"amount_usdt":amount_usdt,
      "realized_pnl_usdt":realised,"commission_usdt":commission,"funding_usdt":funding,"source":source,
      "raw_json":_it_json.dumps(row,ensure_ascii=False,default=str)[:12000]}

@app.post("/api/profit-tax/sync")
def api_it_tax_sync():
    data = request.get_json(silent=True) or {}
    api_key = str(data.get("api_key") or "").strip()
    api_secret = str(data.get("api_secret") or "").strip()
    if not api_key or not api_secret: return jsonify({"error":"Enter a read-only Binance API key and secret for this request."}),400
    try:
        days = max(1,min(90,int(data.get("lookback_days",30))))
    except Exception: days = 30
    strategy = str(data.get("strategy_name") or "Unattributed Binance Futures").strip()[:100] or "Unattributed Binance Futures"
    end_ms = int(_it_time.time()*1000)
    start_ms = end_ms - days*86400000
    records = []
    cursor = start_ms
    try:
        while cursor < end_ms:
            window_end = min(end_ms, cursor + 7*86400000 - 1)
            page_start = cursor
            page_loops = 0
            while page_start <= window_end and page_loops < 15:
                params = {"startTime":page_start,"endTime":window_end,"limit":1000,"timestamp":int(_it_time.time()*1000),"recvWindow":5000}
                query = _it_urlparse.urlencode(params)
                signature = _it_hmac.new(api_secret.encode("utf-8"),query.encode("utf-8"),_it_hashlib.sha256).hexdigest()
                url = "https://fapi.binance.com/fapi/v1/income?" + query + "&signature=" + signature
                req = _it_urlrequest.Request(url,headers={"X-MBX-APIKEY":api_key,"Accept":"application/json","User-Agent":"Binance-Intel-ReadOnly"})
                try:
                    with _it_urlrequest.urlopen(req,timeout=15) as response:
                        payload = _it_json.loads(response.read(4000000).decode("utf-8","replace"))
                except _it_urlerror.HTTPError as exc:
                    raise RuntimeError("Binance Futures income request failed (HTTP "+str(exc.code)+"). Check read-only/Futures permissions, IP restrictions, and the selected date range.")
                if isinstance(payload,dict) and payload.get("code") is not None and _it_float(payload.get("code"),0) < 0:
                    raise RuntimeError("Binance rejected the request: "+str(payload.get("msg") or "check API permissions and date range")[:180])
                if not isinstance(payload,list): raise RuntimeError("Binance returned an unexpected response format.")
                if not payload: break
                for row in payload:
                    item = _it_parse_binance_income(row,strategy,"FUTURES","BINANCE_FUTURES_INCOME_API")
                    if item: records.append(item)
                page_loops += 1
                if len(payload) < 1000: break
                max_time = max([int(x.get("time") or page_start) for x in payload])
                if max_time < page_start or max_time >= window_end: break
                page_start = max_time + 1
            cursor = window_end + 1
        inserted = _it_upsert(records)
        result = _it_summary_data()
        result["sync"] = {"fetched_supported_income_records":len(records),"new_records_saved":inserted,"lookback_days":days,
          "credentials_saved":False,"source":"Binance USD-M Futures income history","note":"Only realised PnL, commissions, and funding-fee entries are imported. Other assets are retained but excluded from USDT totals; copy-portfolio attribution is not guaranteed."}
        return jsonify(result)
    except Exception as exc:
        return jsonify({"error":str(exc)[:500],"credentials_saved":False}),400

@app.post("/api/profit-tax/import")
def api_it_tax_import():
    f = request.files.get("file")
    if not f: return jsonify({"error":"Choose a Binance CSV export first."}),400
    raw = f.read(10000001)
    if len(raw) > 10000000: return jsonify({"error":"CSV is larger than 10 MB. Export a shorter date range."}),413
    try: decoded = raw.decode("utf-8-sig")
    except Exception: return jsonify({"error":"CSV must be UTF-8. Re-export it from Binance and try again."}),400
    try:
        reader = _it_csv.DictReader(_it_io.StringIO(decoded))
        if not reader.fieldnames: return jsonify({"error":"CSV headers were not found."}),400
        market = str(request.form.get("market_type") or "FUTURES").upper()
        if market not in ("SPOT","FUTURES"): market="FUTURES"
        strategy = str(request.form.get("strategy_name") or "Imported Binance records").strip()[:100] or "Imported Binance records"
        records = []
        for line_no, source_row in enumerate(reader, start=2):
            row = {str(k or "").strip().lower().replace("_"," ").replace("-"," "):str(v or "").strip() for k,v in source_row.items()}
            def value(*names):
                for name in names:
                    if row.get(name): return row.get(name)
                for name in names:
                    for k,v in row.items():
                        if name in k and v: return v
                return None
            typ = (value("income type","incometype","type","record type") or "").upper().replace(" ","_")
            pnl_raw = value("realized pnl","realised pnl","realized profit","realised profit","closed pnl","closed profit","pnl usdt","pnl","profit")
            income_raw = value("income")
            commission_raw = value("commission","commission usdt","fee","fees")
            funding_raw = value("funding fee","funding","funding usdt")
            if "UNREALIZED" in typ: continue
            if "REALIZED" in typ: typ="REALIZED_PNL"
            elif "COMMISSION" in typ: typ="COMMISSION"
            elif "FUNDING" in typ: typ="FUNDING_FEE"
            elif pnl_raw is not None: typ="REALIZED_PNL"
            elif commission_raw is not None or funding_raw is not None: typ="COST_ONLY"
            else: continue
            asset = str(value("asset","income asset","pnl asset","settlement asset") or "USDT").upper()
            commission_asset = str(value("commission asset","fee asset") or asset).upper()
            pnl = _it_float(pnl_raw if pnl_raw is not None else income_raw,0.0) if typ=="REALIZED_PNL" else 0.0
            commission = _it_float(income_raw if typ=="COMMISSION" else commission_raw,0.0) if commission_asset=="USDT" else 0.0
            funding = _it_float(income_raw if typ=="FUNDING_FEE" else funding_raw,0.0) if asset=="USDT" else 0.0
            if typ=="COMMISSION" and asset=="USDT" and commission_raw is None: commission=_it_float(income_raw,0.0)
            if typ=="FUNDING_FEE" and funding_raw is None: funding=_it_float(income_raw,0.0)
            if asset!="USDT": pnl=0.0
            if typ=="REALIZED_PNL" and pnl_raw is None and income_raw is None: continue
            stamp = value("time","timestamp","date","datetime","transaction time","create time")
            symbol = str(value("symbol","pair","market") or "")
            trade_id = str(value("trade id","tradeid","tran id","tranid","transaction id","order id","id") or "")
            fingerprint = _it_hashlib.sha256((_it_json.dumps(source_row,sort_keys=True,ensure_ascii=False)).encode("utf-8")).hexdigest()
            ext = "CSV_IMPORT:"+fingerprint
            if typ=="COST_ONLY":
                if commission != 0: typ="COMMISSION"
                elif funding != 0: typ="FUNDING_FEE"
                else: continue
            amount_asset = pnl if typ=="REALIZED_PNL" else (commission if typ=="COMMISSION" else funding)
            amount_usdt = amount_asset if asset=="USDT" else None
            records.append({"external_id":ext,"strategy_name":strategy,"market_type":market,"symbol":symbol,"trade_id":trade_id,"income_type":typ,
              "transaction_time":_it_clean_time(stamp),"asset":asset,"amount_asset":amount_asset,"amount_usdt":amount_usdt,
              "realized_pnl_usdt":pnl,"commission_usdt":commission,"funding_usdt":funding,"source":"CSV_IMPORT",
              "raw_json":_it_json.dumps(source_row,ensure_ascii=False,default=str)[:12000]})
        if not records:
            return jsonify({"error":"No supported realised-PnL, commission, or funding records were recognised. Headers found: "+", ".join(reader.fieldnames[:30])}),400
        inserted = _it_upsert(records)
        result = _it_summary_data()
        result["import"] = {"recognised_records":len(records),"new_records_saved":inserted,"duplicates_ignored":max(0,len(records)-inserted),"source":"CSV_IMPORT"}
        return jsonify(result)
    except Exception as exc:
        return jsonify({"error":"CSV import failed: "+str(exc)[:300]}),400

@app.get("/api/trade-behaviour/summary")
def api_it_trade_behaviour_summary():
    try:
        with SessionLocal() as db:
            by_market = db.execute(_it_sa.text("""
              SELECT t.market_type, COUNT(p.id) AS closed_trades,
                SUM(CASE WHEN p.close_pnl>0 THEN 1 ELSE 0 END) AS wins,
                SUM(CASE WHEN p.close_pnl<0 THEN 1 ELSE 0 END) AS losses,
                SUM(CASE WHEN p.close_pnl=0 THEN 1 ELSE 0 END) AS flat,
                SUM(CASE WHEN p.close_pnl>0 THEN p.close_pnl ELSE 0 END) AS gross_profit,
                SUM(CASE WHEN p.close_pnl<0 THEN ABS(p.close_pnl) ELSE 0 END) AS gross_loss,
                SUM(p.close_pnl) AS net_pnl,
                AVG(p.mae_pct) AS avg_mae_pct, AVG(p.mfe_pct) AS avg_mfe_pct,
                SUM(CASE WHEN p.went_adverse_first THEN 1 ELSE 0 END) AS adverse_first,
                SUM(CASE WHEN p.mae_pct IS NOT NULL OR p.mfe_pct IS NOT NULL THEN 1 ELSE 0 END) AS path_records
              FROM positions p JOIN traders t ON t.id=p.trader_id
              WHERE t.exchange='BINANCE' AND p.close_pnl IS NOT NULL GROUP BY t.market_type
            """)).mappings().all()
            by_trader = db.execute(_it_sa.text("""
              SELECT t.id AS trader_id,t.nickname,t.portfolio_id,t.profile_url,t.market_type,t.start_time_ms,t.copier_pnl,t.roi,t.mdd,
                COUNT(p.id) AS closed_trades,SUM(CASE WHEN p.close_pnl>0 THEN 1 ELSE 0 END) AS wins,
                SUM(CASE WHEN p.close_pnl<0 THEN 1 ELSE 0 END) AS losses,
                SUM(CASE WHEN p.close_pnl>0 THEN p.close_pnl ELSE 0 END) AS gross_profit,
                SUM(CASE WHEN p.close_pnl<0 THEN ABS(p.close_pnl) ELSE 0 END) AS gross_loss,
                SUM(p.close_pnl) AS net_pnl,AVG(p.mae_pct) AS avg_mae_pct,AVG(p.mfe_pct) AS avg_mfe_pct,
                SUM(CASE WHEN p.went_adverse_first THEN 1 ELSE 0 END) AS adverse_first,
                SUM(CASE WHEN p.mae_pct IS NOT NULL OR p.mfe_pct IS NOT NULL THEN 1 ELSE 0 END) AS path_records
              FROM positions p JOIN traders t ON t.id=p.trader_id
              WHERE t.exchange='BINANCE' AND p.close_pnl IS NOT NULL
              GROUP BY t.id,t.nickname,t.portfolio_id,t.profile_url,t.market_type,t.start_time_ms,t.copier_pnl,t.roi,t.mdd
              ORDER BY SUM(p.close_pnl) DESC NULLS LAST LIMIT 100
            """)).mappings().all()
            recent = db.execute(_it_sa.text("""
              SELECT p.id,p.trader_id,t.nickname,t.market_type,t.profile_url,p.symbol,p.side,p.leverage,p.margin_mode,p.entry_price,p.exit_price,p.close_pnl,p.roi_pct,
                p.opened_ms,p.closed_ms,p.mae_pct,p.mfe_pct,p.went_adverse_first,p.path_status,p.coverage_pct,p.candles_covered
              FROM positions p JOIN traders t ON t.id=p.trader_id
              WHERE t.exchange='BINANCE' AND p.close_pnl IS NOT NULL
              ORDER BY CASE WHEN p.closed_ms IS NULL THEN 1 ELSE 0 END,p.closed_ms DESC,p.id DESC LIMIT 250
            """)).mappings().all()
        def val(x): return _it_float(x,0.0)
        def metrics(r):
            n=val(r.get("closed_trades")); wins=val(r.get("wins")); losses=val(r.get("losses"))
            gp=val(r.get("gross_profit")); gl=val(r.get("gross_loss")); net=val(r.get("net_pnl"))
            return {**dict(r),"win_rate_pct":round(100*wins/(wins+losses),2) if wins+losses else None,
              "profit_factor":round(gp/gl,4) if gl>0 else (None if gp<=0 else None),
              "avg_win_usdt":round(gp/wins,6) if wins else None,"avg_loss_usdt":round(gl/losses,6) if losses else None,
              "path_coverage_pct":round(100*val(r.get("path_records"))/n,2) if n else 0,
              "adverse_first_pct":round(100*val(r.get("adverse_first"))/n,2) if n else None,
              "net_pnl":round(net,8)}
        markets=[metrics(r) for r in by_market]
        traders=[metrics(r) for r in by_trader]
        trades=[]
        for r in recent:
            x=dict(r)
            for key in ("opened_ms","closed_ms"):
                try: x[key]=int(x[key]) if x.get(key) is not None else None
                except Exception: x[key]=None
            trades.append(x)
        return jsonify({"mode":"STORED_PUBLIC_LEAD_HISTORY_NOT_PERSONAL_PNL","markets":markets,"traders":traders,"recent_closed_positions":trades,
          "data_note":"These are stored public lead-trader positions. Coverage, fees, funding, leverage fields and trade paths may be incomplete; this is research evidence, not your own account results.",
          "generated_at_utc":_it_dt.datetime.now(_it_dt.timezone.utc).isoformat()})
    except Exception as exc:
        return jsonify({"error":"Trade-behaviour analysis failed: "+str(exc)[:300]}),500

# Tighten ranking using bounded SQL aggregates; never materialize every Position ORM object.
def _mt_report(market_type="FUTURES", min_closed_trades=10, min_profit_factor=1.2, max_mdd_pct=20, min_roi_7d=-5, max_selected=5):
    market_type=(market_type or "FUTURES").upper()
    if market_type not in ("FUTURES","SPOT"): raise ValueError("market_type must be FUTURES or SPOT")
    min_closed_trades=max(1,min(int(min_closed_trades),500)); min_profit_factor=max(.5,min(float(min_profit_factor),10))
    max_mdd_pct=max(1,min(float(max_mdd_pct),100)); min_roi_7d=max(-100,min(float(min_roi_7d),100)); max_selected=max(1,min(int(max_selected),10))
    with SessionLocal() as db:
        traders=list(db.scalars(select(Trader).where(Trader.exchange=="BINANCE",Trader.market_type==market_type).order_by(Trader.last_seen.desc().nullslast(),Trader.id.asc())))
        aggregate_rows=db.execute(_it_sa.text("""
            SELECT p.trader_id, COUNT(*) AS closed_count,
              SUM(CASE WHEN p.close_pnl>0 THEN 1 ELSE 0 END) AS wins,
              SUM(CASE WHEN p.close_pnl<0 THEN 1 ELSE 0 END) AS losses,
              SUM(CASE WHEN p.close_pnl>0 THEN p.close_pnl ELSE 0 END) AS gross_profit,
              SUM(CASE WHEN p.close_pnl<0 THEN ABS(p.close_pnl) ELSE 0 END) AS gross_loss,
              SUM(p.close_pnl) AS net_pnl,
              AVG(p.mae_pct) AS avg_mae_pct, AVG(p.mfe_pct) AS avg_mfe_pct,
              SUM(CASE WHEN p.mae_pct IS NOT NULL OR p.mfe_pct IS NOT NULL THEN 1 ELSE 0 END) AS path_count
            FROM positions p JOIN traders t ON t.id=p.trader_id
            WHERE t.exchange='BINANCE' AND t.market_type=:market_type AND p.close_pnl IS NOT NULL
            GROUP BY p.trader_id
        """),{"market_type":market_type}).mappings().all()
        stats={int(r["trader_id"]):dict(r) for r in aggregate_rows}
        symbol_rows=db.execute(_it_sa.text("""
            SELECT p.trader_id,p.symbol FROM positions p JOIN traders t ON t.id=p.trader_id
            WHERE t.exchange='BINANCE' AND t.market_type=:market_type AND p.close_pnl IS NOT NULL
              AND p.symbol IS NOT NULL AND p.closed_ms >= :since_ms
            GROUP BY p.trader_id,p.symbol
        """),{"market_type":market_type,"since_ms":int((_it_time.time()-90*86400)*1000)}).mappings().all()
        symbols={}
        for r in symbol_rows: symbols.setdefault(int(r["trader_id"]),[]).append(str(r["symbol"]))
    now=utcnow(); rows=[]
    for t in traders:
        try: periods=json.loads(t.period_metrics or "{}")
        except Exception: periods={}
        def pm(period,metric):
            group=periods.get(period,{}) if isinstance(periods,dict) else {}
            return _it_float(group.get(metric)) if isinstance(group,dict) else None
        roi7,roi30,roi90,roi365=[pm(k,"roi") for k in ("7D","30D","90D","365D")]
        mdd7,mdd30,mdd365=[pm(k,"mdd") for k in ("7D","30D","365D")]
        z=stats.get(int(t.id),{})
        closed=int(z.get("closed_count") or 0); wins=int(z.get("wins") or 0); losses=int(z.get("losses") or 0)
        gp=_it_float(z.get("gross_profit"),0) or 0; gl=_it_float(z.get("gross_loss"),0) or 0
        pf=gp/gl if gl>0 else None
        net=_it_float(z.get("net_pnl"),0) or 0
        seen=t.last_seen
        if seen and getattr(seen,"tzinfo",None) is not None: seen=seen.replace(tzinfo=None)
        age=(now-seen).total_seconds()/86400 if seen else None
        reasons=[]
        if age is None or age>7: reasons.append("STALE_PROFILE_OVER_7_DAYS")
        if market_type=="FUTURES" and roi7 is None: reasons.append("MISSING_SOURCE_7D_ROI")
        if market_type=="FUTURES" and mdd7 is None: reasons.append("MISSING_SOURCE_7D_MDD")
        if market_type=="SPOT" and roi30 is None: reasons.append("MISSING_SOURCE_30D_ROI_FOR_SPOT")
        if mdd30 is None: reasons.append("MISSING_SOURCE_30D_MDD")
        recent_roi = roi7 if roi7 is not None else roi30
        if recent_roi is not None and recent_roi<min_roi_7d: reasons.append("RECENT_ROI_BELOW_FLOOR")
        if mdd7 is not None and abs(mdd7)>max_mdd_pct: reasons.append("7D_MDD_LIMIT_EXCEEDED")
        if mdd30 is not None and abs(mdd30)>max_mdd_pct: reasons.append("30D_MDD_LIMIT_EXCEEDED")
        if closed<min_closed_trades: reasons.append("INSUFFICIENT_STORED_CLOSED_TRADES")
        if pf is None: reasons.append("PROFIT_FACTOR_NOT_ESTIMABLE_FROM_STORED_TRADES")
        elif pf<min_profit_factor: reasons.append("PROFIT_FACTOR_BELOW_FLOOR")
        duration=None
        try:
            start_ms=int(t.start_time_ms or 0)
            if start_ms>0: duration=max(0.0,(_it_time.time()*1000-start_ms)/86400000.0)
        except Exception: duration=None
        copier=_it_float(t.copier_pnl)
        if duration is None: reasons.append("MISSING_TRADER_DURATION")
        elif duration<30: reasons.append("INSUFFICIENT_TRADER_TENURE_UNDER_30_DAYS")
        if copier is None: reasons.append("MISSING_COPIER_PNL")
        elif copier<=0: reasons.append("COPIER_PNL_NOT_POSITIVE")
        score=50+max(-20,min(20,recent_roi or 0))*.7+max(-30,min(30,roi30 or 0))*.35+max(-50,min(50,roi90 or 0))*.1
        score+=(min(pf,3)-1)*10 if pf is not None else -12
        score-=abs(mdd30)*.45 if mdd30 is not None else 15
        if duration is not None: score+=min(15.0,max(0.0,duration/365.0*15.0))
        if copier is not None and copier>0: score+=min(15.0,_it_math.log1p(copier)*2.0)
        if mdd365 is None: score-=5.0
        syms=symbols.get(int(t.id),[])
        rows.append({"id":t.id,"nickname":t.nickname,"portfolio_id":t.portfolio_id,"profile_url":t.profile_url,"market_type":t.market_type,
            "last_seen":_iso(t.last_seen),"age_days":round(age,2) if age is not None else None,
            "trader_duration_days":round(duration,2) if duration is not None else None,"roi_7d":roi7,"roi_30d":roi30,"roi_90d":roi90,"roi_365d":roi365,
            "mdd_7d":mdd7,"mdd_30d":mdd30,"mdd_365d":mdd365,"stored_closed_trades":closed,"source_total_positions":t.total_positions,
            "profit_factor":round(pf,4) if pf is not None else None,"win_rate_pct":round(100*wins/(wins+losses),2) if wins+losses else None,
            "net_realized_pnl":round(net,8),"average_win":round(gp/wins,8) if wins else None,"average_loss":round(gl/losses,8) if losses else None,
            "stored_path_coverage_pct":round(100*int(z.get("path_count") or 0)/closed,2) if closed else 0,
            "symbols":syms,"copier_pnl":copier,"score":round(max(0,min(100,score)),2),"eligible":not reasons,"reasons":list(dict.fromkeys(reasons)),
            "selected":False,"allocation_pct":0})
    rows.sort(key=lambda x:(x["eligible"],x["score"],x["stored_closed_trades"]),reverse=True)
    eligible=[x for x in rows if x["eligible"]]; chosen=[]
    while eligible and len(chosen)<max_selected:
        def adjusted(x):
            syms=set(x.get("symbols") or []); overlap=0.0
            for y in chosen:
                ys=set(y.get("symbols") or []); union=syms|ys
                if union: overlap=max(overlap,len(syms & ys)/len(union))
            return _it_float(x.get("score"),0)-overlap*18
        best=max(eligible,key=adjusted)
        best["selected"]=True; best["selection_reason"]="Risk score includes duration/copier PnL and recent symbol-overlap penalty"
        chosen.append(best); eligible.remove(best)
    if chosen:
        weights={str(x["id"]):max(1.0,_it_float(x.get("score"),1))/max(5.0,abs(_it_float(x.get("mdd_30d"),max_mdd_pct))) for x in chosen}
        total=sum(weights.values()) or 1
        for x in chosen: x["allocation_pct"]=round(min(35.0,100*weights[str(x["id"])]/total),2)
    chosen_ids={int(x["id"]) for x in chosen}
    for row in rows:
        row["decision"]="SELECTED_FOR_PAPER_MODE" if int(row["id"]) in chosen_ids else ("ELIGIBLE_NOT_SELECTED" if row["eligible"] else "BLOCKED")
        if row["eligible"] and not row["selected"]: row["selection_reason"]="Eligible but outside the paper shortlist limit"
    return {"mode":"PAPER_ONLY_NO_ORDERS","market_type":market_type,"evaluated_at_utc":utcnow().isoformat()+"Z",
        "monitored_count":len(rows),"eligible_count":sum(x["eligible"] for x in rows),"blocked_count":sum(not x["eligible"] for x in rows),
        "selected_count":len(chosen),"selected_portfolios":[{k:x.get(k) for k in ("id","nickname","portfolio_id","profile_url","score","allocation_pct","roi_7d","roi_30d","roi_90d","mdd_7d","mdd_30d","mdd_365d","profit_factor","copier_pnl","trader_duration_days","stored_closed_trades","symbols","selection_reason")} for x in chosen],
        "candidates":rows[:1000],"candidate_rows_returned":min(1000,len(rows)),"candidates_omitted_from_response":max(0,len(rows)-1000),
        "settings":{"min_closed_trades":min_closed_trades,"min_profit_factor":min_profit_factor,"max_mdd_pct":max_mdd_pct,"min_roi_7d":min_roi_7d,"max_selected":max_selected},
        "policy_notes":["A profile is blocked if trader tenure is under 30 days or copier PnL is missing/non-positive.","Scores incorporate duration and copier PnL; missing 365D MDD is penalised.","This is a paper-research shortlist, not a live copy instruction or profit guarantee."]}
'''
insert_once(app, 'def _run_scheduled_task(kind, market_type, target, args):', backend + '\n', 'def _it_ensure_ledger():', "account ledger and analysis endpoints")

# Make JS routes call real data-backed workflows, including an enhanced Trade behaviour summary.
js = ROOT / "static" / "app.js"
js_code = r'''
function itMoney(v, digits=2){const n=Number(v);return Number.isFinite(n)?n.toLocaleString('en-US',{minimumFractionDigits:digits,maximumFractionDigits:digits}):'—'}
function itUsdt(v){const n=Number(v);return Number.isFinite(n)?itMoney(n,2)+' USDT':'—'}
function itInr(v){const n=Number(v);return Number.isFinite(n)?'₹'+itMoney(n,2):'—'}
function itSafeRate(){const n=Number($('#pt-rate')&&$('#pt-rate').value);return Number.isFinite(n)&&n>0?n:null}
function itLoadStrategyWatch(d){
 const rows=d.by_strategy||[];const rate=itSafeRate();const positive=rows.filter(x=>Number(x.net_after_tax_reserve_usdt)>0).length;const risk=rows.length-positive;
 $('#stw-count').textContent=String(rows.length);$('#stw-positive').textContent=String(positive);$('#stw-risk').textContent=String(risk);
 $('#stw-net').textContent=itUsdt(d.summary&&d.summary.net_after_tax_reserve_usdt);
 $('#stw-net-inr').textContent='INR: '+(rate?itInr(Number(d.summary&&d.summary.net_after_tax_reserve_usdt||0)*rate):'rate unavailable');
 $('#stw-alert').textContent=!rows.length?'No personal strategy records yet. Import or sync your Binance account ledger; public lead-trader positions are intentionally excluded.':(risk?'Warning: '+risk+' of '+rows.length+' strategy labels are non-positive after tax reserve or have losses at least as large as positive gains. Investigate before allocating more capital.':'All imported labels are positive after the conservative reserve in this recorded period; future profitability is not guaranteed.');
 $('#stw-rows').innerHTML=rows.length?rows.map(x=>{const ratio=x.loss_to_gain_ratio==null?'N/A':itMoney(x.loss_to_gain_ratio*100,1)+'%';const cost=Number(x.commission_usdt||0)+Number(x.funding_usdt||0);const warn=x.status==='POSITIVE_IN_IMPORTED_RECORDS'?'Monitor; no guarantee':x.status==='HIGH_COST_DRAG'?'WARNING: high cost drag':x.status==='LOSSES_MATCH_OR_EXCEED_GAINS'?'WARNING: losses match/exceed gains':'WARNING: non-positive after reserve';return '<tr><td><strong>'+esc(x.strategy_name)+'</strong></td><td>'+n(x.record_count,0)+'</td><td>'+itUsdt(x.positive_realized_pnl_usdt)+'</td><td class="negative">'+itUsdt(x.gross_loss_usdt)+'</td><td>'+ratio+'</td><td>'+itUsdt(cost)+'</td><td>'+itUsdt(x.tax_reserve_usdt)+'</td><td class="'+colorNum(x.economic_net_pnl_usdt)+'">'+itUsdt(x.economic_net_pnl_usdt)+'</td><td class="'+colorNum(x.net_after_tax_reserve_usdt)+'">'+itUsdt(x.net_after_tax_reserve_usdt)+'</td><td style="white-space:normal;min-width:220px">'+esc(warn)+'</td></tr>'}).join(''):'<tr><td colspan="10" class="empty-state">No imported personal strategy records.</td></tr>';
}
function itRenderTax(d){
 const s=d.summary||{};const rate=itSafeRate();const get=(k)=>Number(s[k]||0);
 $('#pt-positive').textContent=itUsdt(s.positive_realized_pnl_usdt);$('#pt-tax').textContent=itUsdt(s.tax_reserve_usdt);$('#pt-net').textContent=itUsdt(s.economic_net_pnl_usdt);$('#pt-after').textContent=itUsdt(s.net_after_tax_reserve_usdt);
 $('#pt-positive-inr').textContent='INR: '+(rate?itInr(get('positive_realized_pnl_usdt')*rate):'—');$('#pt-tax-inr').textContent='INR: '+(rate?itInr(get('tax_reserve_usdt')*rate):'—');$('#pt-net-inr').textContent='INR: '+(rate?itInr(get('economic_net_pnl_usdt')*rate):'—');$('#pt-after-inr').textContent='INR: '+(rate?itInr(get('net_after_tax_reserve_usdt')*rate):'—');
 $('#pt-ledger-status').textContent=d.record_count+' personal records · '+(d.included_usdt_record_count||0)+' USDT records counted';
 $('#pt-row-count').textContent=(d.recent||[]).length+' recent records shown';
 $('#pt-warning').textContent=!d.has_personal_records?'No personal trade ledger imported yet. Sync Binance Futures income history with a read-only key or upload a realised-PnL CSV. No public lead-trader PnL has been included.':(get('net_after_tax_reserve_usdt')<=0?'LOSS WARNING: economic PnL after the conservative tax reserve is non-positive. Review strategy performance, fees, funding and position sizing. ':'Imported-records result is positive after the reserve in this period, but this is not a guarantee. ')+(d.excluded_non_usdt_or_unconverted_count?' '+d.excluded_non_usdt_or_unconverted_count+' records use non-USDT assets or have no conversion and are excluded from USDT totals.':'')+' Tax estimate is provisional; futures classification must be reviewed.';
 const sr=d.by_strategy||[];$('#pt-strategy-rows').innerHTML=sr.length?sr.map(x=>'<tr><td><strong>'+esc(x.strategy_name)+'</strong></td><td>'+n(x.record_count,0)+'</td><td>'+itUsdt(x.positive_realized_pnl_usdt)+'</td><td class="negative">'+itUsdt(x.gross_loss_usdt)+'</td><td>'+itUsdt(x.commission_usdt)+'</td><td>'+itUsdt(x.funding_usdt)+'</td><td>'+itUsdt(x.tax_reserve_usdt)+'</td><td class="'+colorNum(x.economic_net_pnl_usdt)+'">'+itUsdt(x.economic_net_pnl_usdt)+'</td><td class="'+colorNum(x.net_after_tax_reserve_usdt)+'">'+itUsdt(x.net_after_tax_reserve_usdt)+'</td><td>'+esc(x.status)+'</td></tr>').join(''):'<tr><td colspan="10" class="empty-state">No imported personal trade records.</td></tr>';
 const recent=d.recent||[];$('#pt-ledger-rows').innerHTML=recent.length?recent.map(x=>'<tr><td>'+esc(x.time||'—')+'</td><td>'+esc(x.strategy_name||'—')+'</td><td>'+esc(x.market_type||'—')+'</td><td>'+esc(x.symbol||'—')+'</td><td>'+esc(x.income_type||'—')+'</td><td>'+esc(x.asset||'—')+' '+itMoney(x.amount_asset,6)+'</td><td class="'+colorNum(x.realized_pnl_usdt)+'">'+itUsdt(x.realized_pnl_usdt)+'</td><td>'+itUsdt(x.commission_usdt)+'</td><td>'+itUsdt(x.funding_usdt)+'</td><td>'+itUsdt(x.tax_reserve_usdt)+'</td><td class="'+colorNum(x.net_after_reserve_usdt)+'">'+itUsdt(x.net_after_reserve_usdt)+'</td></tr>').join(''):'<tr><td colspan="11" class="empty-state">No imported personal trade records. Connect a read-only key or import CSV.</td></tr>';
 itLoadStrategyWatch(d);
}
async function itLoadP2PRates(){
 try{const r=await api('/api/profit-tax/rates');$('#pt-buy-rate').value=r.buy_quote_inr_per_usdt||'';$('#pt-sell-rate').value=r.sell_quote_inr_per_usdt||'';$('#pt-rate-status').textContent=r.sell_quote_inr_per_usdt?'Binance P2P quote · '+String(r.as_of_utc||'').slice(0,19)+' UTC':'P2P quote unavailable · enter a rate manually';if(!$('#pt-rate').dataset.manual&&r.sell_quote_inr_per_usdt)$('#pt-rate').value=r.sell_quote_inr_per_usdt;$('#pt-rate-status').title=r.note||r.source||''}catch(e){$('#pt-rate-status').textContent='P2P source unavailable · enter rate manually'}
}
async function itLoadProfitTax(){
 try{const d=await api('/api/profit-tax/summary');itRenderTax(d)}catch(e){$('#pt-warning').textContent='Unable to load Profit & Tax Centre: '+e.message;$('#pt-ledger-status').textContent='Data load failed'}
}
async function itSyncBinance(){
 const key=$('#pt-api-key').value.trim(), secret=$('#pt-api-secret').value, days=Number($('#pt-days').value||30), label=$('#pt-strategy-sync').value.trim();
 if(!key||!secret){toast('Enter both API key and API secret for this one-time read-only request.','error');return}
 const b=$('#pt-sync');b.disabled=true;b.textContent='Requesting Binance records…';
 try{const d=await api('/api/profit-tax/sync',{method:'POST',body:JSON.stringify({api_key:key,api_secret:secret,lookback_days:days,strategy_name:label})});$('#pt-api-key').value='';$('#pt-api-secret').value='';$('#pt-api-secret').type='password';toast('Binance income records fetched: '+n(d.sync&&d.sync.fetched_supported_income_records,0)+'; new records saved: '+n(d.sync&&d.sync.new_records_saved,0)+'.','success');itRenderTax(d);await itLoadP2PRates()}catch(e){$('#pt-api-secret').value='';toast('Binance sync failed: '+e.message,'error')}finally{$('#pt-api-key').value='';$('#pt-api-secret').value='';b.disabled=false;b.textContent='Request Binance income history'}
}
async function itImportTaxCsv(){
 const file=$('#pt-csv').files&&$('#pt-csv').files[0];if(!file){toast('Choose a CSV file first.','error');return}
 const form=new FormData();form.append('file',file);form.append('market_type',$('#pt-market-csv').value);form.append('strategy_name',$('#pt-strategy-csv').value.trim());
 const b=$('#pt-import');b.disabled=true;b.textContent='Importing CSV…';
 try{const response=await fetch('/api/profit-tax/import',{method:'POST',body:form,credentials:'same-origin'});const d=await response.json();if(!response.ok||d.error)throw new Error(d.error||('HTTP '+response.status));toast('Recognised '+n(d.import&&d.import.recognised_records,0)+' records; saved '+n(d.import&&d.import.new_records_saved,0)+' new rows.','success');itRenderTax(d);$('#pt-csv').value=''}catch(e){toast('CSV import failed: '+e.message,'error')}finally{b.disabled=false;b.textContent='Import CSV records'}
}
function itRenderPortfolio(d){
 const rows=d.selected_portfolios||[];const cap=Math.max(0,Number($('#pl-capital').value||0));let used=0, pnl7=0,pnl30=0,pnl90=0,tax30=0;let known30=0;
 const table=rows.map(x=>{const weight=Math.max(0,Number(x.allocation_pct||0))/100;const amount=cap*weight;used+=amount;const r7=x.roi_7d==null?null:Number(x.roi_7d);const r30=x.roi_30d==null?null:Number(x.roi_30d);const r90=x.roi_90d==null?null:Number(x.roi_90d);const p7=r7==null?null:amount*r7/100;const p30=r30==null?null:amount*r30/100;const p90=r90==null?null:amount*r90/100;if(p7!=null)pnl7+=p7;if(p30!=null){pnl30+=p30;known30+=1;tax30+=Math.max(0,p30)*0.3}if(p90!=null)pnl90+=p90;return '<tr><td><strong>'+esc(x.nickname||x.portfolio_id)+'</strong><small style="display:block;color:#8c98a8">'+esc(x.portfolio_id||'')+'</small></td><td>'+n(x.trader_duration_days,1)+'</td><td class="'+colorNum(x.copier_pnl)+'">'+itUsdt(x.copier_pnl)+'</td><td>'+n(x.score,1)+'</td><td>'+n(x.allocation_pct,1,'%')+'</td><td>'+itUsdt(amount)+'</td><td>'+n(r7,2,'%')+'</td><td>'+n(r30,2,'%')+'</td><td>'+n(r90,2,'%')+'</td><td class="'+colorNum(p30)+'">'+itUsdt(p30)+'</td><td>'+itUsdt(Math.max(0,p30||0)*0.3)+'</td><td style="white-space:normal">'+esc(x.selection_reason||'Selected by screen')+'</td></tr>'}).join('');
 $('#pl-count').textContent=String(rows.length);$('#pl-used').textContent=itUsdt(used)+' / '+itUsdt(cap);$('#pl-30d').textContent=known30?itUsdt(pnl30):'N/A';$('#pl-after-tax').textContent=known30?itUsdt(pnl30-tax30):'N/A';$('#pl-asof').textContent='As of '+String(d.evaluated_at_utc||'').slice(0,19)+' UTC';
 $('#pl-rows').innerHTML=rows.length?table:'<tr><td colspan="12" class="empty-state">No portfolio passed all data, duration, copier-PnL and risk filters. Do not weaken filters just to force a result.</td></tr>';
 $('#pl-alert').textContent=!rows.length?'No eligible portfolio is supported by the current stored evidence. Run discovery and keep screening until sufficient history and positive copier PnL are available.':'Historical scaling is illustrative only: 7D PnL '+itUsdt(pnl7)+', 30D '+itUsdt(pnl30)+', 90D '+itUsdt(pnl90)+'. Positive 30D strategy gains have a '+itUsdt(tax30)+' reserve in this scenario; negative strategy results do not reduce the reserve. This is not an account-level forecast or guarantee.';
}
async function itLoadPortfolioLab(){
 try{const market=$('#pl-market').value;const params=new URLSearchParams({market_type:market,max_selected:$('#pl-max').value,min_closed_trades:$('#pl-min-trades').value,min_profit_factor:'1.2',max_mdd_pct:'20',min_roi_7d:'-5'});const d=await api('/api/multi-trader/candidates?'+params.toString());itRenderPortfolio(d)}catch(e){$('#pl-alert').textContent='Portfolio Lab could not load its stored-data analysis: '+e.message}
}
function itEnsureTradeBehaviourSlot(){
 const root=$('#view-history');if(root&&!$('#tb-data-workflow'))root.insertAdjacentHTML('afterbegin','<div id="tb-data-workflow"><div class="eyebrow">STORED CLOSED-POSITION ANALYSIS</div><div class="kpi-grid"><article class="kpi-card"><div class="kpi-head"><span>Closed positions</span></div><div class="kpi-value" id="tb-closed">—</div><div class="kpi-foot">Stored lead-trader records</div></article><article class="kpi-card"><div class="kpi-head"><span>Win rate</span></div><div class="kpi-value" id="tb-winrate">—</div><div class="kpi-foot">Calculated from stored outcomes</div></article><article class="kpi-card"><div class="kpi-head"><span>Recorded net PnL</span></div><div class="kpi-value" id="tb-net">—</div><div class="kpi-foot">Not copier account PnL</div></article><article class="kpi-card"><div class="kpi-head"><span>Trade-path coverage</span></div><div class="kpi-value" id="tb-coverage">—</div><div class="kpi-foot">MAE/MFE fields available</div></article></div><article class="panel"><div class="panel-header"><div><div class="eyebrow">MARKET COVERAGE</div><h3>Outcome and trade-path summary</h3></div><span class="tag gray" id="tb-asof">Loading</span></div><div class="table-scroll"><table><thead><tr><th>Market</th><th>Closed records</th><th>Win rate</th><th>Profit factor</th><th>Gross profit</th><th>Gross loss</th><th>Net PnL</th><th>Avg MAE</th><th>Avg MFE</th><th>Adverse first</th><th>Path coverage</th></tr></thead><tbody id="tb-market-rows"><tr><td colspan="11" class="empty-state">Loading stored metrics…</td></tr></tbody></table></div></article><article class="panel table-panel"><div class="panel-header"><div><div class="eyebrow">PER-PORTFOLIO BEHAVIOUR</div><h3>Best and weakest stored closed-trade outcomes</h3></div><span class="tag gray">Top 100 profiles by stored net PnL</span></div><div class="table-scroll"><table><thead><tr><th>Portfolio</th><th>Market</th><th>Closed records</th><th>Win rate</th><th>PF</th><th>Copier PnL</th><th>Trader ROI</th><th>Drawdown</th><th>Net stored PnL</th><th>Avg MAE</th><th>Avg MFE</th><th>Adverse first</th><th>Path coverage</th><th>Profile</th></tr></thead><tbody id="tb-trader-rows"><tr><td colspan="14" class="empty-state">Loading portfolio behaviour…</td></tr></tbody></table></div></article><article class="panel table-panel"><div class="panel-header"><div><div class="eyebrow">RECENT CLOSED POSITIONS</div><h3>Entry, exit and adverse/favourable excursion</h3></div><span class="tag gray" id="tb-trade-count">0 records</span></div><div class="table-scroll"><table><thead><tr><th>Opened (UTC)</th><th>Closed (UTC)</th><th>Duration (min)</th><th>Portfolio</th><th>Market</th><th>Symbol</th><th>Side</th><th>Leverage</th><th>Entry</th><th>Exit</th><th>Realised PnL</th><th>ROI</th><th>MAE</th><th>MFE</th><th>Adverse first</th><th>Path status</th><th>Coverage</th></tr></thead><tbody id="tb-recent-rows"><tr><td colspan="17" class="empty-state">Loading recent positions…</td></tr></tbody></table></div></article><div class="notice-box">This is stored public lead-trader research history. It may not contain every trade, account fees, funding, or your copier's fills. It is not your personal tax ledger.</div></div>');
}
async function itLoadTradeBehaviour(){
 itEnsureTradeBehaviourSlot();
 try{const d=await api('/api/trade-behaviour/summary');const markets=d.markets||[],traders=d.traders||[],trades=d.recent_closed_positions||[];const total=markets.reduce((a,x)=>a+Number(x.closed_trades||0),0);const wins=markets.reduce((a,x)=>a+Number(x.wins||0),0),losses=markets.reduce((a,x)=>a+Number(x.losses||0),0);const net=markets.reduce((a,x)=>a+Number(x.net_pnl||0),0);const cov=total?100*markets.reduce((a,x)=>a+Number(x.path_records||0),0)/total:0;
 $('#tb-closed').textContent=n(total,0);$('#tb-winrate').textContent=(wins+losses)?n(100*wins/(wins+losses),2,'%'):'—';$('#tb-net').textContent=itUsdt(net);$('#tb-coverage').textContent=n(cov,1,'%');$('#tb-asof').textContent='As of '+String(d.generated_at_utc||'').slice(0,19)+' UTC';
 $('#tb-market-rows').innerHTML=markets.length?markets.map(x=>'<tr><td>'+esc(x.market_type)+'</td><td>'+n(x.closed_trades,0)+'</td><td>'+n(x.win_rate_pct,2,'%')+'</td><td>'+n(x.profit_factor,3)+'</td><td>'+itUsdt(x.gross_profit)+'</td><td>'+itUsdt(x.gross_loss)+'</td><td class="'+colorNum(x.net_pnl)+'">'+itUsdt(x.net_pnl)+'</td><td>'+n(x.avg_mae_pct,3,'%')+'</td><td>'+n(x.avg_mfe_pct,3,'%')+'</td><td>'+n(x.adverse_first_pct,1,'%')+'</td><td>'+n(x.path_coverage_pct,1,'%')+'</td></tr>').join(''):'<tr><td colspan="11" class="empty-state">No closed positions have been stored for these markets yet.</td></tr>';
 $('#tb-trader-rows').innerHTML=traders.length?traders.map(x=>'<tr><td><strong>'+esc(x.nickname||x.portfolio_id)+'</strong><small style="display:block;color:#8c98a8">'+esc(x.portfolio_id||'')+'</small></td><td>'+esc(x.market_type)+'</td><td>'+n(x.closed_trades,0)+'</td><td>'+n(x.win_rate_pct,2,'%')+'</td><td>'+n(x.profit_factor,3)+'</td><td class="'+colorNum(x.copier_pnl)+'">'+itUsdt(x.copier_pnl)+'</td><td>'+n(x.roi,2,'%')+'</td><td>'+n(x.mdd,2,'%')+'</td><td class="'+colorNum(x.net_pnl)+'">'+itUsdt(x.net_pnl)+'</td><td>'+n(x.avg_mae_pct,3,'%')+'</td><td>'+n(x.avg_mfe_pct,3,'%')+'</td><td>'+n(x.adverse_first_pct,1,'%')+'</td><td>'+n(x.path_coverage_pct,1,'%')+'</td><td>'+(x.profile_url?'<a href="'+esc(x.profile_url)+'" target="_blank" rel="noopener">Open</a>':'—')+'</td></tr>').join(''):'<tr><td colspan="14" class="empty-state">No per-portfolio closed-position records stored.</td></tr>';
 $('#tb-trade-count').textContent=trades.length+' recent positions';$('#tb-recent-rows').innerHTML=trades.length?trades.map(x=>'<tr><td>'+esc(x.opened_ms?new Date(Number(x.opened_ms)).toISOString().replace('T',' ').slice(0,19):'—')+'</td><td>'+esc(x.closed_ms?new Date(Number(x.closed_ms)).toISOString().replace('T',' ').slice(0,19):'—')+'</td><td>'+n(x.opened_ms&&x.closed_ms?(Number(x.closed_ms)-Number(x.opened_ms))/60000:null,1)+'</td><td>'+esc(x.nickname||x.trader_id)+'</td><td>'+esc(x.market_type)+'</td><td>'+esc(x.symbol||'—')+'</td><td>'+esc(x.side||'—')+'</td><td>'+n(x.leverage,1)+'×</td><td>'+n(x.entry_price,6)+'</td><td>'+n(x.exit_price,6)+'</td><td class="'+colorNum(x.close_pnl)+'">'+itUsdt(x.close_pnl)+'</td><td>'+n(x.roi_pct,2,'%')+'</td><td>'+n(x.mae_pct,3,'%')+'</td><td>'+n(x.mfe_pct,3,'%')+'</td><td>'+esc(x.went_adverse_first===true?'Yes':x.went_adverse_first===false?'No':'Unknown')+'</td><td>'+esc(x.path_status||'Not analysed')+'</td><td>'+n(x.coverage_pct,1,'%')+'</td></tr>').join(''):'<tr><td colspan="17" class="empty-state">No recent closed positions stored.</td></tr>';
 }catch(e){$('#tb-asof').textContent='Data request failed';$('#tb-market-rows').innerHTML='<tr><td colspan="11" class="empty-state">'+esc(e.message)+'</td></tr>'}
}
function itBindWorkflowControls(){
 if($('#pt-sync'))$('#pt-sync').addEventListener('click',itSyncBinance);
 if($('#pt-import'))$('#pt-import').addEventListener('click',itImportTaxCsv);
 if($('#pt-refresh-rate'))$('#pt-refresh-rate').addEventListener('click',itLoadP2PRates);
 if($('#pt-rate'))$('#pt-rate').addEventListener('input',()=>{$('#pt-rate').dataset.manual='1';itLoadProfitTax()});
 if($('#pl-run'))$('#pl-run').addEventListener('click',itLoadPortfolioLab);
 if($('#pl-refresh'))$('#pl-refresh').addEventListener('click',itLoadPortfolioLab);
 if($('#pl-market'))$('#pl-market').addEventListener('change',itLoadPortfolioLab);
}
itBindWorkflowControls();
'''
# Insert helpers in the existing bundled JS after the Multi-Trader patch has created the file and before the System loader.
insert_once(js, 'async function loadSystem(){', js_code + '\n', 'function itLoadTradeBehaviour()', "workflow client logic")

s = js.read_text()
old_route = "const titles={overview:'Overview',traders:'Trader universe','multi-trader':'Multi-Trader Mode',history:'Trade behaviour',reports:'Reports & exports',data:'Data import',system:'Source & system'};$('#page-title').textContent=titles[name]||name;if(name==='traders')loadTraders();if(name==='multi-trader')loadMultiTrader(false);if(name==='history')loadPaths();if(name==='system')loadSystem();"
new_route = "const titles={overview:'Overview',traders:'Trader universe','multi-trader':'Multi-Trader Mode','portfolio-lab':'Portfolio Lab','profit-tax':'Profit & Tax Centre','strategy-watch':'Strategy Tax Watch',history:'Trade behaviour',reports:'Reports & exports',data:'Data import',system:'Source & system'};$('#page-title').textContent=titles[name]||name;if(name==='traders')loadTraders();if(name==='multi-trader')loadMultiTrader(false);if(name==='portfolio-lab')itLoadPortfolioLab();if(name==='profit-tax'){itLoadP2PRates();itLoadProfitTax()}if(name==='strategy-watch')itLoadProfitTax();if(name==='history'){loadPaths();itLoadTradeBehaviour()}if(name==='system')loadSystem();"
if old_route in s:
    s = s.replace(old_route,new_route,1)
else:
    # Safe fallback when the previous patch altered whitespace/ordering.
    pattern = r"const titles=\{overview:'Overview'.*?if\(name==='system'\)loadSystem\(\);"
    s2, count = re.subn(pattern,new_route,s,count=1)
    if count != 1: raise RuntimeError("Could not wire the new workflow routes")
    s = s2
timer_old = "state.refreshTimer=setInterval(()=>{refreshStatus();loadRunsOnly();if(state.view==='multi-trader')loadMultiTrader(false);if(state.view==='traders')loadTraders();if(state.view==='history')loadPaths();},30000)"
timer_new = "state.refreshTimer=setInterval(()=>{refreshStatus();loadRunsOnly()},30000)"
if timer_old in s:
    s = s.replace(timer_old,timer_new,1)
js.write_text(s)
print("Intel workflow pages and data-backed endpoints installed")
