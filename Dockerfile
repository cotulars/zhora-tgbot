FROM python:3.11-slim

LABEL authors="cotulars"

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . /app/

ENV PYTHONPATH=/app

CMD ["python", "src/main.py"]
