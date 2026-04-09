"""
Module d'aide pour les imports - Support Docker et développement local
Copie dans analysis/ pour importer config et etl/analysis modules
"""

import sys
import os


def setup_paths():
    """Configure les chemins Python pour importer config, etl et analysis"""

    # Chemins possibles pour config
    config_paths = [
        "/airflow/config",  # Docker
        os.path.join(os.path.dirname(__file__), "..", "config"),  # Depuis analysis/
        os.path.join(os.path.dirname(__file__), "config"),  # Depuis racine
    ]

    # Chemins possibles pour etl et analysis
    module_paths = [
        "/airflow/etl",  # Docker - ETL core scripts
        "/airflow/analysis",  # Docker - Advanced analytics scripts
        os.path.dirname(__file__),  # Répertoire courant (analysis/)
        os.path.join(os.path.dirname(__file__), "..", "etl"),  # etl/ sibling
    ]

    # Ajouter les chemins
    for path in config_paths + module_paths:
        if os.path.exists(path) and path not in sys.path:
            sys.path.insert(0, path)


# Exécuter au chargement du module
setup_paths()
