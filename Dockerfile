# Build stage
FROM python:3.14-alpine3.23 AS builder
ENV PYTHONDONTWRITEBYTECODE=1 PYTHONUNBUFFERED=1
WORKDIR /srv
RUN apk add --no-cache gcc musl-dev libffi-dev openssl-dev postgresql-dev
COPY requirements.txt .
RUN pip install --no-cache-dir --prefix=/install -r requirements.txt

# Runtime stage
FROM python:3.14-alpine3.23
ENV PYTHONDONTWRITEBYTECODE=1 PYTHONUNBUFFERED=1
WORKDIR /srv
RUN addgroup -S zttato && adduser -S -G zttato -h /srv zttato \
    && mkdir -p /srv/data /srv/media && chown -R zttato:zttato /srv \
    && pip uninstall -y pip setuptools ensurepip 2>/dev/null || true
COPY --from=builder /install /usr/local
COPY --chown=zttato:zttato app/ ./app/
COPY --chown=zttato:zttato web/ ./web/
USER zttato
EXPOSE 8000
HEALTHCHECK --interval=30s --timeout=5s --start-period=10s CMD python -c "import urllib.request; urllib.request.urlopen('http://127.0.0.1:8000/health/live',timeout=3)"
CMD ["uvicorn","app.main:create_app","--factory","--host","0.0.0.0","--port","8000","--proxy-headers","--forwarded-allow-ips","127.0.0.1"]