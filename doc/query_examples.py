#!/usr/bin/env python3
"""
SQL Queries Examples — Advanced Analytics
Copy-paste ready queries pour explorer les données des modules Priority 3
"""

QUERIES = {
    "PRODUCT_RFM": {
        "description": "Analyse RFM au niveau produit",
        "queries": {
            "Top 10 Produits Stars": """
SELECT 
    stock_code,
    product_name,
    performance,
    total_customers,
    total_quantity,
    monetary,
    r_score, f_score, m_score
FROM product_rfm
WHERE performance = 'Star'
ORDER BY monetary DESC
LIMIT 10;
            """,
            "Produits Orphelins": """
SELECT 
    stock_code,
    product_name,
    performance,
    total_customers,
    monetary,
    (SELECT COUNT(*) FROM raw_orders WHERE stock_code = product_rfm.stock_code) as total_sales
FROM product_rfm
WHERE performance = 'Orphan'
ORDER BY total_customers ASC
LIMIT 20;
            """,
            "Performance Distribution": """
SELECT 
    performance,
    COUNT(*) as product_count,
    AVG(monetary) as avg_revenue,
    SUM(monetary) as total_revenue,
    AVG(total_customers) as avg_customers
FROM product_rfm
GROUP BY performance
ORDER BY total_revenue DESC;
            """,
            "Top 20 Produits par Revenue": """
SELECT 
    rank() OVER (ORDER BY monetary DESC) as rank,
    stock_code,
    product_name,
    monetary,
    total_customers,
    performance
FROM product_rfm
LIMIT 20;
            """,
        },
    },
    "CHURN_PREDICTION": {
        "description": "Prédiction de désabonnement clients",
        "queries": {
            "Clients à Haut Risque (Actionable)": """
SELECT 
    customer_id,
    churn_score,
    churn_risk,
    recency,
    frequency,
    recommendation
FROM churn_risk
WHERE churn_score >= 80
ORDER BY churn_score DESC
LIMIT 50;
            """,
            "Churn Risk Distribution": """
SELECT 
    churn_risk,
    COUNT(*) as customer_count,
    ROUND(AVG(churn_score), 1) as avg_score,
    MIN(churn_score) as min_score,
    MAX(churn_score) as max_score
FROM churn_risk
GROUP BY churn_risk
ORDER BY customer_count DESC;
            """,
            "Recommendation Breakdown": """
SELECT 
    recommendation,
    COUNT(*) as customer_count,
    ROUND(AVG(churn_score), 1) as avg_score
FROM churn_risk
GROUP BY recommendation
ORDER BY customer_count DESC;
            """,
            "Long-Term Inactive (Prospérité Low)": """
SELECT 
    customer_id,
    recency,
    frequency,
    months_active,
    purchase_frequency_per_month,
    churn_score
FROM churn_risk
WHERE recency > 180 AND frequency < 5
ORDER BY recency DESC
LIMIT 30;
            """,
            "Medium Risk Engagement Targets": """
SELECT 
    customer_id,
    churn_score,
    recency,
    frequency,
    recommendation
FROM churn_risk
WHERE churn_score BETWEEN 60 AND 79
ORDER BY churn_score DESC
LIMIT 100;
            """,
        },
    },
    "GEOGRAPHIC_ANALYSIS": {
        "description": "Analyse géographique et opportunités d'expansion",
        "queries": {
            "Top 5 Pays par Revenue": """
SELECT 
    priority_rank,
    country,
    total_customers,
    total_orders,
    total_revenue,
    avg_order_value,
    avg_customer_value,
    market_growth_potential
FROM geographic_analysis
ORDER BY priority_rank
LIMIT 5;
            """,
            "Opportunités de Croissance": """
SELECT 
    priority_rank,
    country,
    total_customers,
    total_revenue,
    market_growth_potential,
    recency_avg,
    frequency_avg,
    monetary_avg
FROM geographic_analysis
WHERE market_growth_potential IN ('Growing Opportunity', 'Emerging Market')
ORDER BY total_revenue DESC;
            """,
            "Marchés en Déclin": """
SELECT 
    country,
    total_customers,
    total_revenue,
    market_growth_potential,
    recency_avg as days_since_last_order
FROM geographic_analysis
WHERE market_growth_potential = 'Declining'
ORDER BY total_revenue DESC;
            """,
            "Tous les Pays (Classés)": """
SELECT 
    priority_rank,
    country,
    total_customers as cust_count,
    total_orders as orders,
    ROUND(total_revenue::numeric, 2) as revenue,
    ROUND(avg_customer_value::numeric, 2) as avg_cust_value,
    market_growth_potential
FROM geographic_analysis
ORDER BY priority_rank;
            """,
            "Benchmark par Région": """
SELECT 
    market_growth_potential,
    COUNT(*) as country_count,
    ROUND(AVG(total_customers)::numeric, 0) as avg_customers,
    ROUND(AVG(total_revenue)::numeric, 0) as avg_revenue,
    ROUND(AVG(avg_customer_value)::numeric, 2) as avg_customer_value
FROM geographic_analysis
GROUP BY market_growth_potential
ORDER BY avg_revenue DESC;
            """,
        },
    },
    "CLV_FORECAST": {
        "description": "Prévision de la valeur à vie client",
        "queries": {
            "Top 20 Clients par CLV 24 mois": """
SELECT 
    customer_id,
    segment,
    historical_value,
    avg_monthly_value,
    clv_12months,
    clv_24months,
    growth_rate,
    forecast_confidence
FROM clv_forecast
ORDER BY clv_24months DESC
LIMIT 20;
            """,
            "CLV par Segment": """
SELECT 
    segment,
    COUNT(*) as customer_count,
    ROUND(AVG(historical_value)::numeric, 2) as avg_historical,
    ROUND(AVG(clv_12months)::numeric, 2) as avg_12m,
    ROUND(AVG(clv_24months)::numeric, 2) as avg_24m,
    ROUND(SUM(clv_24months)::numeric, 0) as total_24m_forecast,
    ROUND(AVG(growth_rate)::numeric, 2) as avg_growth
FROM clv_forecast
GROUP BY segment
ORDER BY total_24m_forecast DESC;
            """,
            "High Confidence Forecasts (Best Bets)": """
SELECT 
    customer_id,
    segment,
    crust_24months,
    forecast_confidence,
    growth_rate
FROM clv_forecast
WHERE forecast_confidence = '🟢 High'
ORDER BY clv_24months DESC
LIMIT 50;
            """,
            "Forecast vs Actual (Validation)": """
SELECT 
    c.customer_id,
    c.segment,
    r.monetary as historical_actual,
    c.clv_12months as forecast_12m,
    c.clv_24months as forecast_24m,
    ROUND((c.clv_12months / NULLIF(r.monetary, 0))::numeric, 2) as growth_multiplier
FROM clv_forecast c
JOIN rfm_analysis r ON c.customer_id = r.customer_id
WHERE r.monetary > 0
ORDER BY growth_multiplier DESC
LIMIT 30;
            """,
            "Champions Premium Segment (Invest)": """
SELECT 
    customer_id,
    clv_24months,
    growth_rate,
    forecast_confidence
FROM clv_forecast
WHERE segment = 'Champions' AND forecast_confidence = '🟢 High'
ORDER BY clv_24months DESC
LIMIT 30;
            """,
            "Total Forecasted Revenue (12 & 24 months)": """
SELECT 
    SUM(clv_12months)::numeric(15, 2) as total_revenue_12m,
    SUM(clv_24months)::numeric(15, 2) as total_revenue_24m,
    COUNT(*) as total_customers,
    (SUM(clv_24months) / COUNT(*))::numeric(10, 2) as avg_clv_per_customer
FROM clv_forecast;
            """,
        },
    },
}


def display_all_queries():
    """Display all queries organized by module"""
    for module, data in QUERIES.items():
        print(f"\n{'=' * 80}")
        print(f"📊 {module}")
        print(f"   {data['description']}")
        print(f"{'=' * 80}\n")

        for query_name, query in data["queries"].items():
            print(f"🔍 {query_name}")
            print("-" * 80)
            print(query.strip())
            print()


def get_query_by_module(module_name: str):
    """Get specific queries by module"""
    if module_name in QUERIES:
        return QUERIES[module_name]
    else:
        print(f"❌ Module '{module_name}' not found")
        print(f"Available modules: {list(QUERIES.keys())}")


if __name__ == "__main__":
    import sys

    if len(sys.argv) > 1:
        module = sys.argv[1].upper()
        queries = get_query_by_module(module)
        if queries:
            print(f"\n📊 {module}: {queries['description']}")
            for name, query in queries["queries"].items():
                print(f"\n🔍 {name}")
                print("-" * 80)
                print(query.strip())
    else:
        display_all_queries()

    print("\n" + "=" * 80)
    print("💡 USAGE:")
    print("   python query_examples.py                 # Show all queries")
    print("   python query_examples.py PRODUCT_RFM     # Show product queries")
    print("   python query_examples.py CHURN_PREDICTION # Show churn queries")
    print("=" * 80)
