# Étape 1 : Build Angular
FROM node:20 as build-step

WORKDIR /app

COPY package.json package-lock.json ./
RUN npm install

COPY . .
RUN npm run build -- --configuration production

# Étape 2 : Serveur Nginx
FROM nginx:alpine

# Copier le build depuis l'étape précédente
# Note: Vérifiez bien le nom du dossier dans dist/ (ici 'sentiment-analysis')
COPY --from=build-step /app/dist/sentiment-analysis/browser /usr/share/nginx/html

# Copier le template Nginx dans un dossier de travail (pas dans /etc/nginx/templates pour éviter l'auto-processing)
COPY nginx.conf.template /app/nginx.conf.template

# Exposer le port 80
EXPOSE 80

# Commande de démarrage explicite :
# 1. Remplace uniquement ${BACKEND_URL}
# 2. Écrit le fichier de conf final
# 3. Lance Nginx
CMD ["/bin/sh", "-c", "envsubst '${BACKEND_URL}' < /app/nginx.conf.template > /etc/nginx/conf.d/default.conf && exec nginx -g 'daemon off;'"]
