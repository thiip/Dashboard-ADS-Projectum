-- =====================================================
-- Projectum Ads Dashboard — Supabase Schema
-- =====================================================

-- Campanhas
CREATE TABLE IF NOT EXISTS campaigns (
    id TEXT PRIMARY KEY,
    name TEXT NOT NULL,
    funnel TEXT NOT NULL CHECK (funnel IN ('TOPO', 'MEIO', 'FUNDO')),
    status TEXT DEFAULT 'ACTIVE',
    objective TEXT,
    daily_budget NUMERIC(10,2) DEFAULT 0,
    funnel_color TEXT,
    created_at TIMESTAMPTZ DEFAULT now(),
    updated_at TIMESTAMPTZ DEFAULT now()
);

-- Anuncios
CREATE TABLE IF NOT EXISTS ads (
    id TEXT PRIMARY KEY,
    name TEXT NOT NULL,
    campaign_id TEXT REFERENCES campaigns(id) ON DELETE CASCADE,
    status TEXT DEFAULT 'ACTIVE',
    funnel TEXT NOT NULL CHECK (funnel IN ('TOPO', 'MEIO', 'FUNDO')),
    funnel_color TEXT,
    created_at TIMESTAMPTZ DEFAULT now(),
    updated_at TIMESTAMPTZ DEFAULT now()
);

-- Metricas diarias (nivel conta)
CREATE TABLE IF NOT EXISTS daily_metrics (
    id BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    date DATE NOT NULL,
    impressions INTEGER DEFAULT 0,
    clicks INTEGER DEFAULT 0,
    spend NUMERIC(10,2) DEFAULT 0,
    ctr NUMERIC(6,4) DEFAULT 0,
    cpm NUMERIC(10,2) DEFAULT 0,
    cpc NUMERIC(10,2) DEFAULT 0,
    reach INTEGER DEFAULT 0,
    UNIQUE(date)
);

-- Metricas diarias por campanha
CREATE TABLE IF NOT EXISTS campaign_daily_metrics (
    id BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    date DATE NOT NULL,
    campaign_id TEXT REFERENCES campaigns(id) ON DELETE CASCADE,
    impressions INTEGER DEFAULT 0,
    clicks INTEGER DEFAULT 0,
    spend NUMERIC(10,2) DEFAULT 0,
    ctr NUMERIC(6,4) DEFAULT 0,
    cpm NUMERIC(10,2) DEFAULT 0,
    cpc NUMERIC(10,2) DEFAULT 0,
    reach INTEGER DEFAULT 0,
    frequency NUMERIC(6,2) DEFAULT 0,
    leads INTEGER DEFAULT 0,
    UNIQUE(date, campaign_id)
);

-- Metricas diarias por anuncio
CREATE TABLE IF NOT EXISTS ad_daily_metrics (
    id BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    date DATE NOT NULL,
    ad_id TEXT REFERENCES ads(id) ON DELETE CASCADE,
    campaign_id TEXT REFERENCES campaigns(id) ON DELETE CASCADE,
    impressions INTEGER DEFAULT 0,
    clicks INTEGER DEFAULT 0,
    spend NUMERIC(10,2) DEFAULT 0,
    ctr NUMERIC(6,4) DEFAULT 0,
    cpm NUMERIC(10,2) DEFAULT 0,
    cpc NUMERIC(10,2) DEFAULT 0,
    reach INTEGER DEFAULT 0,
    leads INTEGER DEFAULT 0,
    UNIQUE(date, ad_id)
);

-- View: Metricas mensais por campanha (para dashboard de gastos mensais)
CREATE OR REPLACE VIEW monthly_campaign_metrics AS
SELECT
    date_trunc('month', date)::DATE AS month,
    to_char(date_trunc('month', date), 'Mon/YYYY') AS month_name,
    campaign_id,
    c.name AS campaign_name,
    c.funnel,
    c.funnel_color AS color,
    c.daily_budget AS budget_dia,
    SUM(cdm.spend) AS spend,
    SUM(cdm.impressions) AS impressions,
    SUM(cdm.clicks) AS clicks,
    CASE WHEN SUM(cdm.impressions) > 0
         THEN ROUND(SUM(cdm.clicks)::NUMERIC / SUM(cdm.impressions) * 100, 2)
         ELSE 0 END AS ctr,
    CASE WHEN SUM(cdm.impressions) > 0
         THEN ROUND(SUM(cdm.spend) / SUM(cdm.impressions) * 1000, 2)
         ELSE 0 END AS cpm,
    SUM(cdm.leads) AS leads
FROM campaign_daily_metrics cdm
JOIN campaigns c ON c.id = cdm.campaign_id
GROUP BY date_trunc('month', date), campaign_id, c.name, c.funnel, c.funnel_color, c.daily_budget
ORDER BY month, c.funnel;

-- View: Resumo de campanha (periodo customizavel via filtro)
CREATE OR REPLACE VIEW campaign_summary AS
SELECT
    c.id,
    c.name,
    c.funnel,
    c.funnel_color,
    c.status,
    c.objective,
    c.daily_budget,
    COALESCE(SUM(cdm.impressions), 0) AS impressions,
    COALESCE(SUM(cdm.clicks), 0) AS clicks,
    COALESCE(SUM(cdm.spend), 0) AS spend,
    CASE WHEN SUM(cdm.impressions) > 0
         THEN ROUND(SUM(cdm.clicks)::NUMERIC / SUM(cdm.impressions) * 100, 2)
         ELSE 0 END AS ctr,
    CASE WHEN SUM(cdm.impressions) > 0
         THEN ROUND(SUM(cdm.spend) / SUM(cdm.impressions) * 1000, 2)
         ELSE 0 END AS cpm,
    CASE WHEN SUM(cdm.clicks) > 0
         THEN ROUND(SUM(cdm.spend) / SUM(cdm.clicks), 2)
         ELSE 0 END AS cpc,
    COALESCE(SUM(cdm.reach), 0) AS reach,
    CASE WHEN SUM(cdm.reach) > 0
         THEN ROUND(SUM(cdm.impressions)::NUMERIC / SUM(cdm.reach), 2)
         ELSE 0 END AS frequency,
    COALESCE(SUM(cdm.leads), 0) AS leads
FROM campaigns c
LEFT JOIN campaign_daily_metrics cdm ON c.id = cdm.campaign_id
GROUP BY c.id, c.name, c.funnel, c.funnel_color, c.status, c.objective, c.daily_budget;

-- View: Resumo de anuncio
CREATE OR REPLACE VIEW ad_summary AS
SELECT
    a.id,
    a.name,
    a.campaign_id,
    c.name AS campaign_name,
    a.status,
    a.funnel,
    a.funnel_color,
    COALESCE(SUM(adm.impressions), 0) AS impressions,
    COALESCE(SUM(adm.clicks), 0) AS clicks,
    COALESCE(SUM(adm.spend), 0) AS spend,
    CASE WHEN SUM(adm.impressions) > 0
         THEN ROUND(SUM(adm.clicks)::NUMERIC / SUM(adm.impressions) * 100, 2)
         ELSE 0 END AS ctr,
    CASE WHEN SUM(adm.impressions) > 0
         THEN ROUND(SUM(adm.spend) / SUM(adm.impressions) * 1000, 2)
         ELSE 0 END AS cpm,
    CASE WHEN SUM(adm.clicks) > 0
         THEN ROUND(SUM(adm.spend) / SUM(adm.clicks), 2)
         ELSE 0 END AS cpc,
    COALESCE(SUM(adm.reach), 0) AS reach,
    COALESCE(SUM(adm.leads), 0) AS leads
FROM ads a
JOIN campaigns c ON c.id = a.campaign_id
LEFT JOIN ad_daily_metrics adm ON a.id = adm.ad_id
GROUP BY a.id, a.name, a.campaign_id, c.name, a.status, a.funnel, a.funnel_color;

-- =====================================================
-- SEED DATA — Campanhas e Anuncios Projectum reais
-- =====================================================

INSERT INTO campaigns (id, name, funnel, status, objective, daily_budget, funnel_color) VALUES
('6918443271116', '[TOPO] Reconhecimento - Projectum Natal 2026', 'TOPO', 'ACTIVE', 'OUTCOME_AWARENESS', 13.00, '#3B82F6'),
('6918443936116', '[MEIO] Consideração - Projectum Natal 2026', 'MEIO', 'ACTIVE', 'OUTCOME_TRAFFIC', 30.00, '#8B5CF6'),
('6918443949116', '[FUNDO] Conversão - Projectum Natal 2026', 'FUNDO', 'ACTIVE', 'OUTCOME_LEADS', 23.00, '#10B981')
ON CONFLICT (id) DO NOTHING;

INSERT INTO ads (id, name, campaign_id, status, funnel, funnel_color) VALUES
('6930266155300', '[TOPO] Ad1 - Vídeo Portfólio', '6918443271116', 'PAUSED', 'TOPO', '#3B82F6'),
('6930266155400', '[TOPO] Ad2 - Carrossel Projetos', '6918443271116', 'ACTIVE', 'TOPO', '#3B82F6'),
('6930266155716', '[TOPO] Ad3 - Impacto Visual', '6918443271116', 'ACTIVE', 'TOPO', '#3B82F6'),
('6930266156100', '[MEIO] Ad3 - Case de Sucesso', '6918443936116', 'ACTIVE', 'MEIO', '#8B5CF6'),
('6930266156200', '[MEIO] Ad4 - Storytelling Resiliência', '6918443936116', 'ACTIVE', 'MEIO', '#8B5CF6'),
('6930266156300', '[MEIO] Ad5 - Diferencial Externo + Shopping', '6918443936116', 'ACTIVE', 'MEIO', '#8B5CF6'),
('6930266156600', '[FUNDO] Ad6 - Lead Form Direto', '6918443949116', 'ACTIVE', 'FUNDO', '#10B981'),
('6930266156700', '[FUNDO] Ad7 - WhatsApp Direct', '6918443949116', 'ACTIVE', 'FUNDO', '#10B981'),
('6930266156800', '[FUNDO] Ad8 - Urgência Agenda Limitada', '6918443949116', 'ACTIVE', 'FUNDO', '#10B981')
ON CONFLICT (id) DO NOTHING;

-- Seed: metricas diárias (últimos 30 dias) para cada campanha
-- Gerado via função para popular dados realistas
DO $$
DECLARE
    d DATE;
    camp RECORD;
    base_spend NUMERIC;
    day_spend NUMERIC;
    day_impressions INTEGER;
    day_clicks INTEGER;
    day_leads INTEGER;
    rnd NUMERIC;
BEGIN
    FOR d IN SELECT generate_series(
        CURRENT_DATE - INTERVAL '30 days',
        CURRENT_DATE - INTERVAL '1 day',
        '1 day'::INTERVAL
    )::DATE LOOP
        FOR camp IN SELECT * FROM campaigns LOOP
            rnd := random();

            -- Base spend per campaign
            IF camp.funnel = 'TOPO' THEN base_spend := 13;
            ELSIF camp.funnel = 'MEIO' THEN base_spend := 30;
            ELSE base_spend := 23;
            END IF;

            day_spend := ROUND((base_spend * (0.85 + rnd * 0.3))::NUMERIC, 2);
            day_impressions := (day_spend / 0.016 * (0.85 + random() * 0.3))::INTEGER;
            day_clicks := (day_impressions * (0.012 + random() * 0.015))::INTEGER;
            day_leads := 0;

            IF camp.funnel = 'FUNDO' AND random() > 0.85 THEN
                day_leads := 1;
            END IF;

            INSERT INTO campaign_daily_metrics (date, campaign_id, impressions, clicks, spend, ctr, cpm, cpc, reach, frequency, leads)
            VALUES (
                d,
                camp.id,
                day_impressions,
                day_clicks,
                day_spend,
                ROUND(day_clicks::NUMERIC / GREATEST(day_impressions, 1) * 100, 2),
                ROUND(day_spend / GREATEST(day_impressions, 1) * 1000, 2),
                ROUND(day_spend / GREATEST(day_clicks, 1), 2),
                (day_impressions * (0.6 + random() * 0.2))::INTEGER,
                1.0 + random() * 0.8,
                day_leads
            )
            ON CONFLICT (date, campaign_id) DO NOTHING;
        END LOOP;

        -- Account-level daily
        INSERT INTO daily_metrics (date, impressions, clicks, spend, ctr, cpm, cpc, reach)
        SELECT
            d,
            SUM(impressions),
            SUM(clicks),
            SUM(spend),
            ROUND(SUM(clicks)::NUMERIC / GREATEST(SUM(impressions), 1) * 100, 2),
            ROUND(SUM(spend) / GREATEST(SUM(impressions), 1) * 1000, 2),
            ROUND(SUM(spend) / GREATEST(SUM(clicks), 1), 2),
            SUM(reach)
        FROM campaign_daily_metrics
        WHERE date = d
        ON CONFLICT (date) DO NOTHING;
    END LOOP;
END $$;

-- Enable Row Level Security (public read)
ALTER TABLE campaigns ENABLE ROW LEVEL SECURITY;
ALTER TABLE ads ENABLE ROW LEVEL SECURITY;
ALTER TABLE daily_metrics ENABLE ROW LEVEL SECURITY;
ALTER TABLE campaign_daily_metrics ENABLE ROW LEVEL SECURITY;
ALTER TABLE ad_daily_metrics ENABLE ROW LEVEL SECURITY;

CREATE POLICY "Public read campaigns" ON campaigns FOR SELECT USING (true);
CREATE POLICY "Public read ads" ON ads FOR SELECT USING (true);
CREATE POLICY "Public read daily_metrics" ON daily_metrics FOR SELECT USING (true);
CREATE POLICY "Public read campaign_daily_metrics" ON campaign_daily_metrics FOR SELECT USING (true);
CREATE POLICY "Public read ad_daily_metrics" ON ad_daily_metrics FOR SELECT USING (true);
