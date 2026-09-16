FROM python:3.12-slim

ENV PYTHONIOENCODING=utf-8

WORKDIR /app

COPY . /app

RUN pip install --no-cache-dir flask flask-sqlalchemy psycopg2-binary

EXPOSE 7777

CMD ["python", "app.py"]

# Hello vim
