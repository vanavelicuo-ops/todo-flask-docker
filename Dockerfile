# Шаг 1: Берем чистый Python 3.12 через рабочее зеркало huecker.io
FROM huecker.io/library/python:3.12-slim

ENV PYTHONIOENCODING=utf-8

# Шаг 2: Создаем внутри контейнера рабочую папку /app
WORKDIR /app

# Шаг 3: Копируем все файлы нашего проекта с ноутбука внутрь контейнера
COPY . /app

# Шаг 4: Устанавливаем библиотеки Flask и Flask-SQLAlchemy через pip
RUN pip install --no-cache-dir flask flask-sqlalchemy

# Шаг 5: Говорим Docker, что наше приложение работает на 5000-м порту
EXPOSE 5000

# Шаг 6: Инструкция, как именно запускать наш сайт при старте контейнера
CMD ["python", "app.py"]