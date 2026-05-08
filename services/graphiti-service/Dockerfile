FROM python:3.11-slim AS builder

WORKDIR /build
RUN pip install --upgrade pip
COPY pyproject.toml .
RUN pip install --prefix=/install .

FROM python:3.11-slim

WORKDIR /app
RUN groupadd -r appuser && useradd -r -g appuser appuser

COPY --from=builder /install /usr/local
COPY --from=builder /build/app ./app

RUN chown -R appuser:appuser /app
USER appuser

EXPOSE 8001
HEALTHCHECK --interval=10s --timeout=5s --retries=3 \
    CMD python -c "import urllib.request; urllib.request.urlopen('http://localhost:8001/health')" || exit 1

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8001"]
