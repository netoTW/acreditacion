FROM node:22-alpine AS build
WORKDIR /app
COPY package.json package-lock.json ./
RUN npm ci
COPY tsconfig.json vite.config.ts index.html ./
COPY src ./src
# La API se llama por ruta relativa: mismo origen que la página, así que la
# imagen sirve igual en localhost, en la red local o detrás de un túnel público
# sin volver a compilar. Quien resuelve /api es nginx, no el navegador.
ARG VITE_API=/api
ENV VITE_API=$VITE_API
RUN npm run build

FROM nginx:alpine
COPY nginx.conf /etc/nginx/conf.d/default.conf
COPY --from=build /app/dist /usr/share/nginx/html
EXPOSE 5180
