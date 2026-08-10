FROM node:22-alpine AS build
WORKDIR /app
COPY package.json package-lock.json ./
RUN npm ci
COPY tsconfig.json vite.config.ts index.html ./
COPY src ./src
# La URL de la API la resuelve el NAVEGADOR del director, no el contenedor:
# por eso apunta a localhost del host, no al nombre del servicio.
ARG VITE_API=http://localhost:8010
ENV VITE_API=$VITE_API
RUN npm run build

FROM node:22-alpine
WORKDIR /app
RUN npm install -g serve@14
COPY --from=build /app/dist ./dist
EXPOSE 5180
CMD ["serve", "-s", "dist", "-l", "5180"]
