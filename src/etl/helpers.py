"""
Module d'aide pour les imports - Support Docker et développement local
"""

import sys
import os


def setup_paths():
    """Configure les chemins Python pour importer config et etl"""

    # Chemins possibles pour config
    config_paths = [
        "/airflow/config",  # Docker
        os.path.join(os.path.dirname(__file__), "..", "config"),  # Depuis etl/
        os.path.join(os.path.dirname(__file__), "config"),  # Depuis racine
    ]

    # Chemins possibles pour etl
    etl_paths = [
        "/airflow/etl",  # Docker
        os.path.dirname(__file__),  # Répertoire courant
    ]

    # Ajouter les chemins
    for path in config_paths + etl_paths:
        if os.path.exists(path) and path not in sys.path:
            sys.path.insert(0, path)


# Exécuter au chargement du module
setup_paths()
