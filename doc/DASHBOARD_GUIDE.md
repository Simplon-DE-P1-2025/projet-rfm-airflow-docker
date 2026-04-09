# 📊 Dashboard RFM Streamlit - Guide d'Utilisation

## 🎯 Vue d'ensemble

Le dashboard Streamlit affiche l'analyse RFM complète des clients avec segmentation automatique basée sur les scores de Recency, Frequency et Monetary.

---

## 🚀 Démarrage du Dashboard

```powershell
cd "d:\data eng\projet-rfm-airflow-docker"

# Lancer le dashboard (une fois la pipeline Docker lancée)
streamlit run src/app/main.py
```

Le dashboard sera accessible à : **http://localhost:8501**

---

## 📑 Structure des Onglets

### 📈 **Tab 1 : Vue d'ensemble**
- **KPIs globaux** : Nombre de commandes, clients, revenu total, produits
- **Chiffre d'affaires mensuel** : Tendance de revenu dans le temps
- **Top 10 pays** : Distribution géographique des clients

### 🎯 **Tab 2 : Segmentation RFM**
- **KPIs segments** : Nombre de Champions, Clients à Risque, Perdus
- **Distribution des segments** : Répartition en camembert et barra chart
- **Statistiques détaillées** : Tableau comparatif des segments

### 🔍 **Tab 3 : Analyse Détaillée**
- **Scatter plots** : Récence vs Fréquence, Fréquence vs Montant
- **Histogrammes** : Distribution de la Récence et du Montant par segment
- **Heatmap RFM** : Matrice Récence × Fréquence

### 📋 **Tab 4 : Données Brutes**
- Tableau complet des clients avec tous les scores
- Filtrage avancé
- Export CSV des données filtrées

---

## 🎮 Filtres Sidebar

### Segments
- **Cocher/Décocher individuellement** : Sélectionner chaque segment manuellement
- **Boutons rapides** : "Tout cocher" ou "Tout décocher"

### Plages
- **Récence** : Filtrer par nombre de jours depuis dernier achat
- **Montant** : Filtrer par montant total de dépenses

Les filtres s'appliquent en temps réel à tous les visualisations.

---

## 📊 Segmentation des Clients

| Segment | Signification | R | F | M |
|---------|---------------|---|---|---|
| 🏆 Champions | Meilleurs clients | ≥4 | ≥4 | ≥4 |
| 💎 Clients Fidèles | Fidèles et rentables | ≥3 | ≥3 | ≥3 |
| 🌱 Nouveaux Clients | Récents mais peu fréquents | ≥4 | ≤2 | - |
| 📈 Clients Potentiels | Bon potentiel | ≥3 | ≥1 | ≥2 |
| ⚠️ À Risque | Ancien mais fréquent | ≤2 | ≥3 | - |
| 💤 Perdus | Faible engagement | ≤2 | ≤2 | ≤2 |
| 🔄 À Réactiver | Ancien avec montant élevé | ≤2 | ≤2 | ≥3 |
| ➖ Moyens | Autres profils | - | - | - |

---

## 🔄 Mise à Jour des Données

Le dashboard se met à jour automatiquement (cache de 5 minutes) après chaque exécution du DAG Airflow.

Pour forcer le rafraîchissement :
1. Appuyez sur **R** dans Streamlit
2. Ou relancez le dashboard : `streamlit run src/app/main.py`

---

## 💡 Cas d'Usage Courants

### Identifier les Champions
1. Allez à **Tab 2 : Segmentation RFM**
2. Dans le sidebar, décochez tous les segments sauf "Champions"
3. Consultez le tableau "Statistiques par Segment"

### Analyser les Clients à Risque
1. Tab 2 → Filtrez sur "À Risque"
2. Tab 3 → Visualisez les graphiques scatter pour comprendre le profil
3. Tab 4 → Exportez en CSV pour action marketing

### Comparer les Pays
1. Tab 1 → Consultez le graphique "Top 10 Pays"
2. Fiez-vous à ce segment pour stratégie géographique

---

## 🔧 Dépannage

### "Impossible de charger les données depuis PostgreSQL"
- ✅ Assurez-vous que Docker (`docker-compose up -d`) est lancé
- ✅ Vérifiez que le DAG Airflow `rfm_pipeline` a été exécuté
- ✅ Vérifiez les variables `.env` (DB_HOST, DB_PORT, etc.)

### "Colonnes manquantes dans rfm_analysis"
- ✅ La table `rfm_analysis` doit contenir : customer_id, recency, frequency, monetary, r_score, f_score, m_score, rfm_score, segment
- ✅ Relancez le DAG Airflow pour recalculer les scores

### Dashboard vide ou très lent
- ✅ Les données volumineuses (>1M lignes) peuvent ralentir le rendu
- ✅ Utilisez les filtres pour réduire le nombre de clients affichés

---

## 📤 Export des Données

Depuis Tab 4, cliquez sur "⬇️ Télécharger les données filtrées (CSV)" pour exporter :
- Les clients filtrés uniquement
- Tous les scores RFM
- Segment associé

Utile pour :
- Actions marketing ciblées
- Analysis en Excel
- Import dans d'autres outils

---

## 📝 Notes

- Les scores RFM sont calculés lors du DAG et stockés dans PostgreSQL
- Les segments sont attribués automatiquement selon les régles RFM
- Les couleurs des segments sont cohérentes dans tout le dashboard
- Les emojis aident à la lecture rapide des indicateurs

---

**✨ Bon analyse ! ✨**
