FROM python:3.10-slim
RUN apt-get update && apt-get install -y --no-install-recommends iproute2 \
    && rm -rf /var/lib/apt/lists/*
WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY agent.py .
# topology_data.csv được mount từ docker-compose (không COPY cố định)
CMD ["python", "agent.py"]
