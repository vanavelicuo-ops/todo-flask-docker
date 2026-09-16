#!/bin/bash
echo "Запуск автоматического деплоя�..."

docker rm -f my_todo_app

docker build -t my_todo_app .

docker run -d --name my_todo_app --restart=always --net=host my_todo_app

echo "Деплой успешно завершен! Сайт обновле��.�"

