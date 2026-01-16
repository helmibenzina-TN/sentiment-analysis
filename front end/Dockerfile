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

# Copier le template Nginx
COPY nginx.conf.template /etc/nginx/templates/default.conf.template

# Copier et configurer le script d'entrée personnalisé
COPY entrypoint.sh /docker-entrypoint.sh
RUN chmod +x /docker-entrypoint.sh

# Exposer le port 80
EXPOSE 80

ENTRYPOINT ["/docker-entrypoint.sh"]
CMD ["nginx", "-g", "daemon off;"]
