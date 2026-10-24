FROM python:3.12-slim
ENV PYTHONDONTWRITEBYTECODE=1 PYTHONUNBUFFERED=1 PIP_NO_CACHE_DIR=1
WORKDIR /app
COPY bundle.b64 /tmp/bundle.b64
RUN base64 -d /tmp/bundle.b64 | tar -xJ -C /app \
    && rm /tmp/bundle.b64 \
    && pip install --no-cache-dir -r /app/requirements.txt
EXPOSE 10000
CMD ["sh", "-c", "gunicorn app:app --workers 1 --threads 4 --timeout 180 --bind 0.0.0.0:${PORT:-10000}"]