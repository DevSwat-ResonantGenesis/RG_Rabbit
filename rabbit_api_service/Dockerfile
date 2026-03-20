FROM python:3.11-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY app ./app

COPY alembic.ini ./alembic.ini
COPY alembic ./alembic

EXPOSE 8000

CMD ["sh", "-c", "i=0; until alembic upgrade head; do i=$((i+1)); if [ $i -ge 30 ]; then echo 'alembic failed after retries' >&2; exit 1; fi; sleep 2; done; uvicorn app.main:app --host 0.0.0.0 --port 8000"]
