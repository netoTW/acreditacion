FROM node:22-alpine

WORKDIR /app

COPY package.json package-lock.json ./
RUN npm ci --omit=dev && npm install esbuild

COPY src ./src
COPY cliente ./cliente
COPY colyseus.js.d.ts* ./

# El bundle del cliente se construye acá: NUNCA se sirve node_modules/colyseus.js/dist,
# que está compilado contra Node y revienta en el navegador con "Buffer is not defined".
RUN npx esbuild colyseus.js --bundle --format=iife --global-name=Colyseus \
      --platform=browser --target=es2019 --minify \
      --outfile=cliente/vendor/colyseus.js

EXPOSE 2567
CMD ["node", "src/index.js"]
