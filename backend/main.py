"""
Projectum Ads Dashboard — Backend API
Modo DEMO (dados das campanhas reais) + Modo API (Meta Graph API v21.0)
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
USE_DEMO = not bool(META_TOKEN)

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
    return {
        "status": "ok",
        "mode": "demo" if USE_DEMO else "api",
        "account_id": ACCOUNT_ID,
        "token_configured": bool(META_TOKEN),
    }


@app.get("/api/summary")
async def get_summary(days: int = Query(30, ge=1, le=365)):
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
