FROM python:3.11-slim

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1
ENV PYTHONPATH=/app

WORKDIR /app

COPY requirements.txt requirements-mcp.txt ./
RUN pip install --no-cache-dir -r requirements-mcp.txt

COPY . .

RUN useradd --create-home appuser
USER appuser

CMD ["uvicorn", "ai_service.app:app", "--host", "0.0.0.0", "--port", "8000"]
