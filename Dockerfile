# Utiliser une image Python officielle légère
FROM python:3.9-slim

# Définir le répertoire de travail
WORKDIR /app

# Copier le fichier des dépendances
COPY requirements.txt .

# Installer les dépendances
RUN pip install --no-cache-dir -r requirements.txt

# Installer les données NLTK nécessaires (VADER et Punkt)
RUN python -m nltk.downloader vader_lexicon punkt

# Copier le reste du code de l'application
COPY . .

# Exposer le port 5000
EXPOSE 5000

# Commande de démarrage
CMD ["python", "app.py"]
