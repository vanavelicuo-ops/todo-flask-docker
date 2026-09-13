FROM huecker.io/library/python:3.12-slim

ENV PYTHONIOENCODING=utf-8

WORKDIR /app

COPY . /app

RUN pip install --no-cache-dir flask flask-sqlalchemy

EXPOSE 5000

CMD ["python", "app.py"]