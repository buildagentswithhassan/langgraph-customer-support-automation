FROM python:3.12-slim

WORKDIR /app

RUN apt-get update && apt-get install -y curl && rm -rf /var/lib/apt/lists/*
RUN adduser --disabled-password --gecos '' appuser

COPY pyproject.toml .
RUN pip install --no-cache-dir -e .

COPY . .
RUN chown -R appuser:appuser /app

USER appuser

EXPOSE 8000

CMD ["uvicorn", "main:mcp_app", "--host", "0.0.0.0", "--port", "8000"]
