# syntax=docker/dockerfile:1

# ---- Build aşaması: Vite üretim derlemesi ----
FROM node:22-alpine AS build
WORKDIR /app

# Bağımlılıkları önce kur (katman önbelleği: manifest değişmedikçe yeniden kurulmaz)
COPY package.json package-lock.json ./
RUN npm ci

# Backend adresi Vite tarafından DERLEME anında gömülür (import.meta.env.VITE_API_URL);
# çalışma anında değiştirilemez. Farklı ortam = farklı build-arg.
ARG VITE_API_URL=http://localhost:8000
ENV VITE_API_URL=$VITE_API_URL

COPY . .
RUN npm run build

# ---- Servis aşaması: statik build'i nginx ile sun ----
FROM nginx:alpine AS serve
COPY nginx.conf /etc/nginx/conf.d/default.conf
COPY --from=build /app/dist /usr/share/nginx/html
EXPOSE 80
# nginx:alpine varsayılan komutu nginx'i ön planda çalıştırır (CMD gerekmez)
