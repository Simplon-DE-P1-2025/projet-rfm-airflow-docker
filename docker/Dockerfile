FROM apache/airflow:2.8.1-python3.11

# Installer les dépendances système
USER root
RUN apt-get update && apt-get install -y \
    postgresql-client \
    && rm -rf /var/lib/apt/lists/*

# Revenir à l'utilisateur airflow
USER airflow

# Copier les requirements
COPY requirements.txt /tmp/requirements.txt
RUN pip install --no-cache-dir -r /tmp/requirements.txt
