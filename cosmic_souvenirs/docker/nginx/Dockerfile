# docker/nginx/Dockerfile
FROM nginx:alpine

# Копируем конфиг nginx
COPY nginx.conf /etc/nginx/nginx.conf

# Копируем статические файлы
COPY --from=builder /app/staticfiles /static
COPY --from=builder /app/media /media