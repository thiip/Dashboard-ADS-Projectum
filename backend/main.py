"""
Projectum Ads Dashboard — Backend API
Modo DEMO | Modo Supabase | Modo Meta API
"""
from fastapi import FastAPI, Query
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from datetime import datetime, timedelta
import random
import math
import os
import time
from pathlib import Path

try:
    import requests as http_requests
except ImportError:
    http_requests = None

try:
    from supabase import create_client, Client as SupabaseClient
    from supabase.lib.client_options import ClientOptions
except ImportError:
    SupabaseClient = None
    create_client = None
    ClientOptions = None

from dotenv import load_dotenv

load_dotenv()

app = FastAPI(title="Projectum Ads Dashboard", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# Serve frontend
FRONTEND_DIR = Path(__file__).parent.parent / "frontend"
if FRONTEND_DIR.exists():
    app.mount("/static", StaticFiles(directory=str(FRONTEND_DIR)), name="frontend")

META_TOKEN = os.getenv("META_ACCESS_TOKEN", "")
ACCOUNT_ID = os.getenv("META_ACCOUNT_ID", "1917726750804")
SUPABASE_URL = os.getenv("SUPABASE_URL", "")
SUPABASE_KEY = os.getenv("SUPABASE_KEY", "")
SUPABASE_SCHEMA = os.getenv("SUPABASE_SCHEMA", "ads_meta")

# Data source priority: Supabase > Meta API > Demo
supabase: SupabaseClient = None
if SUPABASE_URL and SUPABASE_KEY and create_client:
    try:
        opts = ClientOptions(schema=SUPABASE_SCHEMA) if ClientOptions else None
        supabase = create_client(SUPABASE_URL, SUPABASE_KEY, options=opts) if opts else create_client(SUPABASE_URL, SUPABASE_KEY)
    except Exception:
        supabase = None

USE_SUPABASE = supabase is not None
USE_META_API = not USE_SUPABASE and bool(META_TOKEN)
USE_DEMO = not USE_SUPABASE and not USE_META_API

# =====================================================
# DEMO DATA — Estrutura real das campanhas Projectum
# =====================================================

DEMO_CAMPAIGNS = [
    {
        "id": "6918443271116",
        "name": "[TOPO] Reconhecimento - Projectum Natal 2026",
        "status": "ACTIVE",
        "funnel": "TOPO",
        "funnel_color": "#3B82F6",
        "objective": "OUTCOME_AWARENESS",
        "daily_budget": 13.00,
        "impressions": 18420,
        "clicks": 312,
        "spend": 285.40,
        "ctr": 1.69,
        "cpm": 15.49,
        "cpc": 0.91,
        "reach": 11850,
        "frequency": 1.55,
        "leads": 0,
    },
    {
        "id": "6918443936116",
        "name": "[MEIO] Consideração - Projectum Natal 2026",
        "status": "ACTIVE",
        "funnel": "MEIO",
        "funnel_color": "#8B5CF6",
        "objective": "OUTCOME_TRAFFIC",
        "daily_budget": 30.00,
        "impressions": 52340,
        "clicks": 1259,
        "spend": 658.20,
        "ctr": 2.41,
        "cpm": 12.58,
        "cpc": 0.73,
        "reach": 28400,
        "frequency": 1.84,
        "leads": 0,
    },
    {
        "id": "6918443949116",
        "name": "[FUNDO] Conversão - Projectum Natal 2026",
        "status": "ACTIVE",
        "funnel": "FUNDO",
        "funnel_color": "#10B981",
        "objective": "OUTCOME_LEADS",
        "daily_budget": 23.00,
        "impressions": 9870,
        "clicks": 245,
        "spend": 504.60,
        "ctr": 0.88,
        "cpm": 51.13,
        "cpc": 2.06,
        "reach": 6320,
        "frequency": 1.56,
        "leads": 3,
    },
]

DEMO_ADS = [
    # TOPO ads
    {
        "id": "6930266155300",
        "name": "[TOPO] Ad1 - Vídeo Portfólio",
        "status": "PAUSED",
        "campaign_id": "6918443271116",
        "campaign_name": "[TOPO] Reconhecimento - Projectum Natal 2026",
        "funnel": "TOPO",
        "funnel_color": "#3B82F6",
        "impressions": 8240,
        "clicks": 156,
        "spend": 132.50,
        "ctr": 1.89,
        "cpm": 16.08,
        "cpc": 0.85,
        "reach": 5620,
        "frequency": 1.47,
        "leads": 0,
    },
    {
        "id": "6930266155400",
        "name": "[TOPO] Ad2 - Carrossel Projetos",
        "status": "ACTIVE",
        "campaign_id": "6918443271116",
        "campaign_name": "[TOPO] Reconhecimento - Projectum Natal 2026",
        "funnel": "TOPO",
        "funnel_color": "#3B82F6",
        "impressions": 6580,
        "clicks": 98,
        "spend": 94.20,
        "ctr": 1.49,
        "cpm": 14.32,
        "cpc": 0.96,
        "reach": 4180,
        "frequency": 1.57,
        "leads": 0,
    },
    {
        "id": "6930266155716",
        "name": "[TOPO] Ad3 - Impacto Visual",
        "status": "ACTIVE",
        "campaign_id": "6918443271116",
        "campaign_name": "[TOPO] Reconhecimento - Projectum Natal 2026",
        "funnel": "TOPO",
        "funnel_color": "#3B82F6",
        "impressions": 3600,
        "clicks": 58,
        "spend": 58.70,
        "ctr": 1.61,
        "cpm": 16.31,
        "cpc": 1.01,
        "reach": 2050,
        "frequency": 1.76,
        "leads": 0,
    },
    # MEIO ads
    {
        "id": "6930266156100",
        "name": "[MEIO] Ad3 - Case de Sucesso",
        "status": "ACTIVE",
        "campaign_id": "6918443936116",
        "campaign_name": "[MEIO] Consideração - Projectum Natal 2026",
        "funnel": "MEIO",
        "funnel_color": "#8B5CF6",
        "impressions": 5820,
        "clicks": 140,
        "spend": 78.40,
        "ctr": 2.41,
        "cpm": 13.47,
        "cpc": 0.56,
        "reach": 3950,
        "frequency": 1.47,
        "leads": 0,
    },
    {
        "id": "6930266156200",
        "name": "[MEIO] Ad4 - Storytelling Resiliência",
        "status": "ACTIVE",
        "campaign_id": "6918443936116",
        "campaign_name": "[MEIO] Consideração - Projectum Natal 2026",
        "funnel": "MEIO",
        "funnel_color": "#8B5CF6",
        "impressions": 40120,
        "clicks": 967,
        "spend": 498.60,
        "ctr": 2.41,
        "cpm": 12.43,
        "cpc": 0.52,
        "reach": 21200,
        "frequency": 1.89,
        "leads": 0,
    },
    {
        "id": "6930266156300",
        "name": "[MEIO] Ad5 - Diferencial Externo + Shopping",
        "status": "ACTIVE",
        "campaign_id": "6918443936116",
        "campaign_name": "[MEIO] Consideração - Projectum Natal 2026",
        "funnel": "MEIO",
        "funnel_color": "#8B5CF6",
        "impressions": 6400,
        "clicks": 152,
        "spend": 81.20,
        "ctr": 2.38,
        "cpm": 12.69,
        "cpc": 0.53,
        "reach": 3250,
        "frequency": 1.97,
        "leads": 0,
    },
    # FUNDO ads
    {
        "id": "6930266156600",
        "name": "[FUNDO] Ad6 - Lead Form Direto",
        "status": "ACTIVE",
        "campaign_id": "6918443949116",
        "campaign_name": "[FUNDO] Conversão - Projectum Natal 2026",
        "funnel": "FUNDO",
        "funnel_color": "#10B981",
        "impressions": 3120,
        "clicks": 82,
        "spend": 168.40,
        "ctr": 0.92,
        "cpm": 53.97,
        "cpc": 2.05,
        "reach": 2100,
        "frequency": 1.49,
        "leads": 1,
    },
    {
        "id": "6930266156700",
        "name": "[FUNDO] Ad7 - WhatsApp Direct",
        "status": "ACTIVE",
        "campaign_id": "6918443949116",
        "campaign_name": "[FUNDO] Conversão - Projectum Natal 2026",
        "funnel": "FUNDO",
        "funnel_color": "#10B981",
        "impressions": 3450,
        "clicks": 88,
        "spend": 172.80,
        "ctr": 0.84,
        "cpm": 50.09,
        "cpc": 1.96,
        "reach": 2180,
        "frequency": 1.58,
        "leads": 1,
    },
    {
        "id": "6930266156800",
        "name": "[FUNDO] Ad8 - Urgência Agenda Limitada",
        "status": "ACTIVE",
        "campaign_id": "6918443949116",
        "campaign_name": "[FUNDO] Conversão - Projectum Natal 2026",
        "funnel": "FUNDO",
        "funnel_color": "#10B981",
        "impressions": 3300,
        "clicks": 75,
        "spend": 163.40,
        "ctr": 0.87,
        "cpm": 49.52,
        "cpc": 2.18,
        "reach": 2040,
        "frequency": 1.62,
        "leads": 1,
    },
]


def generate_daily_demo(days: int):
    """Gera série temporal diária realista."""
    rows = []
    base_date = datetime.now() - timedelta(days=days)
    random.seed(42)  # reproducible
    for i in range(days):
        dt = base_date + timedelta(days=i)
        date_str = dt.strftime("%Y-%m-%d")
        # Budget total ~R$66/dia com variação
        day_of_week = dt.weekday()
        # Weekends get slightly more spend on awareness
        weekend_factor = 1.12 if day_of_week >= 5 else 1.0
        base_spend = 66 * weekend_factor
        spend = round(base_spend * (0.85 + random.random() * 0.30), 2)
        impressions = int(spend / 0.015 * (0.8 + random.random() * 0.4))
        clicks = int(impressions * (0.015 + random.random() * 0.012))
        ctr = round(clicks / max(impressions, 1) * 100, 2)
        cpm = round(spend / max(impressions, 1) * 1000, 2)
        reach = int(impressions * (0.6 + random.random() * 0.2))
        rows.append({
            "date_start": date_str,
            "date_stop": date_str,
            "impressions": str(impressions),
            "clicks": str(clicks),
            "spend": str(spend),
            "ctr": str(ctr),
            "cpm": str(cpm),
            "reach": str(reach),
        })
    return rows


def generate_monthly_demo():
    """Gera dados mensais dos últimos 12 meses por campanha."""
    months = []
    now = datetime.now()
    random.seed(123)

    # Campanhas começaram em dez/2025 (planejamento natal 2026)
    start_month = datetime(2025, 12, 1)

    for i in range(12):
        dt = datetime(now.year, now.month, 1) - timedelta(days=30 * (11 - i))
        month_dt = datetime(dt.year, dt.month, 1)
        if month_dt < start_month:
            continue

        month_label = month_dt.strftime("%Y-%m")
        month_name = month_dt.strftime("%b/%Y")
        days_in_month = 30

        # Ramp up: primeiros meses gastam menos, depois estabiliza
        months_running = (month_dt.year - start_month.year) * 12 + month_dt.month - start_month.month
        ramp = min(1.0, 0.4 + months_running * 0.15)

        for camp in [
            {"funnel": "TOPO", "name": "[TOPO] Reconhecimento", "budget": 13, "color": "#3B82F6"},
            {"funnel": "MEIO", "name": "[MEIO] Consideração", "budget": 30, "color": "#8B5CF6"},
            {"funnel": "FUNDO", "name": "[FUNDO] Conversão", "budget": 23, "color": "#10B981"},
        ]:
            base = camp["budget"] * days_in_month * ramp
            spend = round(base * (0.88 + random.random() * 0.24), 2)
            impressions = int(spend / 0.016 * (0.85 + random.random() * 0.3))
            clicks = int(impressions * (0.012 + random.random() * 0.015))
            leads = 0
            if camp["funnel"] == "FUNDO" and months_running >= 2:
                leads = int(random.random() * 4) + 1
            ctr = round(clicks / max(impressions, 1) * 100, 2)
            cpm = round(spend / max(impressions, 1) * 1000, 2)

            months.append({
                "month": month_label,
                "month_name": month_name,
                "funnel": camp["funnel"],
                "campaign_name": camp["name"],
                "color": camp["color"],
                "spend": spend,
                "impressions": impressions,
                "clicks": clicks,
                "ctr": ctr,
                "cpm": cpm,
                "leads": leads,
                "budget_dia": camp["budget"],
            })

    return months


# =====================================================
# META API (modo live)
# =====================================================
API_VERSION = "v21.0"
BASE_URL = f"https://graph.facebook.com/{API_VERSION}"
_cache: dict = {}
CACHE_TTL = 300

FUNNEL_ORDER = {"TOPO": 0, "MEIO": 1, "FUNDO": 2, "OUTRO": 99}
FUNNEL_COLOR = {"TOPO": "#3B82F6", "MEIO": "#8B5CF6", "FUNDO": "#10B981", "OUTRO": "#6B7280"}
INSIGHT_FIELDS = "impressions,clicks,spend,ctr,cpm,cpc,reach,frequency,actions"


def cache_get(key):
    if key in _cache:
        data, ts = _cache[key]
        if time.time() - ts < CACHE_TTL:
            return data
    return None


def cache_set(key, data):
    _cache[key] = (data, time.time())


def meta_get(path, params=None):
    if params is None:
        params = {}
    params["access_token"] = META_TOKEN
    cache_key = f"{path}:{str(sorted(params.items()))}"
    cached = cache_get(cache_key)
    if cached is not None:
        return cached
    resp = http_requests.get(f"{BASE_URL}{path}", params=params, timeout=30)
    resp.raise_for_status()
    data = resp.json()
    cache_set(cache_key, data)
    return data


def get_date_range(days):
    end = datetime.now().strftime("%Y-%m-%d")
    start = (datetime.now() - timedelta(days=days)).strftime("%Y-%m-%d")
    return start, end


def extract_action(actions, action_type):
    if not actions:
        return 0
    for a in actions:
        if a.get("action_type") == action_type:
            return int(float(a.get("value", 0)))
    return 0


def funnel_from_name(name):
    if "[TOPO]" in name:
        return "TOPO"
    elif "[MEIO]" in name:
        return "MEIO"
    elif "[FUNDO]" in name:
        return "FUNDO"
    return "OUTRO"


def parse_insights(ins):
    return {
        "impressions": int(ins.get("impressions", 0)),
        "clicks": int(ins.get("clicks", 0)),
        "spend": float(ins.get("spend", 0)),
        "ctr": float(ins.get("ctr", 0)),
        "cpm": float(ins.get("cpm", 0)),
        "cpc": float(ins.get("cpc", 0)),
        "reach": int(ins.get("reach", 0)),
        "frequency": float(ins.get("frequency", 0)),
        "leads": extract_action(ins.get("actions"), "lead"),
    }


# =====================================================
# ENDPOINTS
# =====================================================

@app.get("/")
async def serve_index():
    index = FRONTEND_DIR / "index.html"
    if index.exists():
        return FileResponse(str(index))
    return {"message": "Frontend not found. Access API at /docs"}


@app.get("/health")
async def health():
    mode = "supabase" if USE_SUPABASE else ("api" if USE_META_API else "demo")
    return {
        "status": "ok",
        "mode": mode,
        "account_id": ACCOUNT_ID,
        "token_configured": bool(META_TOKEN),
        "supabase_configured": USE_SUPABASE,
    }


@app.get("/api/summary")
async def get_summary(days: int = Query(30, ge=1, le=365)):
    if USE_SUPABASE:
        start, end = get_date_range(days)
        resp = supabase.table("daily_metrics").select("*").gte("date", start).lte("date", end).execute()
        rows = resp.data or []
        total = {
            "impressions": sum(r["impressions"] for r in rows),
            "clicks": sum(r["clicks"] for r in rows),
            "spend": round(sum(float(r["spend"]) for r in rows), 2),
            "reach": sum(r["reach"] for r in rows),
        }
        # Get leads from campaign metrics
        resp2 = supabase.table("campaign_daily_metrics").select("leads").gte("date", start).lte("date", end).execute()
        total["leads"] = sum(r["leads"] for r in (resp2.data or []))
        total["ctr"] = round(total["clicks"] / max(total["impressions"], 1) * 100, 2)
        total["cpm"] = round(total["spend"] / max(total["impressions"], 1) * 1000, 2)
        total["cpc"] = round(total["spend"] / max(total["clicks"], 1), 2)
        total["frequency"] = round(total["impressions"] / max(total["reach"], 1), 2)
        total["days"] = days
        total["date_start"] = start
        total["date_end"] = end
        total["mode"] = "supabase"
        return total

    if USE_DEMO:
        total = {
            "impressions": sum(c["impressions"] for c in DEMO_CAMPAIGNS),
            "clicks": sum(c["clicks"] for c in DEMO_CAMPAIGNS),
            "spend": round(sum(c["spend"] for c in DEMO_CAMPAIGNS), 2),
            "reach": sum(c["reach"] for c in DEMO_CAMPAIGNS),
            "leads": sum(c["leads"] for c in DEMO_CAMPAIGNS),
        }
        total["ctr"] = round(total["clicks"] / max(total["impressions"], 1) * 100, 2)
        total["cpm"] = round(total["spend"] / max(total["impressions"], 1) * 1000, 2)
        total["cpc"] = round(total["spend"] / max(total["clicks"], 1), 2)
        total["frequency"] = round(total["impressions"] / max(total["reach"], 1), 2)
        total["days"] = days
        start, end = get_date_range(days)
        total["date_start"] = start
        total["date_end"] = end
        total["mode"] = "demo"
        return total

    start, end = get_date_range(days)
    data = meta_get(f"/act_{ACCOUNT_ID}/insights", {
        "fields": INSIGHT_FIELDS,
        "time_range": f'{{"since":"{start}","until":"{end}"}}',
        "level": "account",
    })
    rows = data.get("data", [])
    if not rows:
        return {**parse_insights({}), "days": days, "date_start": start, "date_end": end, "mode": "api"}
    result = parse_insights(rows[0])
    result.update({"days": days, "date_start": start, "date_end": end, "mode": "api"})
    return result


@app.get("/api/campaigns")
async def get_campaigns(days: int = Query(30, ge=1, le=365)):
    if USE_SUPABASE:
        start, end = get_date_range(days)
        # Get campaigns
        camps = supabase.table("campaigns").select("*").execute().data or []
        result = []
        for c in camps:
            # Get metrics for this campaign in the period
            metrics = supabase.table("campaign_daily_metrics").select("*").eq("campaign_id", c["id"]).gte("date", start).lte("date", end).execute().data or []
            impressions = sum(r["impressions"] for r in metrics)
            clicks = sum(r["clicks"] for r in metrics)
            spend = round(sum(float(r["spend"]) for r in metrics), 2)
            reach = sum(r["reach"] for r in metrics)
            leads = sum(r["leads"] for r in metrics)
            result.append({
                "id": c["id"], "name": c["name"],
                "status": c["status"], "funnel": c["funnel"],
                "funnel_color": c["funnel_color"],
                "objective": c.get("objective", ""),
                "daily_budget": float(c.get("daily_budget", 0)),
                "impressions": impressions, "clicks": clicks, "spend": spend,
                "ctr": round(clicks / max(impressions, 1) * 100, 2),
                "cpm": round(spend / max(impressions, 1) * 1000, 2),
                "cpc": round(spend / max(clicks, 1), 2),
                "reach": reach,
                "frequency": round(impressions / max(reach, 1), 2),
                "leads": leads,
            })
        result.sort(key=lambda x: FUNNEL_ORDER.get(x["funnel"], 99))
        return result

    if USE_DEMO:
        return DEMO_CAMPAIGNS

    start, end = get_date_range(days)
    camps_data = meta_get(f"/act_{ACCOUNT_ID}/campaigns", {
        "fields": "id,name,status,effective_status,daily_budget,objective",
        "limit": 50,
    })
    result = []
    for camp in camps_data.get("data", []):
        name = camp.get("name", "")
        if "Projectum" not in name:
            continue
        ins_data = meta_get(f"/{camp['id']}/insights", {
            "fields": INSIGHT_FIELDS,
            "time_range": f'{{"since":"{start}","until":"{end}"}}',
        })
        raw = ins_data.get("data", [{}])
        ins = raw[0] if raw else {}
        funnel = funnel_from_name(name)
        db = camp.get("daily_budget")
        result.append({
            "id": camp["id"], "name": name,
            "status": camp.get("effective_status", camp.get("status", "")),
            "funnel": funnel, "funnel_color": FUNNEL_COLOR[funnel],
            "objective": camp.get("objective", ""),
            "daily_budget": float(db) / 100 if db else 0,
            **parse_insights(ins),
        })
    result.sort(key=lambda x: FUNNEL_ORDER.get(x["funnel"], 99))
    return result


@app.get("/api/ads")
async def get_ads(days: int = Query(30, ge=1, le=365)):
    if USE_SUPABASE:
        start, end = get_date_range(days)
        ads_list = supabase.table("ads").select("*, campaigns(name)").execute().data or []
        result = []
        for a in ads_list:
            metrics = supabase.table("ad_daily_metrics").select("*").eq("ad_id", a["id"]).gte("date", start).lte("date", end).execute().data or []
            impressions = sum(r["impressions"] for r in metrics)
            clicks = sum(r["clicks"] for r in metrics)
            spend = round(sum(float(r["spend"]) for r in metrics), 2)
            reach = sum(r["reach"] for r in metrics)
            leads = sum(r["leads"] for r in metrics)
            cn = a.get("campaigns", {}).get("name", "") if a.get("campaigns") else ""
            result.append({
                "id": a["id"], "name": a["name"],
                "status": a["status"],
                "campaign_id": a["campaign_id"], "campaign_name": cn,
                "funnel": a["funnel"], "funnel_color": a["funnel_color"],
                "impressions": impressions, "clicks": clicks, "spend": spend,
                "ctr": round(clicks / max(impressions, 1) * 100, 2),
                "cpm": round(spend / max(impressions, 1) * 1000, 2),
                "cpc": round(spend / max(clicks, 1), 2),
                "reach": reach, "leads": leads,
            })
        result.sort(key=lambda x: (FUNNEL_ORDER.get(x["funnel"], 99), -x["spend"]))
        return result

    if USE_DEMO:
        return DEMO_ADS

    start, end = get_date_range(days)
    ads_data = meta_get(f"/act_{ACCOUNT_ID}/ads", {
        "fields": "id,name,status,effective_status,campaign_id,campaign{name}",
        "limit": 100,
    })
    result = []
    for ad in ads_data.get("data", []):
        cn = ad.get("campaign", {}).get("name", "")
        if "Projectum" not in cn:
            continue
        ins_data = meta_get(f"/{ad['id']}/insights", {
            "fields": INSIGHT_FIELDS,
            "time_range": f'{{"since":"{start}","until":"{end}"}}',
        })
        raw = ins_data.get("data", [{}])
        ins = raw[0] if raw else {}
        funnel = funnel_from_name(cn)
        result.append({
            "id": ad["id"], "name": ad["name"],
            "status": ad.get("effective_status", ad.get("status", "")),
            "campaign_id": ad.get("campaign_id", ""), "campaign_name": cn,
            "funnel": funnel, "funnel_color": FUNNEL_COLOR[funnel],
            **parse_insights(ins),
        })
    result.sort(key=lambda x: (FUNNEL_ORDER.get(x["funnel"], 99), -x["spend"]))
    return result


@app.get("/api/daily")
async def get_daily(days: int = Query(30, ge=7, le=365)):
    if USE_SUPABASE:
        start, end = get_date_range(days)
        resp = supabase.table("daily_metrics").select("*").gte("date", start).lte("date", end).order("date").execute()
        return [{"date_start": r["date"], "date_stop": r["date"],
                 "impressions": str(r["impressions"]), "clicks": str(r["clicks"]),
                 "spend": str(r["spend"]), "ctr": str(r["ctr"]),
                 "cpm": str(r["cpm"]), "reach": str(r["reach"])} for r in (resp.data or [])]

    if USE_DEMO:
        return generate_daily_demo(days)

    start, end = get_date_range(days)
    data = meta_get(f"/act_{ACCOUNT_ID}/insights", {
        "fields": "impressions,clicks,spend,ctr,cpm,reach",
        "time_range": f'{{"since":"{start}","until":"{end}"}}',
        "time_increment": "1",
        "level": "account",
    })
    return data.get("data", [])


@app.get("/api/monthly")
async def get_monthly():
    """Gastos mensais por campanha (últimos meses)."""
    if USE_SUPABASE:
        try:
            resp = supabase.rpc("get_monthly_metrics", {}).execute()
            if resp.data:
                return resp.data
        except Exception:
            pass
        # Fallback: query the view
        resp = supabase.table("monthly_campaign_metrics").select("*").execute()
        return [{"month": str(r["month"])[:7], "month_name": r["month_name"],
                 "funnel": r["funnel"], "campaign_name": r["campaign_name"],
                 "color": r["color"], "spend": float(r["spend"]),
                 "impressions": int(r["impressions"]), "clicks": int(r["clicks"]),
                 "ctr": float(r["ctr"]), "cpm": float(r["cpm"]),
                 "leads": int(r["leads"]), "budget_dia": float(r.get("budget_dia", 0))}
                for r in (resp.data or [])]

    if USE_DEMO:
        return generate_monthly_demo()

    # API mode: últimos 12 meses com incremento mensal
    end = datetime.now().strftime("%Y-%m-%d")
    start = (datetime.now() - timedelta(days=365)).strftime("%Y-%m-%d")
    data = meta_get(f"/act_{ACCOUNT_ID}/insights", {
        "fields": "campaign_name,impressions,clicks,spend,ctr,cpm,actions",
        "time_range": f'{{"since":"{start}","until":"{end}"}}',
        "time_increment": "monthly",
        "level": "campaign",
    })
    result = []
    for r in data.get("data", []):
        cn = r.get("campaign_name", "")
        if "Projectum" not in cn:
            continue
        funnel = funnel_from_name(cn)
        ds = r.get("date_start", "")
        month_label = ds[:7] if ds else ""
        result.append({
            "month": month_label,
            "month_name": month_label,
            "funnel": funnel,
            "campaign_name": cn,
            "color": FUNNEL_COLOR.get(funnel, "#6B7280"),
            "spend": float(r.get("spend", 0)),
            "impressions": int(r.get("impressions", 0)),
            "clicks": int(r.get("clicks", 0)),
            "ctr": float(r.get("ctr", 0)),
            "cpm": float(r.get("cpm", 0)),
            "leads": extract_action(r.get("actions"), "lead"),
        })
    return result


@app.delete("/api/cache")
async def clear_cache():
    _cache.clear()
    return {"cleared": True}


# =====================================================
# LINKEDIN ADS — Demo Data + Endpoints
# =====================================================

DEMO_LINKEDIN_CAMPAIGNS = [
    {
        "id": "594114753",
        "name": "L1 — Awareness — Gestores de Shopping",
        "status": "DRAFT",
        "funnel": "TOPO",
        "funnel_color": "#0077B5",
        "objective": "BRAND_AWARENESS",
        "daily_budget": 40.00,
        "impressions": 4820,
        "clicks": 86,
        "spend": 312.50,
        "ctr": 1.78,
        "cpm": 64.83,
        "cpc": 3.63,
        "reach": 2180,
        "frequency": 2.21,
        "leads": 0,
    },
    {
        "id": "594114900",
        "name": "L2 — Consideração — Decisores de Shopping",
        "status": "DRAFT",
        "funnel": "MEIO",
        "funnel_color": "#0A66C2",
        "objective": "WEBSITE_VISITS",
        "daily_budget": 30.00,
        "impressions": 3150,
        "clicks": 67,
        "spend": 228.40,
        "ctr": 2.13,
        "cpm": 72.51,
        "cpc": 3.41,
        "reach": 1420,
        "frequency": 2.22,
        "leads": 2,
    },
]

DEMO_LINKEDIN_ADS = [
    {
        "id": "ad_li_01", "name": "Vila Alemã — Do conceito à instalação",
        "status": "DRAFT", "campaign_id": "594114753",
        "campaign_name": "L1 — Awareness — Gestores de Shopping",
        "funnel": "TOPO", "funnel_color": "#0077B5",
        "impressions": 1680, "clicks": 32, "spend": 108.40,
        "ctr": 1.90, "cpm": 64.52, "cpc": 3.39,
        "reach": 820, "frequency": 2.05, "leads": 0,
    },
    {
        "id": "ad_li_02", "name": "Multidão — Decoração que lota",
        "status": "DRAFT", "campaign_id": "594114753",
        "campaign_name": "L1 — Awareness — Gestores de Shopping",
        "funnel": "TOPO", "funnel_color": "#0077B5",
        "impressions": 1240, "clicks": 22, "spend": 82.30,
        "ctr": 1.77, "cpm": 66.37, "cpc": 3.74,
        "reach": 580, "frequency": 2.14, "leads": 0,
    },
    {
        "id": "ad_li_03", "name": "Diferencial — 90% terceirizam",
        "status": "DRAFT", "campaign_id": "594114753",
        "campaign_name": "L1 — Awareness — Gestores de Shopping",
        "funnel": "TOPO", "funnel_color": "#0077B5",
        "impressions": 1020, "clicks": 18, "spend": 68.20,
        "ctr": 1.76, "cpm": 66.86, "cpc": 3.79,
        "reach": 460, "frequency": 2.22, "leads": 0,
    },
    {
        "id": "ad_li_04", "name": "Fabricação — Isso é fabricado",
        "status": "DRAFT", "campaign_id": "594114753",
        "campaign_name": "L1 — Awareness — Gestores de Shopping",
        "funnel": "TOPO", "funnel_color": "#0077B5",
        "impressions": 880, "clicks": 14, "spend": 53.60,
        "ctr": 1.59, "cpm": 60.91, "cpc": 3.83,
        "reach": 320, "frequency": 2.75, "leads": 0,
    },
    {
        "id": "ad_li_05", "name": "Case Vila Alemã — Projeto executado",
        "status": "DRAFT", "campaign_id": "594114900",
        "campaign_name": "L2 — Consideração — Decisores de Shopping",
        "funnel": "MEIO", "funnel_color": "#0A66C2",
        "impressions": 1620, "clicks": 38, "spend": 124.60,
        "ctr": 2.35, "cpm": 76.91, "cpc": 3.28,
        "reach": 780, "frequency": 2.08, "leads": 1,
    },
    {
        "id": "ad_li_06", "name": "Experiência — Natal que vira resultado",
        "status": "DRAFT", "campaign_id": "594114900",
        "campaign_name": "L2 — Consideração — Decisores de Shopping",
        "funnel": "MEIO", "funnel_color": "#0A66C2",
        "impressions": 1530, "clicks": 29, "spend": 103.80,
        "ctr": 1.90, "cpm": 67.84, "cpc": 3.58,
        "reach": 640, "frequency": 2.39, "leads": 1,
    },
]


def generate_linkedin_daily_demo(days: int):
    rows = []
    base_date = datetime.now() - timedelta(days=days)
    for d in range(days):
        dt = base_date + timedelta(days=d)
        if dt.weekday() >= 5:
            spend = random.uniform(5, 18)
        else:
            spend = random.uniform(15, 45)
        impressions = int(spend * random.uniform(12, 20))
        clicks = max(1, int(impressions * random.uniform(0.015, 0.028)))
        ctr = round(clicks / impressions * 100, 2) if impressions else 0
        cpm = round(spend / impressions * 1000, 2) if impressions else 0
        reach = int(impressions * random.uniform(0.35, 0.55))
        rows.append({
            "date_start": dt.strftime("%Y-%m-%d"),
            "date_stop": dt.strftime("%Y-%m-%d"),
            "impressions": str(impressions),
            "clicks": str(clicks),
            "spend": str(round(spend, 2)),
            "ctr": str(ctr),
            "cpm": str(cpm),
            "reach": str(reach),
        })
    return rows


def generate_linkedin_monthly_demo():
    months = []
    now = datetime.now()
    campaigns = [
        ("L1 — Awareness", "TOPO", "#0077B5", 40),
        ("L2 — Consideração", "MEIO", "#0A66C2", 30),
    ]
    for m_offset in range(3):
        dt = now - timedelta(days=30 * m_offset)
        month_str = dt.strftime("%Y-%m")
        month_name = dt.strftime("%b/%Y")
        for cname, funnel, color, budget in campaigns:
            factor = 1.0 - (m_offset * 0.15)
            spend = round(budget * 30 * factor * random.uniform(0.85, 1.05), 2)
            impressions = int(spend * random.uniform(12, 18))
            clicks = int(impressions * random.uniform(0.015, 0.025))
            leads = random.randint(0, 2) if funnel == "MEIO" else 0
            months.append({
                "month": month_str, "month_name": month_name,
                "funnel": funnel, "campaign_name": cname,
                "color": color, "spend": spend,
                "impressions": impressions, "clicks": clicks,
                "ctr": round(clicks / impressions * 100, 2) if impressions else 0,
                "cpm": round(spend / impressions * 1000, 2) if impressions else 0,
                "leads": leads, "budget_dia": budget,
            })
    return months


@app.get("/api/linkedin/summary")
async def linkedin_summary(days: int = Query(30, ge=7, le=365)):
    camps = DEMO_LINKEDIN_CAMPAIGNS
    total = {
        "spend": sum(c["spend"] for c in camps),
        "impressions": sum(c["impressions"] for c in camps),
        "clicks": sum(c["clicks"] for c in camps),
        "reach": sum(c["reach"] for c in camps),
        "leads": sum(c["leads"] for c in camps),
    }
    total["ctr"] = round(total["clicks"] / total["impressions"] * 100, 2) if total["impressions"] else 0
    total["cpm"] = round(total["spend"] / total["impressions"] * 1000, 2) if total["impressions"] else 0
    total["cpc"] = round(total["spend"] / total["clicks"], 2) if total["clicks"] else 0
    return total


@app.get("/api/linkedin/campaigns")
async def linkedin_campaigns(days: int = Query(30, ge=7, le=365)):
    return DEMO_LINKEDIN_CAMPAIGNS


@app.get("/api/linkedin/ads")
async def linkedin_ads(days: int = Query(30, ge=7, le=365)):
    return DEMO_LINKEDIN_ADS


@app.get("/api/linkedin/daily")
async def linkedin_daily(days: int = Query(30, ge=7, le=365)):
    return generate_linkedin_daily_demo(days)


@app.get("/api/linkedin/monthly")
async def linkedin_monthly():
    return generate_linkedin_monthly_demo()


# =====================================================
# GOOGLE ADS — Real API Endpoints
# =====================================================

GOOGLE_CUSTOMER_ID = os.getenv("GOOGLE_ADS_CUSTOMER_ID", "3213298943")
_gads_client = None


def _get_gads_client():
    global _gads_client
    if _gads_client is not None:
        return _gads_client
    try:
        from google.ads.googleads.client import GoogleAdsClient as _GoogleAdsClient
        # Tenta carregar do arquivo local (dev)
        yaml_path = Path(__file__).parent / "google-ads.yaml"
        if yaml_path.exists():
            _gads_client = _GoogleAdsClient.load_from_storage(str(yaml_path))
        else:
            # Em produção: carrega das variáveis de ambiente
            credentials = {
                "developer_token": os.getenv("GOOGLE_ADS_DEVELOPER_TOKEN", ""),
                "client_id": os.getenv("GOOGLE_ADS_CLIENT_ID", ""),
                "client_secret": os.getenv("GOOGLE_ADS_CLIENT_SECRET", ""),
                "refresh_token": os.getenv("GOOGLE_ADS_REFRESH_TOKEN", ""),
                "use_proto_plus": True,
            }
            _gads_client = _GoogleAdsClient.load_from_dict(credentials)
        return _gads_client
    except Exception as e:
        raise RuntimeError(f"Google Ads API não configurada: {e}")


def _micros_to_brl(micros):
    return round(micros / 1_000_000, 2)


def fetch_google_campaigns(days: int):
    client = _get_gads_client()
    ga_service = client.get_service("GoogleAdsService")
    query = f"""
        SELECT
            campaign.id,
            campaign.name,
            campaign.status,
            metrics.impressions,
            metrics.clicks,
            metrics.cost_micros,
            metrics.ctr,
            metrics.average_cpc,
            metrics.conversions
        FROM campaign
        WHERE segments.date DURING LAST_{days}_DAYS
          AND campaign.status != 'REMOVED'
        ORDER BY metrics.cost_micros DESC
    """
    response = ga_service.search(customer_id=GOOGLE_CUSTOMER_ID, query=query)
    campaigns = []
    for row in response:
        c = row.campaign
        m = row.metrics
        spend = _micros_to_brl(m.cost_micros)
        clicks = m.clicks
        impressions = m.impressions
        campaigns.append({
            "id": str(c.id),
            "name": c.name,
            "status": c.status.name,
            "spend": spend,
            "impressions": impressions,
            "clicks": clicks,
            "reach": impressions,
            "leads": int(m.conversions),
            "ctr": round(m.ctr * 100, 2),
            "cpc": _micros_to_brl(m.average_cpc),
            "cpm": round(spend / impressions * 1000, 2) if impressions else 0,
        })
    return campaigns


def fetch_google_ads_detail(days: int):
    client = _get_gads_client()
    ga_service = client.get_service("GoogleAdsService")
    query = f"""
        SELECT
            ad_group_ad.ad.id,
            ad_group_ad.ad.name,
            ad_group_ad.ad.type_,
            campaign.name,
            ad_group.name,
            metrics.impressions,
            metrics.clicks,
            metrics.cost_micros,
            metrics.ctr,
            metrics.average_cpc,
            metrics.conversions
        FROM ad_group_ad
        WHERE segments.date DURING LAST_{days}_DAYS
          AND ad_group_ad.status != 'REMOVED'
        ORDER BY metrics.cost_micros DESC
        LIMIT 50
    """
    response = ga_service.search(customer_id=GOOGLE_CUSTOMER_ID, query=query)
    ads = []
    for row in response:
        a = row.ad_group_ad.ad
        m = row.metrics
        spend = _micros_to_brl(m.cost_micros)
        clicks = m.clicks
        impressions = m.impressions
        ads.append({
            "id": str(a.id),
            "name": a.name or f"Ad {a.id}",
            "campaign_name": row.campaign.name,
            "ad_group": row.ad_group.name,
            "spend": spend,
            "impressions": impressions,
            "clicks": clicks,
            "leads": int(m.conversions),
            "ctr": round(m.ctr * 100, 2),
            "cpc": _micros_to_brl(m.average_cpc),
            "cpm": round(spend / impressions * 1000, 2) if impressions else 0,
        })
    return ads


def fetch_google_daily(days: int):
    client = _get_gads_client()
    ga_service = client.get_service("GoogleAdsService")
    query = f"""
        SELECT
            segments.date,
            metrics.impressions,
            metrics.clicks,
            metrics.cost_micros,
            metrics.conversions
        FROM customer
        WHERE segments.date DURING LAST_{days}_DAYS
        ORDER BY segments.date ASC
    """
    response = ga_service.search(customer_id=GOOGLE_CUSTOMER_ID, query=query)
    daily = []
    for row in response:
        m = row.metrics
        spend = _micros_to_brl(m.cost_micros)
        daily.append({
            "date": row.segments.date,
            "spend": spend,
            "impressions": m.impressions,
            "clicks": m.clicks,
            "leads": int(m.conversions),
            "ctr": round(m.clicks / m.impressions * 100, 2) if m.impressions else 0,
            "cpc": round(spend / m.clicks, 2) if m.clicks else 0,
        })
    return daily


def fetch_google_monthly():
    client = _get_gads_client()
    ga_service = client.get_service("GoogleAdsService")
    query = """
        SELECT
            segments.month,
            metrics.impressions,
            metrics.clicks,
            metrics.cost_micros,
            metrics.conversions
        FROM customer
        WHERE segments.date DURING LAST_12_MONTHS
        ORDER BY segments.month ASC
    """
    response = ga_service.search(customer_id=GOOGLE_CUSTOMER_ID, query=query)
    monthly = {}
    for row in response:
        month = row.segments.month[:7]  # YYYY-MM
        m = row.metrics
        if month not in monthly:
            monthly[month] = {"month": month, "spend": 0, "impressions": 0, "clicks": 0, "leads": 0}
        monthly[month]["spend"] += _micros_to_brl(m.cost_micros)
        monthly[month]["impressions"] += m.impressions
        monthly[month]["clicks"] += m.clicks
        monthly[month]["leads"] += int(m.conversions)
    result = list(monthly.values())
    for r in result:
        r["spend"] = round(r["spend"], 2)
        r["ctr"] = round(r["clicks"] / r["impressions"] * 100, 2) if r["impressions"] else 0
        r["cpc"] = round(r["spend"] / r["clicks"], 2) if r["clicks"] else 0
    return result

DEMO_GOOGLE_CAMPAIGNS = [
    {
        "id": "g_camp_01",
        "name": "[Search] Decoração Natal Shopping — Branded",
        "status": "ACTIVE",
        "funnel": "FUNDO",
        "funnel_color": "#10B981",
        "objective": "SEARCH",
        "daily_budget": 35.00,
        "impressions": 6240,
        "clicks": 412,
        "spend": 824.60,
        "ctr": 6.60,
        "cpm": 132.15,
        "cpc": 2.00,
        "reach": 4850,
        "frequency": 1.29,
        "leads": 8,
    },
    {
        "id": "g_camp_02",
        "name": "[Search] Decoração Natal Shopping — Genérico",
        "status": "ACTIVE",
        "funnel": "MEIO",
        "funnel_color": "#8B5CF6",
        "objective": "SEARCH",
        "daily_budget": 50.00,
        "impressions": 18920,
        "clicks": 876,
        "spend": 1542.30,
        "ctr": 4.63,
        "cpm": 81.52,
        "cpc": 1.76,
        "reach": 12400,
        "frequency": 1.53,
        "leads": 5,
    },
    {
        "id": "g_camp_03",
        "name": "[Display] Remarketing — Visitantes Site",
        "status": "ACTIVE",
        "funnel": "FUNDO",
        "funnel_color": "#10B981",
        "objective": "DISPLAY",
        "daily_budget": 20.00,
        "impressions": 42600,
        "clicks": 298,
        "spend": 396.40,
        "ctr": 0.70,
        "cpm": 9.31,
        "cpc": 1.33,
        "reach": 18200,
        "frequency": 2.34,
        "leads": 3,
    },
    {
        "id": "g_camp_04",
        "name": "[YouTube] Vídeo Portfólio — Awareness",
        "status": "ACTIVE",
        "funnel": "TOPO",
        "funnel_color": "#3B82F6",
        "objective": "VIDEO",
        "daily_budget": 25.00,
        "impressions": 68400,
        "clicks": 1024,
        "spend": 512.80,
        "ctr": 1.50,
        "cpm": 7.50,
        "cpc": 0.50,
        "reach": 35600,
        "frequency": 1.92,
        "leads": 0,
    },
]

DEMO_GOOGLE_ADS = [
    # Search Branded
    {"id": "g_ad_01", "name": "Projectum Decoração Natal — Exact Match", "status": "ACTIVE",
     "campaign_id": "g_camp_01", "campaign_name": "[Search] Decoração Natal Shopping — Branded",
     "funnel": "FUNDO", "funnel_color": "#10B981",
     "impressions": 3120, "clicks": 218, "spend": 436.20, "ctr": 6.99, "cpm": 139.81, "cpc": 2.00,
     "reach": 2480, "frequency": 1.26, "leads": 5},
    {"id": "g_ad_02", "name": "Projectum Shopping Centers — Phrase Match", "status": "ACTIVE",
     "campaign_id": "g_camp_01", "campaign_name": "[Search] Decoração Natal Shopping — Branded",
     "funnel": "FUNDO", "funnel_color": "#10B981",
     "impressions": 3120, "clicks": 194, "spend": 388.40, "ctr": 6.22, "cpm": 124.49, "cpc": 2.00,
     "reach": 2370, "frequency": 1.32, "leads": 3},
    # Search Genérico
    {"id": "g_ad_03", "name": "Decoração de Natal para Shopping — Broad", "status": "ACTIVE",
     "campaign_id": "g_camp_02", "campaign_name": "[Search] Decoração Natal Shopping — Genérico",
     "funnel": "MEIO", "funnel_color": "#8B5CF6",
     "impressions": 9820, "clicks": 462, "spend": 812.40, "ctr": 4.70, "cpm": 82.73, "cpc": 1.76,
     "reach": 6800, "frequency": 1.44, "leads": 3},
    {"id": "g_ad_04", "name": "Empresa Decoração Natal — Phrase Match", "status": "ACTIVE",
     "campaign_id": "g_camp_02", "campaign_name": "[Search] Decoração Natal Shopping — Genérico",
     "funnel": "MEIO", "funnel_color": "#8B5CF6",
     "impressions": 9100, "clicks": 414, "spend": 729.90, "ctr": 4.55, "cpm": 80.21, "cpc": 1.76,
     "reach": 5600, "frequency": 1.63, "leads": 2},
    # Display Remarketing
    {"id": "g_ad_05", "name": "Banner 300x250 — Vila Alemã", "status": "ACTIVE",
     "campaign_id": "g_camp_03", "campaign_name": "[Display] Remarketing — Visitantes Site",
     "funnel": "FUNDO", "funnel_color": "#10B981",
     "impressions": 22400, "clicks": 168, "spend": 210.80, "ctr": 0.75, "cpm": 9.41, "cpc": 1.25,
     "reach": 9800, "frequency": 2.29, "leads": 2},
    {"id": "g_ad_06", "name": "Banner 728x90 — Portfólio Natal", "status": "ACTIVE",
     "campaign_id": "g_camp_03", "campaign_name": "[Display] Remarketing — Visitantes Site",
     "funnel": "FUNDO", "funnel_color": "#10B981",
     "impressions": 20200, "clicks": 130, "spend": 185.60, "ctr": 0.64, "cpm": 9.19, "cpc": 1.43,
     "reach": 8400, "frequency": 2.40, "leads": 1},
    # YouTube
    {"id": "g_ad_07", "name": "Vídeo 30s — Portfólio Projectum 2025", "status": "ACTIVE",
     "campaign_id": "g_camp_04", "campaign_name": "[YouTube] Vídeo Portfólio — Awareness",
     "funnel": "TOPO", "funnel_color": "#3B82F6",
     "impressions": 38200, "clicks": 612, "spend": 298.40, "ctr": 1.60, "cpm": 7.81, "cpc": 0.49,
     "reach": 20800, "frequency": 1.84, "leads": 0},
    {"id": "g_ad_08", "name": "Bumper 6s — Natal Shopping Centers", "status": "ACTIVE",
     "campaign_id": "g_camp_04", "campaign_name": "[YouTube] Vídeo Portfólio — Awareness",
     "funnel": "TOPO", "funnel_color": "#3B82F6",
     "impressions": 30200, "clicks": 412, "spend": 214.40, "ctr": 1.36, "cpm": 7.10, "cpc": 0.52,
     "reach": 14800, "frequency": 2.04, "leads": 0},
]


def generate_google_daily_demo(days: int):
    rows = []
    base_date = datetime.now() - timedelta(days=days)
    for d in range(days):
        dt = base_date + timedelta(days=d)
        spend = random.uniform(80, 140) if dt.weekday() < 5 else random.uniform(40, 80)
        impressions = int(spend * random.uniform(30, 60))
        clicks = max(1, int(impressions * random.uniform(0.018, 0.04)))
        ctr = round(clicks / impressions * 100, 2) if impressions else 0
        cpm = round(spend / impressions * 1000, 2) if impressions else 0
        reach = int(impressions * random.uniform(0.4, 0.65))
        rows.append({
            "date_start": dt.strftime("%Y-%m-%d"),
            "date_stop": dt.strftime("%Y-%m-%d"),
            "impressions": str(impressions),
            "clicks": str(clicks),
            "spend": str(round(spend, 2)),
            "ctr": str(ctr),
            "cpm": str(cpm),
            "reach": str(reach),
        })
    return rows


def generate_google_monthly_demo():
    months = []
    now = datetime.now()
    campaigns = [
        ("[Search] Branded", "FUNDO", "#10B981", 35),
        ("[Search] Genérico", "MEIO", "#8B5CF6", 50),
        ("[Display] Remarketing", "FUNDO", "#10B981", 20),
        ("[YouTube] Awareness", "TOPO", "#3B82F6", 25),
    ]
    for m_offset in range(4):
        dt = now - timedelta(days=30 * m_offset)
        month_str = dt.strftime("%Y-%m")
        month_name = dt.strftime("%b/%Y")
        for cname, funnel, color, budget in campaigns:
            factor = 1.0 - (m_offset * 0.08)
            spend = round(budget * 30 * factor * random.uniform(0.9, 1.1), 2)
            imp_mult = 50 if 'YouTube' in cname or 'Display' in cname else 12
            impressions = int(spend * random.uniform(imp_mult * 0.8, imp_mult * 1.2))
            ctr_base = 0.7 if 'Display' in cname else (1.5 if 'YouTube' in cname else 5.0)
            clicks = int(impressions * random.uniform(ctr_base * 0.008, ctr_base * 0.012))
            leads = random.randint(1, 4) if funnel in ("FUNDO", "MEIO") else 0
            months.append({
                "month": month_str, "month_name": month_name,
                "funnel": funnel, "campaign_name": cname,
                "color": color, "spend": spend,
                "impressions": impressions, "clicks": clicks,
                "ctr": round(clicks / impressions * 100, 2) if impressions else 0,
                "cpm": round(spend / impressions * 1000, 2) if impressions else 0,
                "leads": leads, "budget_dia": budget,
            })
    return months


@app.get("/api/google/summary")
async def google_summary(days: int = Query(30, ge=7, le=365)):
    try:
        camps = fetch_google_campaigns(days)
        total = {
            "spend": round(sum(c["spend"] for c in camps), 2),
            "impressions": sum(c["impressions"] for c in camps),
            "clicks": sum(c["clicks"] for c in camps),
            "reach": sum(c["impressions"] for c in camps),
            "leads": sum(c["leads"] for c in camps),
        }
        total["ctr"] = round(total["clicks"] / total["impressions"] * 100, 2) if total["impressions"] else 0
        total["cpm"] = round(total["spend"] / total["impressions"] * 1000, 2) if total["impressions"] else 0
        total["cpc"] = round(total["spend"] / total["clicks"], 2) if total["clicks"] else 0
        return total
    except Exception as e:
        return {"error": str(e), "spend": 0, "impressions": 0, "clicks": 0, "reach": 0, "leads": 0, "ctr": 0, "cpm": 0, "cpc": 0}


@app.get("/api/google/campaigns")
async def google_campaigns(days: int = Query(30, ge=7, le=365)):
    try:
        return fetch_google_campaigns(days)
    except Exception as e:
        return [{"error": str(e)}]


@app.get("/api/google/ads")
async def google_ads(days: int = Query(30, ge=7, le=365)):
    try:
        return fetch_google_ads_detail(days)
    except Exception as e:
        return [{"error": str(e)}]


@app.get("/api/google/daily")
async def google_daily(days: int = Query(30, ge=7, le=365)):
    try:
        return fetch_google_daily(days)
    except Exception as e:
        return [{"error": str(e)}]


@app.get("/api/google/monthly")
async def google_monthly():
    try:
        return fetch_google_monthly()
    except Exception as e:
        return [{"error": str(e)}]
