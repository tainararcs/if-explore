# Imagem de desenvolvimento da interface (usada pelo compose.yaml na raiz).
FROM node:24.22.0-slim

WORKDIR /app

COPY package.json package-lock.json ./
RUN npm ci

COPY . .

EXPOSE 5173

CMD ["npm", "run", "dev", "--", "--host", "0.0.0.0"]
