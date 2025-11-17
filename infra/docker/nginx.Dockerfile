# syntax=docker/dockerfile:1.6
FROM nginx:1.25-alpine
RUN addgroup -S app && adduser -S app -G app
COPY infra/docker/nginx/nginx.conf /etc/nginx/nginx.conf
RUN chown -R app:app /var/cache/nginx /var/run && chmod 755 /var/cache/nginx
USER app
EXPOSE 8080
HEALTHCHECK --interval=30s --timeout=3s CMD wget -qO- http://127.0.0.1:8080/healthz || exit 1
CMD ["nginx", "-g", "daemon off;"]
