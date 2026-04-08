FROM python:3.12-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

EXPOSE 8080 9090 8883

CMD ["python", "-m", "src.core.node", "--config", "configs/production.yaml"]
