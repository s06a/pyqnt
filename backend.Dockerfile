FROM python:3.10-slim

WORKDIR /app

COPY . .

RUN pip install --no-cache-dir ".[full]"

ENV PYTHONPATH=/app/src

CMD ["uvicorn", "api.main:app", "--host", "0.0.0.0", "--port", "8000"]
