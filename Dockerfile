FROM python:3.11-slim
RUN apt-get update && apt-get install -y \
    chromium \
    chromium-driver \
    libnss3 \
    libatk-bridge2.0-0 \
    libdrm2 \
    libxkbcommon0 \
    libgbm1 \
    libasound2 \
    && rm -rf /var/lib/apt/lists/*
RUN useradd -m -u 1000 appuser
WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt \
    && playwright install --with-deps chromium
COPY . .
RUN mkdir -p logs && chown -R appuser:appuser /app/logs && chmod -R 777 /app/logs
RUN mkdir -p logs && chown -R appuser:appuser /app
#USER appuser
EXPOSE 8000
CMD ["uvicorn", "src.api.api_app:app", "--host", "0.0.0.0", "--port", "8000"]