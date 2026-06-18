FROM python:3.11-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY bot.py .
COPY knowledge ./knowledge

# Unbuffered logs so docker compose logs shows output immediately.
ENV PYTHONUNBUFFERED=1

CMD ["python", "bot.py"]
