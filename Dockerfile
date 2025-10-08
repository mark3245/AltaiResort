FROM python:3.11-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

WORKDIR /app

COPY requirements.txt /app/
RUN pip install --no-cache-dir -r requirements.txt

COPY . /app

# Collect static at build time (optional)
RUN python manage.py collectstatic --noinput || true

EXPOSE 8000
CMD ["gunicorn", "altai_resort.wsgi:application", "--bind", "0.0.0.0:8000"]
