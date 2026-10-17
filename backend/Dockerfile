FROM python:3.10-slim

WORKDIR /app

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PYTHONPATH=/app

RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    libpq-dev \
    curl \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .

# Install CPU-only PyTorch without resolving its dependencies
# from the PyTorch index.
RUN pip install --no-cache-dir \
    --no-deps \
    torch==2.14.0 \
    --index-url https://download.pytorch.org/whl/cpu

# Install all normal project dependencies from PyPI.
# The CPU torch installation above already satisfies torch==2.14.0.
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

EXPOSE 8000

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
