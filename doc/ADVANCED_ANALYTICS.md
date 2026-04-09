# Advanced Analytics

4 analyses optionnelles pour enrichir l'analyse RFM.

---

## 📊 Les 4 Analyses

| Type | Calcule | Table | Utilité |
|------|---------|-------|---------|
| 🏆 **Product RFM** | Performance produits (Star/Strong/Stable/Orphan) | `product_rfm` | Prioriser stocks & pricing |
| 🚨 **Churn Prediction** | Score risque désabonnement (0-100) | `churn_risk` | Campagnes de rétention |
| 🌍 **Geographic** | Opportunités par pays & performance régionale | `geographic_analysis` | Expansion géographique |
| 💰 **CLV Forecast** | Valeur à vie client sur 12-24 mois | `clv_forecast` | Budget allocation par segment |

---

## 1️⃣ Product-Level RFM

**Quoi** : Analyse des produits comme les clients (Récence, Fréquence, Montant)

**Classifications** :
- 🟢 Star (score ≥ 4): Vedettes → boost marketing
- 🔵 Strong (score ≥ 3): Forts → maintenir
- 🟡 Stable (score ≥ 2): Stables → stable
- 🔴 Orphan (score < 2): Losers → clearance/abandon

**Lancer** :
```bash
python src/etl/product_rfm.py
```

**Utiliser** :
```sql
SELECT * FROM product_rfm WHERE performance = 'Star' ORDER BY monetary DESC;
```

---

## 2️⃣ Churn Prediction

**Quoi** : Score risque de désabonnement (60% Récence + 40% Fréquence)

**Niveaux** :
- 🔴 High (80-100): Très à risque → Win-back + 50% off
- 🟠 Medium (60-79): Moyen → Email engagement + 20% off
- 🟡 Low (40-59): Faible → Newsletter + surprise
- 🟢 Very Low (<40): Très stable → VIP loyalty program

**Lancer** :
```bash
python src/etl/churn_prediction.py
```

**Utiliser** :
```sql
SELECT * FROM churn_risk WHERE churn_score >= 80;
```

---

## 3️⃣ Geographic Analysis

**Quoi** : Performance par pays + classification marché

**Classifications** :
- 🟢 Established Leader: High revenue + Recent → Premium strategy
- 🟠 Declining: High revenue + Old → Réactivation
- 🟡 Growing Opportunity: Low revenue + Recent → Expansion
- 🔴 Emerging Market: Low revenue + Old → Investment

**Lancer** :
```bash
python src/etl/geographic_analysis.py
```

**Utiliser** :
```sql
SELECT * FROM geographic_analysis ORDER BY total_revenue DESC;
```

---

## 4️⃣ CLV Forecast

**Quoi** : Valeur à vie prédite sur 12 et 24 mois par segment

**Growth Rates** :
- Champions: +15% | Fidèles: +10% | Nouveaux: +20% | À Risque: -15% | Perdus: -50%

**Lancer** :
```bash
python src/etl/clv_forecast.py
```

**Utiliser** :
```sql
SELECT * FROM clv_forecast ORDER BY clv_24months DESC LIMIT 20;
```

---

## 🚀 Exécuter Toutes les Analyses

**Individuellement** :
```bash
python src/etl/product_rfm.py
python src/etl/churn_prediction.py
python src/etl/geographic_analysis.py
python src/etl/clv_forecast.py
```

**En parallèle** :
```bash
python src/etl/product_rfm.py & python src/etl/churn_prediction.py & \
python src/etl/geographic_analysis.py & python src/etl/clv_forecast.py
```

**Via Airflow** :
```bash
airflow dags trigger advanced_analytics
```

---

## ⏱️ Temps d'Exécution

- Product RFM: ~0.5-2s
- Churn Prediction: ~1-3s
- Geographic: ~0.5-1s
- CLV: ~1-4s

---

## ⚠️ Notes

✅ Dépendances : product_rfm/churn/geo dépendent de `raw_orders` | clv dépend de `rfm_analysis`  
✅ Tables auto-créées avec `DROP IF EXISTS`  
✅ Tout prêt pour intégration dashboard (5ème tab)  

---

**Status:** ✅ Production Ready
