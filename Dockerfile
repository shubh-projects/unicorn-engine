FROM python:3.10-slim

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential libssl-dev libffi-dev python3-dev libpq-dev \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir \
    cryptography==42.0.5 \
    pyopenssl==24.0.0 \
    oauth2client==4.1.3 \
    google-api-python-client \
    pandas \
    numpy \
    websockets \
    redis \
    fastapi \
    uvicorn \
    python-multipart \
    dhanhq \
    psycopg2-binary

COPY . /app

CMD ["python", "main.py"]
