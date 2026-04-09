# ──────────────────────────────────────────────
# TAB 5 : Advanced Analytics
# ──────────────────────────────────────────────
with tab5:
    st.markdown("## 🚀 Advanced Analytics — 4 Modules Avancés")
    st.markdown("Analyses approfondies: Produits, Churn, Géographie, CLV Forecast")
    st.markdown("---")

    # Sub-tabs pour chaque module
    sub_tab1, sub_tab2, sub_tab3, sub_tab4 = st.tabs(
        ["🏆 Produits RFM", "🚨 Churn Risk", "🌍 Géographie", "💰 CLV Forecast"]
    )

    # ─────────────────────────────────────────────
    # SUB-TAB 1 : Product RFM
    # ─────────────────────────────────────────────
    with sub_tab1:
        st.markdown("### Analyse RFM au Niveau Produit")
        df_products = load_product_rfm()

        if not df_products.empty:
            col1, col2, col3 = st.columns(3)
            with col1:
                n_stars = len(df_products[df_products["performance"] == "Star"])
                st.metric("⭐ Produits Stars", f"{n_stars}")
            with col2:
                n_orphans = len(df_products[df_products["performance"] == "Orphan"])
                st.metric("💀 Produits Orphelins", f"{n_orphans}")
            with col3:
                total_products = len(df_products)
                st.metric("📦 Total Produits Analysés", f"{total_products}")

            st.markdown("---")

            col_left, col_right = st.columns(2)

            with col_left:
                st.markdown("### 🎯 Distribution par Performance")
                perf_counts = df_products["performance"].value_counts().reset_index()
                perf_counts.columns = ["performance", "count"]
                fig_perf = px.pie(
                    perf_counts,
                    values="count",
                    names="performance",
                    color_discrete_sequence=[
                        "#2ecc71",
                        "#3498db",
                        "#f39c12",
                        "#95a5a6",
                    ],
                    hole=0.4,
                )
                fig_perf.update_layout(height=400, paper_bgcolor="rgba(0,0,0,0)")
                st.plotly_chart(fig_perf, use_container_width=True)

            with col_right:
                st.markdown("### 💰 Top 10 Produits par Revenue")
                df_top_products = df_products.nlargest(10, "monetary")
                fig_prod_revenue = px.bar(
                    df_top_products,
                    x="monetary",
                    y="stock_code",
                    orientation="h",
                    color="performance",
                    color_discrete_map={
                        "Star": "#2ecc71",
                        "Strong": "#3498db",
                        "Stable": "#f39c12",
                        "Orphan": "#95a5a6",
                    },
                    labels={"monetary": "Revenue (€)", "stock_code": "Product"},
                )
                fig_prod_revenue.update_layout(
                    height=400,
                    showlegend=False,
                    paper_bgcolor="rgba(0,0,0,0)",
                )
                st.plotly_chart(fig_prod_revenue, use_container_width=True)

            st.markdown("---")
            st.markdown("### 📊 Tous les Produits Analysés")
            st.dataframe(
                df_products[
                    [
                        "stock_code",
                        "product_name",
                        "performance",
                        "total_customers",
                        "monetary",
                        "r_score",
                        "f_score",
                        "m_score",
                    ]
                ],
                use_container_width=True,
                height=400,
            )
        else:
            st.info("📭 Pas de données produits. Lancez le DAG pour générer l'analyse.")

    # ─────────────────────────────────────────────
    # SUB-TAB 2 : Churn Prediction
    # ─────────────────────────────────────────────
    with sub_tab2:
        st.markdown("### Prédiction de Churn — Risque de Désabonnement")
        df_churn = load_churn_data()

        if not df_churn.empty:
            col1, col2, col3, col4 = st.columns(4)
            with col1:
                n_high = len(df_churn[df_churn["churn_score"].astype(float) >= 80])
                st.metric("🔴 Haut Risque", f"{n_high}")
            with col2:
                n_medium = len(
                    df_churn[
                        (df_churn["churn_score"].astype(float) >= 60)
                        & (df_churn["churn_score"].astype(float) < 80)
                    ]
                )
                st.metric("🟠 Risque Moyen", f"{n_medium}")
            with col3:
                n_low = len(
                    df_churn[
                        (df_churn["churn_score"].astype(float) >= 40)
                        & (df_churn["churn_score"].astype(float) < 60)
                    ]
                )
                st.metric("🟡 Faible Risque", f"{n_low}")
            with col4:
                n_vlow = len(df_churn[df_churn["churn_score"].astype(float) < 40])
                st.metric("🟢 Très Faible", f"{n_vlow}")

            st.markdown("---")
            st.markdown("### 🎯 Score de Churn Distribution")

            fig_churn_hist = px.histogram(
                df_churn,
                x="churn_score",
                nbins=30,
                color_discrete_sequence=["#e74c3c"],
                labels={"churn_score": "Churn Score (0-100)"},
            )
            fig_churn_hist.update_layout(height=400, paper_bgcolor="rgba(0,0,0,0)")
            st.plotly_chart(fig_churn_hist, use_container_width=True)

            st.markdown("---")
            st.markdown("### 🚨 Clients à Haut Risque (Actionables)")
            df_high_risk = df_churn[df_churn["churn_score"].astype(float) >= 80].head(
                50
            )
            st.dataframe(
                df_high_risk[
                    [
                        "customer_id",
                        "churn_score",
                        "recency",
                        "frequency",
                        "recommendation",
                    ]
                ],
                use_container_width=True,
                height=400,
            )
            if len(df_high_risk) > 0:
                st.download_button(
                    "⬇️ Télécharger liste Haut Risque",
                    df_high_risk.to_csv(index=False),
                    "churn_high_risk.csv",
                    "text/csv",
                )
        else:
            st.info("📭 Pas de données churn. Lancez le DAG pour générer l'analyse.")

    # ─────────────────────────────────────────────
    # SUB-TAB 3 : Geographic Analysis
    # ─────────────────────────────────────────────
    with sub_tab3:
        st.markdown("### Analyse Géographique — Opportunités d'Expansion")
        df_geo = load_geographic_data()

        if not df_geo.empty:
            col1, col2, col3 = st.columns(3)
            with col1:
                n_established = len(
                    df_geo[
                        df_geo["market_growth_potential"].str.contains("Established")
                    ]
                )
                st.metric("🟢 Marchés Établis", f"{n_established}")
            with col2:
                n_growing = len(
                    df_geo[df_geo["market_growth_potential"].str.contains("Growing")]
                )
                st.metric("📈 En Croissance", f"{n_growing}")
            with col3:
                n_emerging = len(
                    df_geo[df_geo["market_growth_potential"].str.contains("Emerging")]
                )
                st.metric("🚀 Émergents", f"{n_emerging}")

            st.markdown("---")
            st.markdown("### 🌍 Top 10 Pays par Potentiel")

            fig_geo_bubble = px.scatter(
                df_geo.head(10),
                x="total_customers",
                y="total_revenue",
                size="avg_customer_value",
                hover_name="country",
                color="market_growth_potential",
                color_discrete_map={
                    "🟢 Established Leader": "#2ecc71",
                    "🟠 Declining": "#e74c3c",
                    "🟡 Growing Opportunity": "#f39c12",
                    "🔴 Emerging Market": "#e67e22",
                },
                labels={"total_customers": "Clients", "total_revenue": "Revenue (€)"},
            )
            fig_geo_bubble.update_layout(height=400, paper_bgcolor="rgba(0,0,0,0)")
            st.plotly_chart(fig_geo_bubble, use_container_width=True)

            st.markdown("---")
            st.markdown("### 📊 Tous les Pays Analysés")
            st.dataframe(
                df_geo[
                    [
                        "priority_rank",
                        "country",
                        "total_customers",
                        "total_revenue",
                        "avg_customer_value",
                        "market_growth_potential",
                    ]
                ],
                use_container_width=True,
                height=400,
            )
        else:
            st.info(
                "📭 Pas de données géographiques. Lancez le DAG pour générer l'analyse."
            )

    # ─────────────────────────────────────────────
    # SUB-TAB 4 : CLV Forecast
    # ─────────────────────────────────────────────
    with sub_tab4:
        st.markdown("### Prévision CLV — Valeur à Vie du Client (12-24 mois)")
        df_clv = load_clv_data()

        if not df_clv.empty:
            # Calculs agrégés
            total_clv_12 = df_clv["clv_12months"].sum()
            total_clv_24 = df_clv["clv_24months"].sum()
            avg_clv_12 = df_clv["clv_12months"].mean()

            col1, col2, col3 = st.columns(3)
            with col1:
                st.metric(
                    "💰 Revenue Prévu 12M",
                    f"€{total_clv_12:,.0f}",
                    delta=f"Avg: €{avg_clv_12:,.0f}/client",
                )
            with col2:
                st.metric(
                    "💰 Revenue Prévu 24M",
                    f"€{total_clv_24:,.0f}",
                )
            with col3:
                confidence_high = len(
                    df_clv[df_clv["forecast_confidence"] == "🟢 High"]
                )
                st.metric("✅ Haute Confiance", f"{confidence_high}")

            st.markdown("---")
            st.markdown("### 📊 CLV par Segment")

            df_clv_segment = (
                df_clv.groupby("segment")
                .agg(
                    {
                        "customer_id": "count",
                        "clv_12months": "sum",
                        "clv_24months": "sum",
                    }
                )
                .reset_index()
            )
            df_clv_segment.columns = [
                "segment",
                "customers",
                "clv_12m_total",
                "clv_24m_total",
            ]

            fig_clv_segment = px.bar(
                df_clv_segment,
                x="segment",
                y=["clv_12m_total", "clv_24m_total"],
                barmode="group",
                labels={"x": "Segment", "value": "Revenue Prévu (€)"},
                color_discrete_map={
                    "clv_12m_total": "#3498db",
                    "clv_24m_total": "#2ecc71",
                },
            )
            fig_clv_segment.update_layout(height=400, paper_bgcolor="rgba(0,0,0,0)")
            st.plotly_chart(fig_clv_segment, use_container_width=True)

            st.markdown("---")
            st.markdown("### 🏆 Top 30 Clients par CLV 24 mois")
            df_top_clv = df_clv.nlargest(30, "clv_24months")
            st.dataframe(
                df_top_clv[
                    [
                        "customer_id",
                        "segment",
                        "historical_value",
                        "clv_12months",
                        "clv_24months",
                        "forecast_confidence",
                    ]
                ],
                use_container_width=True,
                height=400,
            )
            st.download_button(
                "⬇️ Télécharger Top CLV",
                df_top_clv.to_csv(index=False),
                "clv_forecast_top.csv",
                "text/csv",
            )
        else:
            st.info("📭 Pas de données CLV. Lancez le DAG pour générer l'analyse.")
