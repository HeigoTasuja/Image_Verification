FROM python:3.13-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY ./app /app/app

RUN mkdir -p /app/data
RUN addgroup --system app \
    && adduser --system --ingroup app app
RUN chown -R app:app /app

USER app

HEALTHCHECK --interval=30s --timeout=3s --start-period=5s --retries=3 \
    CMD python -c "import urllib.request, sys; \
    try: \
        r = urllib.request.urlopen('http://127.0.0.1:8000/api/stats', timeout=2); \
        sys.exit(0 if r.getcode() == 200 else 1); \
    except Exception: \
        sys.exit(1)"

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]