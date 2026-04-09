"""
Test du DAG - Valider que les tâches peuvent être importées
"""

import sys
import os

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

try:
    print("🔍 Teste l'import du DAG...\n")

    # Importer le DAG
    from src.dags.rfm_pipeline_dag import dag

    # Valider le DAG
    dag.validate()

    print("✅ DAG valide !")
    print(f"   DAG ID : {dag.dag_id}")
    print(f"   Tâches : {len(dag.tasks)}")
    print(f"\n   Tâches du pipeline :")
    for task in dag.tasks:
        print(f"      - {task.task_id}")

    print("\n" + "=" * 50)
    print("✅ Le DAG est prêt pour Airflow !")
    print("=" * 50)

except Exception as e:
    print(f"❌ Erreur : {e}")
    import traceback

    traceback.print_exc()
    sys.exit(1)
