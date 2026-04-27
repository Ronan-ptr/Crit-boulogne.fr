# ============================================================
# Image de base compatible ARM (Raspberry Pi)
# ============================================================
FROM python:3.11-slim

# Répertoire de travail dans le conteneur
WORKDIR /app

# ============================================================
# Installation des dépendances système
# ============================================================
RUN apt-get update && apt-get install -y \
    gcc \
    && rm -rf /var/lib/apt/lists/*

# ============================================================
# Installation des dépendances Python
# On copie UNIQUEMENT requirements.txt en premier
# → Si le code change mais pas les dépendances,
#   Docker réutilise le cache → build beaucoup plus rapide
# ============================================================
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# ============================================================
# Copie du code source
# ============================================================
COPY . .

# ============================================================
# Variables d'environnement internes au conteneur
# ============================================================
ENV STREAMLIT_SERVER_PORT=8501
ENV STREAMLIT_SERVER_ADDRESS=0.0.0.0
ENV STREAMLIT_SERVER_HEADLESS=true
ENV DATA_PATH=/app/data

# Port exposé par le conteneur
EXPOSE 8501

# ============================================================
# Commande de démarrage
# ============================================================
CMD ["streamlit", "run", "app.py", "--server.port=8501", "--server.address=0.0.0.0"]
