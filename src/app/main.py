"""
Dashboard RFM — Analyse de la Segmentation Clients
Pipeline Data RFM (Docker & Airflow)
"""

import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from sqlalchemy import create_engine
import os

# ──────────────────────────────────────────────
# Configuration de la page
# ──────────────────────────────────────────────
st.set_page_config(
    page_title="Dashboard RFM — Segmentation Clients",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ──────────────────────────────────────────────
# Connexion à la base de données
# ──────────────────────────────────────────────
DB_HOST = os.getenv("DB_HOST", "postgres")
DB_PORT = os.getenv("DB_PORT", "5432")
DB_NAME = os.getenv("DB_NAME", "rfm_db")
DB_USER = os.getenv("DB_USER", "rfm_user")
DB_PASSWORD = os.getenv("DB_PASSWORD", "rfm_password")

DATABASE_URL = f"postgresql://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}"


@st.cache_data(ttl=300)
def load_rfm_data():
    """Charge les données RFM avec scores depuis PostgreSQL."""
    try:
        engine = create_engine(DATABASE_URL)
        query = """
            SELECT customer_id, recency, frequency, monetary, 
                   r_score, f_score, m_score, rfm_score, segment 
            FROM rfm_analysis
            ORDER BY monetary DESC
        """
        df = pd.read_sql(query, engine)

        # Conversion des types pour assurer la compatibilité
        df["r_score"] = df["r_score"].astype(int)
        df["f_score"] = df["f_score"].astype(int)
        df["m_score"] = df["m_score"].astype(int)
        df["monetary"] = df["monetary"].astype(float)

        engine.dispose()
        return df
    except Exception as e:
        st.error(f"Erreur chargement RFM: {e}")
        return pd.DataFrame()


@st.cache_data(ttl=300)
def load_raw_stats():
    """Charge les statistiques des données brutes."""
    try:
        engine = create_engine(DATABASE_URL)
        stats = {}
        stats["total_orders"] = pd.read_sql(
            "SELECT COUNT(DISTINCT invoice) AS cnt FROM raw_orders", engine
        )["cnt"].iloc[0]
        stats["total_customers"] = pd.read_sql(
            "SELECT COUNT(DISTINCT customer_id) AS cnt FROM raw_orders WHERE customer_id IS NOT NULL",
            engine,
        )["cnt"].iloc[0]
        stats["total_revenue"] = pd.read_sql(
            "SELECT SUM(price * quantity) AS total FROM raw_orders WHERE quantity > 0",
            engine,
        )["total"].iloc[0]
        stats["total_products"] = pd.read_sql(
            "SELECT COUNT(DISTINCT stock_code) AS cnt FROM raw_orders", engine
        )["cnt"].iloc[0]
        stats["top_countries"] = pd.read_sql(
            """SELECT country, COUNT(DISTINCT customer_id) AS nb_clients
               FROM raw_orders WHERE customer_id IS NOT NULL
               GROUP BY country ORDER BY nb_clients DESC LIMIT 10""",
            engine,
        )
        stats["monthly_revenue"] = pd.read_sql(
            """SELECT DATE_TRUNC('month', invoice_date) AS mois,
                      SUM(price * quantity) AS revenue
               FROM raw_orders WHERE quantity > 0
               GROUP BY mois ORDER BY mois""",
            engine,
        )
        engine.dispose()
        return stats
    except Exception as e:
        st.error(f"Erreur chargement stats: {e}")
        return {}


SEGMENT_COLORS = {
    "Champions": "#2ecc71",
    "Clients Fidèles": "#3498db",
    "Nouveaux Clients": "#9b59b6",
    "Clients Potentiels": "#f39c12",
    "À Risque": "#e74c3c",
    "Perdus": "#95a5a6",
    "À Réactiver": "#e67e22",
    "Moyens": "#1abc9c",
}


# ──────────────────────────────────────────────
# Chargement des données
# ──────────────────────────────────────────────
try:
    df_rfm = load_rfm_data()
    if df_rfm.empty:
        raise ValueError("Aucune donnée RFM trouvée")
    raw_stats = load_raw_stats()
    data_loaded = True
except Exception as e:
    data_loaded = False
    error_msg = str(e)

# ──────────────────────────────────────────────
# En-tête
# ──────────────────────────────────────────────
st.markdown(
    """
    <div style="text-align: center; padding: 1rem 0;">
        <h1 style="color: #2c3e50; margin-bottom: 0.2rem;">📊 Dashboard RFM</h1>
        <p style="color: #7f8c8d; font-size: 1.1rem;">Analyse de la Segmentation Clients — Online Retail II</p>
    </div>
    <hr style="border: 1px solid #ecf0f1;">
    """,
    unsafe_allow_html=True,
)

if not data_loaded:
    st.error(
        f"❌ Impossible de charger les données depuis PostgreSQL.\n\n**Erreur :** {error_msg}\n\n"
        "Assurez-vous que le DAG Airflow `rfm_pipeline` a été exécuté avec succès."
    )
    st.stop()

# ──────────────────────────────────────────────
# Validation des données
# ──────────────────────────────────────────────
required_cols = [
    "customer_id",
    "recency",
    "frequency",
    "monetary",
    "r_score",
    "f_score",
    "m_score",
    "rfm_score",
    "segment",
]
missing_cols = [col for col in required_cols if col not in df_rfm.columns]
if missing_cols:
    st.error(f"❌ Colonnes manquantes dans rfm_analysis: {missing_cols}")
    st.stop()

# ──────────────────────────────────────────────
# Sidebar / Filtres
# ──────────────────────────────────────────────
with st.sidebar:
    st.markdown(
        """
        <div style="text-align:center; padding: 0.5rem 0 1rem 0;">
            <span style="font-size: 1.6rem;">🎯</span>
            <h3 style="margin: 0.2rem 0 0 0;">Filtres</h3>
        </div>
        """,
        unsafe_allow_html=True,
    )

    # Segments via checkboxes individuels
    st.markdown("**Segments clients**")
    all_segments = sorted(df_rfm["segment"].unique())

    col_sel1, col_sel2 = st.columns(2)
    with col_sel1:
        select_all = st.button("Tout cocher", use_container_width=True)
    with col_sel2:
        deselect_all = st.button("Tout décocher", use_container_width=True)

    if select_all:
        for seg in all_segments:
            st.session_state[f"seg_{seg}"] = True
    if deselect_all:
        for seg in all_segments:
            st.session_state[f"seg_{seg}"] = False

    segments = []
    for seg in all_segments:
        emoji = {
            "Champions": "🏆",
            "Clients Fidèles": "💎",
            "Nouveaux Clients": "🌱",
            "Clients Potentiels": "📈",
            "À Risque": "⚠️",
            "Perdus": "💤",
            "À Réactiver": "🔄",
            "Moyens": "➖",
        }.get(seg, "•")
        checked = st.checkbox(
            f"{emoji} {seg}",
            value=st.session_state.get(f"seg_{seg}", True),
            key=f"seg_{seg}",
        )
        if checked:
            segments.append(seg)

    st.markdown("---")

    # Plages min/max avec number_input
    st.markdown("**Récence (jours)**")
    r_col1, r_col2 = st.columns(2)
    with r_col1:
        r_min = st.number_input(
            "Min",
            min_value=int(df_rfm["recency"].min()),
            max_value=int(df_rfm["recency"].max()),
            value=int(df_rfm["recency"].min()),
            key="r_min",
        )
    with r_col2:
        r_max = st.number_input(
            "Max",
            min_value=int(df_rfm["recency"].min()),
            max_value=int(df_rfm["recency"].max()),
            value=int(df_rfm["recency"].max()),
            key="r_max",
        )
    recency_range = (r_min, r_max)

    st.markdown("**Montant total (€)**")
    m_col1, m_col2 = st.columns(2)
    with m_col1:
        m_min = st.number_input(
            "Min ",
            min_value=float(df_rfm["monetary"].min()),
            max_value=float(df_rfm["monetary"].max()),
            value=float(df_rfm["monetary"].min()),
            step=100.0,
            format="%.0f",
            key="m_min",
        )
    with m_col2:
        m_max = st.number_input(
            "Max ",
            min_value=float(df_rfm["monetary"].min()),
            max_value=float(df_rfm["monetary"].max()),
            value=float(df_rfm["monetary"].max()),
            step=100.0,
            format="%.0f",
            key="m_max",
        )
    monetary_range = (m_min, m_max)

    st.markdown("---")
    st.markdown(
        """
        <div style="font-size: 0.82rem; color: #aaa; line-height: 1.5;">
            <b>R</b>ecency — Dernière commande<br>
            <b>F</b>requency — Nb de commandes<br>
            <b>M</b>onetary — Montant total<br><br>
            <i>Source : Online Retail II (UCI)</i>
        </div>
        """,
        unsafe_allow_html=True,
    )

# Application des filtres
df_filtered = df_rfm[
    (df_rfm["segment"].isin(segments))
    & (df_rfm["recency"].between(*recency_range))
    & (df_rfm["monetary"].between(*monetary_range))
]

# ══════════════════════════════════════════════
# TAB LAYOUT
# ══════════════════════════════════════════════
tab1, tab2, tab3, tab4 = st.tabs(
    ["📈 Vue d'ensemble", "🎯 Segmentation RFM", "🔍 Analyse détaillée", "📋 Données"]
)

# ──────────────────────────────────────────────
# TAB 1 : Vue d'ensemble
# ──────────────────────────────────────────────
with tab1:
    st.markdown("## Vue d'ensemble du Business")

    # KPIs principaux
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric("🧾 Commandes totales", f"{raw_stats['total_orders']:,}")
    with col2:
        st.metric("👥 Clients uniques", f"{raw_stats['total_customers']:,}")
    with col3:
        st.metric("💰 Revenu total", f"{raw_stats['total_revenue']:,.0f} €")
    with col4:
        st.metric("📦 Produits distincts", f"{raw_stats['total_products']:,}")

    st.markdown("---")

    col_left, col_right = st.columns(2)

    with col_left:
        st.markdown("### 📈 Évolution du Chiffre d'Affaires Mensuel")
        if "monthly_revenue" in raw_stats and not raw_stats["monthly_revenue"].empty:
            df_monthly = raw_stats["monthly_revenue"].copy()
            df_monthly["mois"] = pd.to_datetime(df_monthly["mois"])
            fig_revenue = px.area(
                df_monthly,
                x="mois",
                y="revenue",
                labels={"mois": "Mois", "revenue": "Revenu (€)"},
                color_discrete_sequence=["#3498db"],
            )
            fig_revenue.update_layout(
                plot_bgcolor="rgba(0,0,0,0)",
                paper_bgcolor="rgba(0,0,0,0)",
                xaxis=dict(showgrid=False),
                yaxis=dict(showgrid=True, gridcolor="#ecf0f1"),
                height=400,
            )
            st.plotly_chart(fig_revenue, use_container_width=True)
        else:
            st.info("📭 Pas de données de chiffre d'affaires")

    with col_right:
        st.markdown("### 🌍 Top 10 Pays par Nombre de Clients")
        if "top_countries" in raw_stats and not raw_stats["top_countries"].empty:
            df_countries = raw_stats["top_countries"].copy()
            fig_countries = px.bar(
                df_countries,
                x="nb_clients",
                y="country",
                orientation="h",
                labels={"nb_clients": "Nombre de clients", "country": "Pays"},
                color="nb_clients",
                color_continuous_scale="Blues",
            )
            fig_countries.update_layout(
                plot_bgcolor="rgba(0,0,0,0)",
                paper_bgcolor="rgba(0,0,0,0)",
                yaxis=dict(autorange="reversed"),
                coloraxis_showscale=False,
                height=400,
            )
            st.plotly_chart(fig_countries, use_container_width=True)
        else:
            st.info("📭 Pas de données par pays")

# ──────────────────────────────────────────────
# TAB 2 : Segmentation RFM
# ──────────────────────────────────────────────
with tab2:
    st.markdown("## Segmentation RFM des Clients")

    # KPIs segment
    col1, col2, col3 = st.columns(3)
    with col1:
        n_champions = len(df_filtered[df_filtered["segment"] == "Champions"])
        st.metric("🏆 Champions", f"{n_champions:,}")
    with col2:
        n_risk = len(df_filtered[df_filtered["segment"] == "À Risque"])
        st.metric("⚠️ À Risque", f"{n_risk:,}")
    with col3:
        n_lost = len(df_filtered[df_filtered["segment"] == "Perdus"])
        st.metric("❌ Perdus", f"{n_lost:,}")

    st.markdown("---")

    col_left, col_right = st.columns(2)

    with col_left:
        st.markdown("### 🍩 Répartition des Segments")
        if not df_filtered.empty:
            segment_counts = df_filtered["segment"].value_counts().reset_index()
            segment_counts.columns = ["segment", "count"]
            fig_pie = px.pie(
                segment_counts,
                values="count",
                names="segment",
                color="segment",
                color_discrete_map=SEGMENT_COLORS,
                hole=0.4,
            )
            fig_pie.update_traces(textposition="inside", textinfo="percent+label")
            fig_pie.update_layout(
                showlegend=False,
                plot_bgcolor="rgba(0,0,0,0)",
                paper_bgcolor="rgba(0,0,0,0)",
                height=450,
            )
            st.plotly_chart(fig_pie, use_container_width=True)
        else:
            st.info("📭 Pas de données")

    with col_right:
        st.markdown("### 📊 Nombre de Clients par Segment")
        if not df_filtered.empty:
            segment_counts = df_filtered["segment"].value_counts().reset_index()
            segment_counts.columns = ["segment", "count"]
            segment_counts_sorted = segment_counts.sort_values("count", ascending=True)
            fig_bar = px.bar(
                segment_counts_sorted,
                x="count",
                y="segment",
                orientation="h",
                color="segment",
                color_discrete_map=SEGMENT_COLORS,
                labels={"count": "Nombre de clients", "segment": "Segment"},
            )
            fig_bar.update_layout(
                showlegend=False,
                plot_bgcolor="rgba(0,0,0,0)",
                paper_bgcolor="rgba(0,0,0,0)",
                yaxis=dict(showgrid=False),
                xaxis=dict(showgrid=True, gridcolor="#ecf0f1"),
                height=450,
            )
            st.plotly_chart(fig_bar, use_container_width=True)
        else:
            st.info("📭 Pas de données")

    # Tableau récapitulatif des segments
    st.markdown("### 📋 Statistiques par Segment")
    if not df_filtered.empty:
        segment_stats = (
            df_filtered.groupby("segment")
            .agg(
                clients=("customer_id", "count"),
                recence_moy=("recency", "mean"),
                frequence_moy=("frequency", "mean"),
                montant_moy=("monetary", "mean"),
                montant_total=("monetary", "sum"),
            )
            .round(1)
            .sort_values("montant_total", ascending=False)
            .reset_index()
        )
        segment_stats.columns = [
            "Segment",
            "Clients",
            "Récence moy. (j)",
            "Fréquence moy.",
            "Panier moy. (€)",
            "Revenu total (€)",
        ]
        st.dataframe(segment_stats, use_container_width=True, hide_index=True)
    else:
        st.info("📭 Pas de données après filtrage")

# ──────────────────────────────────────────────
# TAB 3 : Analyse détaillée
# ──────────────────────────────────────────────
with tab3:
    st.markdown("## Analyse Détaillée RFM")

    col_left, col_right = st.columns(2)

    with col_left:
        st.markdown("### 🔵 Récence vs. Fréquence")
        if not df_filtered.empty:
            fig_rf = px.scatter(
                df_filtered,
                x="recency",
                y="frequency",
                color="segment",
                color_discrete_map=SEGMENT_COLORS,
                size="monetary",
                size_max=20,
                opacity=0.6,
                labels={
                    "recency": "Récence (jours)",
                    "frequency": "Fréquence",
                    "monetary": "Montant (€)",
                    "segment": "Segment",
                },
                hover_data=["customer_id", "monetary"],
            )
            fig_rf.update_layout(
                plot_bgcolor="rgba(0,0,0,0)",
                paper_bgcolor="rgba(0,0,0,0)",
                xaxis=dict(showgrid=True, gridcolor="#ecf0f1"),
                yaxis=dict(showgrid=True, gridcolor="#ecf0f1"),
                height=500,
            )
            st.plotly_chart(fig_rf, use_container_width=True)
        else:
            st.info("📭 Pas de données")

    with col_right:
        st.markdown("### 🟢 Fréquence vs. Montant")
        if not df_filtered.empty:
            fig_fm = px.scatter(
                df_filtered,
                x="frequency",
                y="monetary",
                color="segment",
                color_discrete_map=SEGMENT_COLORS,
                size="monetary",
                size_max=20,
                opacity=0.6,
                labels={
                    "frequency": "Fréquence",
                    "monetary": "Montant (€)",
                    "segment": "Segment",
                },
                hover_data=["customer_id", "recency"],
            )
            fig_fm.update_layout(
                plot_bgcolor="rgba(0,0,0,0)",
                paper_bgcolor="rgba(0,0,0,0)",
                xaxis=dict(showgrid=True, gridcolor="#ecf0f1"),
                yaxis=dict(showgrid=True, gridcolor="#ecf0f1"),
                height=500,
            )
            st.plotly_chart(fig_fm, use_container_width=True)
        else:
            st.info("📭 Pas de données")

    st.markdown("---")

    col_left2, col_right2 = st.columns(2)

    with col_left2:
        st.markdown("### 📊 Distribution de la Récence")
        if not df_filtered.empty:
            fig_hist_r = px.histogram(
                df_filtered,
                x="recency",
                nbins=50,
                color="segment",
                color_discrete_map=SEGMENT_COLORS,
                labels={"recency": "Récence (jours)", "count": "Nombre de clients"},
            )
            fig_hist_r.update_layout(
                plot_bgcolor="rgba(0,0,0,0)",
                paper_bgcolor="rgba(0,0,0,0)",
                xaxis=dict(showgrid=False),
                yaxis=dict(showgrid=True, gridcolor="#ecf0f1"),
                height=400,
                barmode="stack",
            )
            st.plotly_chart(fig_hist_r, use_container_width=True)
        else:
            st.info("📭 Pas de données")

    with col_right2:
        st.markdown("### 💰 Distribution du Montant")
        if not df_filtered.empty:
            fig_hist_m = px.histogram(
                df_filtered,
                x="monetary",
                nbins=50,
                color="segment",
                color_discrete_map=SEGMENT_COLORS,
                labels={"monetary": "Montant (€)", "count": "Nombre de clients"},
            )
            fig_hist_m.update_layout(
                plot_bgcolor="rgba(0,0,0,0)",
                paper_bgcolor="rgba(0,0,0,0)",
                xaxis=dict(showgrid=False),
                yaxis=dict(showgrid=True, gridcolor="#ecf0f1"),
                height=400,
                barmode="stack",
            )
            st.plotly_chart(fig_hist_m, use_container_width=True)
        else:
            st.info("📭 Pas de données")

    # Heatmap RFM
    st.markdown("### 🗺️ Heatmap des Scores RFM (Récence × Fréquence)")
    if not df_filtered.empty:
        heatmap_data = (
            df_filtered.groupby(["r_score", "f_score"], observed=True)
            .size()
            .reset_index(name="count")
            .pivot(index="r_score", columns="f_score", values="count")
            .fillna(0)
            .astype(int)
        )
        # Créer une heatmap cohérente (de 1 à 5)
        heatmap_full = pd.DataFrame(0, index=range(5, 0, -1), columns=range(1, 6))
        heatmap_full.update(heatmap_data)

        fig_heat = px.imshow(
            heatmap_full,
            labels=dict(x="Score Fréquence", y="Score Récence", color="Clients"),
            x=list(range(1, 6)),
            y=list(range(5, 0, -1)),
            color_continuous_scale="Blues",
            aspect="auto",
            text_auto=True,
        )
        fig_heat.update_layout(
            height=400,
            plot_bgcolor="rgba(0,0,0,0)",
            paper_bgcolor="rgba(0,0,0,0)",
        )
        st.plotly_chart(fig_heat, use_container_width=True)
    else:
        st.info("📭 Pas de données pour la heatmap")

# ──────────────────────────────────────────────
# TAB 4 : Données brutes
# ──────────────────────────────────────────────
with tab4:
    st.markdown("## 📋 Données RFM Détaillées")

    col1, col2 = st.columns(2)
    with col1:
        st.metric("Clients affichés (filtrés)", f"{len(df_filtered):,}")
    with col2:
        st.metric("Clients total", f"{len(df_rfm):,}")

    if not df_filtered.empty:
        # Formater les colonnes pour affichage
        df_display = df_filtered[
            [
                "customer_id",
                "recency",
                "frequency",
                "monetary",
                "r_score",
                "f_score",
                "m_score",
                "rfm_score",
                "segment",
            ]
        ].copy()

        df_display.columns = [
            "ID",
            "Récence (j)",
            "Fréquence",
            "Montant (€)",
            "R",
            "F",
            "M",
            "RFM",
            "Segment",
        ]
        df_display = df_display.sort_values("Montant (€)", ascending=False).reset_index(
            drop=True
        )

        st.dataframe(
            df_display,
            use_container_width=True,
            height=500,
            hide_index=False,
        )

        # Export CSV
        csv_export = df_display.to_csv(index=False).encode("utf-8")
        st.download_button(
            label="⬇️  Télécharger les données filtrées (CSV)",
            data=csv_export,
            file_name="rfm_segmentation.csv",
            mime="text/csv",
        )
    else:
        st.info("📭 Aucune donnée après filtrage")

# ──────────────────────────────────────────────
# Footer
# ──────────────────────────────────────────────
st.markdown("---")
st.markdown(
    """
    <div style="text-align: center; color: #95a5a6; font-size: 0.85rem;">
        Pipeline RFM — Docker & Airflow | Données : Online Retail II (UCI) | Simplon DE 2025
    </div>
    """,
    unsafe_allow_html=True,
)
