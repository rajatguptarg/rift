# ── Build stage ─────────────────────────────────────────────────────────────
FROM node:20-alpine AS build

WORKDIR /app

COPY package.json package-lock.json* ./
RUN npm ci

COPY . .

# API URL is baked in at build time; override via build-arg for non-local envs
ARG VITE_API_BASE_URL=http://localhost:8000
ENV VITE_API_BASE_URL=$VITE_API_BASE_URL

RUN npm run build

# ── Serve stage ──────────────────────────────────────────────────────────────
FROM nginx:1.27-alpine AS serve

COPY --from=build /app/dist /usr/share/nginx/html

# SPA fallback: all routes → index.html
COPY nginx.conf /etc/nginx/conf.d/default.conf

EXPOSE 80
CMD ["nginx", "-g", "daemon off;"]
