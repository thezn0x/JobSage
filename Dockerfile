FROM python:3.11-slim
LABEL authors="zain"
WORKDIR app/
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
RUN playwright install --with-deps chromium
COPY . .
RUN mkdir -p logs
EXPOSE 8000
CMD ["uvicorn","src.api.api_app:app","--host","0.0.0.0","--port","8000"]