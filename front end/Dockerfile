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

# Copier la configuration Nginx personnalisée
COPY nginx.conf /etc/nginx/conf.d/default.conf

# Exposer le port 80
EXPOSE 80

CMD ["nginx", "-g", "daemon off;"]
