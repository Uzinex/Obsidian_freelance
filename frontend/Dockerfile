# syntax=docker/dockerfile:1.6
FROM node:20-alpine AS deps
WORKDIR /app
COPY package.json package-lock.json ./
RUN npm ci

FROM deps AS build
COPY . .
RUN npm run build

FROM caddy:2-alpine AS runtime
WORKDIR /srv
COPY --from=build /app/dist ./
COPY infra/docker/caddy/Caddyfile /etc/caddy/Caddyfile
RUN addgroup -S app && adduser -S app -G app && chown -R app:app /srv
USER app
EXPOSE 4173
HEALTHCHECK --interval=30s --timeout=3s CMD wget -qO- http://127.0.0.1:4173/healthz || exit 1
CMD ["caddy", "run", "--config", "/etc/caddy/Caddyfile"]
