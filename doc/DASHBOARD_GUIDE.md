# 📊 Dashboard RFM Streamlit

Guide simple pour utiliser le dashboard.

---

## 🚀 Lancer le Dashboard

```powershell
cd "d:\data eng\projet-rfm-airflow-docker"
streamlit run src/app/main.py
```

Accès : **http://localhost:8501**

---

## 📑 Les 5 Onglets

| Tab | Contenu | Utilité |
|-----|---------|---------|
| 📈 **Vue d'ensemble** | KPIs globaux, revenu mensuel, pays | Aperçu business |
| 🎯 **Segmentation RFM** | Distribution des 8 segments, stats | Voir la répartition clients |
| 🔍 **Analyse Détaillée** | Graphiques scatter, histogrammes, heatmap | Comprendre les patterns |
| 📋 **Données Brutes** | Tableau complet + filtres + export CSV | Analyser individuellement |
| 🚀 **Advanced Analytics** | Product RFM, Churn, Géographie, CLV (optionnel) | Analyses approfondies |

---

## 🎮 Filtres (Sidebar)

**Segments** : Cocher/décocher les segments à afficher  
**Récence** : Filtrer par jours depuis dernier achat  
**Montant** : Filtrer par montant total dépensé  

→ S'appliquent en temps réel à tous les graphiques

---

## 8️⃣ Les 8 Segments RFM

| Segment | Description | Action |
|---------|-------------|--------|
| 🏆 Champions | Meilleurs clients (R≥4, F≥4, M≥4) | VIP loyalty program |
| 💎 Clients Fidèles | Fidèles et rentables (R≥3, F≥3, M≥3) | Maintenir engagement |
| 🌱 Nouveaux Clients | Récents mais peu fréquents (R≥4, F≤2) | Convertir habitants |
| 📈 Clients Potentiels | Bon potentiel (R≥3, F≥1, M≥2) | Upsell products |
| ⚠️ À Risque | Ancien mais fréquent (R≤2, F≥3) | Re-engagement campaign |
| 💤 Perdus | Faible engagement (R≤2, F≤2, M≤2) | Win-back ou abandon |
| 🔄 À Réactiver | Ancien mais gros montant (R≤2, M≥3) | Réactivation exclusive |
| ➖ Moyens | Autres profils | Segmentation fine |

---

## 💡 Cas d'Usage Rapides

### Voir les Champions
1. Tab 2 → Décochez tous segments sauf "Champions"
2. Tableau "Statistiques par Segment" affiche leurs caractéristiques

### Analyser les Perdus
1. Tab 2 → Filtrez sur "Perdus"  
2. Tab 3 → Voyez leur profil (scatter plots)
3. Tab 4 → Exportez en CSV pour campagne win-back

### Comparer les Pays
1. Tab 1 → Graphique "Top 10 Pays"
2. Identifiez priorités expansion

---

## 🔄 Mise à Jour

Le dashboard se met à jour **automatiquement** après chaque DAG Airflow.

Pour forcer : Appuyez **R** dans Streamlit ou relancez.

---

## 📤 Exporter les Données

**Tab 4** → Bouton "⬇️ Télécharger les données filtrées (CSV)"

Exporte les clients + tous les scores RFM pour usage externe.

---

## ⚠️ Dépannage

| Problème | Solution |
|----------|----------|
| "Impossible charger données" | Vérifier Docker lancé + DAG exécuté |
| Dashboard vide | Relancer DAG Airflow |
| Très lent | Réduire filtres (moins de données) |

---

**✨ C'est tout ! Bon analyse ! ✨**

