# Advanced Analytics — Priority 3 Enhancements

## 📚 Overview

Quatre nouvelles analyses optionnelles pour enrichir le dashboard RFM et explorer de nouvelles dimensions:

| Feature | Purpose | Tables | Status |
|---------|---------|--------|--------|
| 🏆 **Product-Level RFM** | Identifie produits stars vs orphelins | `product_rfm` | ✅ Ready |
| 🚨 **Churn Prediction** | Scoring de désabonnement (0-100) | `churn_risk` | ✅ Ready |
| 🌍 **Geographic Drill-Down** | Opportunités marché par pays | `geographic_analysis` | ✅ Ready |
| 💰 **CLV Forecast** | Prévision valeur à vie (12-24 mois) | `clv_forecast` | ✅ Ready |

---

## 1️⃣ Product-Level RFM

### Purpose
Analyser la performance des **produits** plutôt que des clients.

### What's Calculated
```
- Recency: Jours depuis dernier achat du produit
- Frequency: Nombre de clients distincts ayant acheté le produit
- Monetary: Montant total généré par le produit
- Performance: Star | Strong | Stable | Orphan (classification)
```

### Business Use Cases
- 🎯 **Inventory Management**: Réduire stock des produits orphelins
- 📈 **Cross-sell**: Bundler produits stars avec moyens/faibles
- 🛍️ **Pricing**: Ajuster prix des stars (marges) vs orphelins (promotion)
- 🎁 **Sourcing**: Identifier produits à relancer ou abandonner

### How to Use

**Standalone:**
```bash
python src/etl/product_rfm.py
```

**In Airflow:**
```bash
airflow tasks trigger advanced_analytics product_rfm_analysis
```

**Query Results:**
```sql
SELECT stock_code, product_name, performance, total_customers, monetary
FROM product_rfm
WHERE performance = 'Star'
ORDER BY monetary DESC
LIMIT 20;
```

### Performance Classifications
- 🟢 **Star** (avg_score ≥ 4): Produits vedettes — boost marketing
- 🔵 **Strong** (avg_score ≥ 3): Produits forts — maintenir
- 🟡 **Stable** (avg_score ≥ 2): Produits stables — stable
- 🔴 **Orphan** (avg_score < 2): Produits orphelins — clearance ou abandon

---

## 2️⃣ Churn Prediction

### Purpose
Identifier clients à **risque de désabonnement** pour intervenir proactivement.

### What's Calculated
```
Churn Score (0-100):
  = Recency Weight (60%) + Frequency Weight (40%)
  
Recency Weight:
  - 95 pts: > 180 jours (très ancien)
  - 80 pts: 120-180 jours
  - 60 pts: 90-120 jours
  - 40 pts: 30-90 jours
  - 20 pts: < 30 jours (très récent)

Frequency Weight:
  - 80 pts: < 0.33 achats/mois (très faible)
  - 60 pts: 0.33-0.66 achats/mois
  - 40 pts: 0.66-1.0 achats/mois
  - 20 pts: 1.0-2.0 achats/mois
  - 5 pts: > 2.0 achats/mois (très fréquent)
```

### Churn Risk Levels

| Score | Risk | Color | Recommendation |
|-------|------|-------|-----------------|
| 80-100 | 🔴 High | High | Win-back campaign + special offer (50% off) |
| 60-79 | 🟠 Medium | Medium | Engagement email + coupon (20% off) |
| 40-59 | 🟡 Low | Low | Regular newsletter + surprise |
| <40 | 🟢 Very Low | Very Low | VIP loyalty program + exclusive access |

### Business Use Cases
- 📧 **Email Campaigns**: Segment par churn score → tailored messaging
- 🎁 **Retention Offers**: Win-back pour High, loyalty perks pour Very Low
- 📱 **CRM Integration**: Flag churners in CRM for outreach
- 📊 **Churn Rate Tracking**: Monitor churn_risk trends monthly

### How to Use

**Standalone:**
```bash
python src/etl/churn_prediction.py
```

**In Airflow:**
```bash
airflow tasks trigger advanced_analytics churn_prediction
```

**Query Results:**
```sql
-- Clients à haut risque avec recommendations
SELECT customer_id, churn_score, churn_risk, recommendation
FROM churn_risk
WHERE churn_score >= 80
ORDER BY churn_score DESC
LIMIT 50;
```

### Output Fields
- `churn_score`: Score de 0-100 (plus haut = plus à risque)
- `churn_risk`: Classification 🔴 High / 🟠 Medium / 🟡 Low / 🟢 Very Low
- `recommendation`: Action marketing suggérée
- `recency`: Jours depuis dernier achat
- `frequency`: Nombre de commandes totales

---

## 3️⃣ Geographic Drill-Down

### Purpose
Identifier **opportunités d'expansion** par pays et performance régionale.

### What's Calculated
```
- Total Customers: Clients distincts par pays
- Total Orders: Commandes totales
- Total Revenue: Montant payé
- Avg Order Value: Revenue / Orders
- Avg Customer Value: Revenue / Customers
- Recency Average: Moyenne des jours depuis dernier achat
- Market Growth Potential: Classification d'opportunité
- Priority Rank: Ranking par revenue
```

### Market Classifications

| Type | Characteristics | Strategy |
|------|-----------------|----------|
| 🟢 **Established Leader** | High revenue + Low recency | Maximize: Premium products, exclusive offers |
| 🟠 **Declining** | High revenue + High recency | Reactivate: "We miss you" campaign |
| 🟡 **Growing Opportunity** | Low revenue + Low recency | Expand: Increase marketing budget |
| 🔴 **Emerging Market** | Low revenue + High recency | Invest: New partnerships, local ads |

### Business Use Cases
- 🌍 **Market Expansion**: Prioritize emerging markets avec croissance potentielle
- 📊 **Regional Reports**: Analyze performance par zone géographique
- 💼 **Localization**: Adapter produits/pricing par marché
- 🚀 **Growth Planning**: Allouer budget marketing par région

### How to Use

**Standalone:**
```bash
python src/etl/geographic_analysis.py
```

**In Airflow:**
```bash
airflow tasks trigger advanced_analytics geographic_analysis
```

**Query Results:**
```sql
-- Top 5 pays par priorité
SELECT priority_rank, country, total_revenue, market_growth_potential
FROM geographic_analysis
ORDER BY priority_rank
LIMIT 5;

-- Opportunités de croissance
SELECT country, total_customers, market_growth_potential
FROM geographic_analysis
WHERE market_growth_potential IN ('Growing Opportunity', 'Emerging Market')
ORDER BY total_customers DESC;
```

---

## 4️⃣ CLV Forecast

### Purpose
Prédire la **valeur à vie clientèle** (Customer Lifetime Value) sur 12 et 24 mois.

### What's Calculated
```
Historical Value: SUM de tous les achats passés

Avg Monthly Value: Historical Value / Months Active

Growth Rate (par segment):
  Champions: +15% (best customers, likely to increase)
  Clients Fidèles: +10% (loyal, stable growth)
  Nouveaux Clients: +20% (high potential)
  Clients Potentiels: +8% (moderate growth)
  À Risque: -15% (likely to decrease)
  Perdus: -50% (very low chance)
  À Réactiver: +5% (reactivation bonus)
  Moyens: 0% (stable)

CLV 12 Months: Avg Monthly Value × 12 × Growth Rate
CLV 24 Months: Avg Monthly Value × 24 × Growth Rate

Forecast Confidence:
  🟢 High: Customer active 12+ months with €100+ lifetime value
  🟡 Medium: 3-11 months active OR €<100 lifetime
  🟡 Low: <€100 lifetime value (early stage)
```

### Business Use Cases
- 💼 **Customer Portfolio Value**: Connaître future revenue par segment
- 🎯 **Resource Allocation**: Invest davantage dans Champions vs Perdus
- 📈 **Revenue Forecasting**: Budget planning sur 12-24 mois
- 🏆 **VIP Identification**: Prioriser Champions pour exclusive perks
- 💡 **Segment Strategy**: Adapter approche par segment CLV forecast

### How to Use

**Standalone:**
```bash
python src/etl/clv_forecast.py
```

**In Airflow:**
```bash
airflow tasks trigger advanced_analytics clv_forecast
```

**Query Results:**
```sql
-- Top 20 clients par CLV 24 mois
SELECT customer_id, segment, clv_24months, forecast_confidence
FROM clv_forecast
ORDER BY clv_24months DESC
LIMIT 20;

-- Classe par segment CLV moyen
SELECT segment, 
       COUNT(*) as customers,
       AVG(clv_12months) as avg_12m,
       AVG(clv_24months) as avg_24m,
       SUM(clv_24months) as total_24m
FROM clv_forecast
GROUP BY segment
ORDER BY total_24m DESC;
```

---

## 🚀 Complete Workflow

### Option A: Manual Execution (Ad-hoc)
```bash
# Run individually
python src/etl/product_rfm.py
python src/etl/churn_prediction.py
python src/etl/geographic_analysis.py
python src/etl/clv_forecast.py

# Or all at once (en parallèle dans votre shell)
python src/etl/product_rfm.py & \
python src/etl/churn_prediction.py & \
python src/etl/geographic_analysis.py & \
python src/etl/clv_forecast.py
```

### Option B: Via Airflow DAG
```bash
# Déclencher le DAG avancé
airflow dags trigger advanced_analytics

# Ou scheduler weekly (edit advanced_analytics_dag.py)
# schedule_interval='@weekly'
```

### Option C: Intégration Main Pipeline
```python
# Modifier rfm_pipeline_dag.py pour exécuter après load:
from advanced_analytics_dag import (
    task_product_rfm, task_churn, task_geo, task_clv
)

task_load >> [task_product_rfm, task_churn, task_geo, task_clv]
```

---

## 📊 Dashboard Integration

Pour ajouter une **5ème tab** au Streamlit dashboard:

```python
# main.py - ajouter après les 4 tabs existantes
with st.tabs([..., "Advanced Analytics"]):
    selected_analysis = st.selectbox(
        "Choose Analysis",
        ["Product RFM", "Churn Prediction", "Geographic", "CLV Forecast"]
    )
    
    if selected_analysis == "Product RFM":
        df_prod = pd.read_sql("SELECT * FROM product_rfm...", engine)
        st.dataframe(df_prod)
        # ... visualizations
```

---

## ⚠️ Important Notes

### Data Dependencies
- ✅ product_rfm: Depend on `raw_orders` ✓
- ✅ churn_prediction: Depend on `raw_orders` ✓
- ✅ geographic_analysis: Depend on `raw_orders` ✓
- ✅ clv_forecast: Depend on `rfm_analysis` ✓

### Tous les scripts créent les tables automatiquement avec `DROP IF EXISTS`

### Performance
- product_rfm: ~0.5-2s (depends on products count)
- churn_prediction: ~1-3s (per customer grouping)
- geographic_analysis: ~0.5-1s (per country)
- clv_forecast: ~1-4s (per customer calculation)

### Monitoring
Check execution in Airflow logs:
```bash
docker compose exec airflow logs -f
# Output: look for ✅ success or ❌ error messages
```

---

## 🎯 Next Steps

1. **Run Product-RFM** → Analyze which products to promote/discontinue
2. **Run Churn Prediction** → Launch win-back campaign for High risk
3. **Run Geographic** → Plan expansion in Growing Opportunity markets
4. **Run CLV Forecast** → Allocate marketing budget by segment

Then integrate findings into **dashboard tabs** and **marketing campaigns**!

---

## 📞 Troubleshooting

| Issue | Solution |
|-------|----------|
| Table already exists | Tables auto-drop with `DROP TABLE IF EXISTS` |
| No data in output | Check rfm_analysis has data. raw_orders must have invoices |
| Slow execution | Might need table indexes, e.g., `CREATE INDEX idx_customer_id ON raw_orders(customer_id);` |
| Missing segments | Ensure transform.py ran successfully first |

---

**Last Updated:** April 2026
**Status:** ✅ Production Ready
