FROM python:3.12-slim

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1
ENV PORT=8080

WORKDIR /app

RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy backend (including canon.db)
COPY backend ./backend

# Re-copy canon.db explicitly — this layer invalidates when canon.db changes,
# overwriting the cached version from COPY backend ./backend
COPY backend/data/canon.db ./backend/data/canon.db

EXPOSE 8080

CMD ["uvicorn", "backend.api.main:app", "--host", "0.0.0.0", "--port", "8080"]