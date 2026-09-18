from flask import Flask, render_template, request, redirect, url_for
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)

# Настройка базы данных SQLite
app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://ivan:super_secret_123@127.0.0.1:5432/todo_db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

# Модель задачи для БД (Добавили новое поле device)
class Task(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False)
    device = db.Column(db.String(150), default="Неизвестное устройство") # Сюда пишем марку

    def repr(self):
        return f'<Task {self.id}>'

# Автоматическое создание таблиц при запуске
with app.app_context():
    db.create_all()

# Функция для красивого определения марки телефона из сложной строки User-Agent
def get_clean_device(user_agent_string):
    ua = user_agent_string.lower()
    if 'iphone' in ua:
        return 'Apple iPhone 📱'
    elif 'ipad' in ua:
        return 'Apple iPad 🍏'
    elif 'android' in ua:
        # Пытаемся вытащить модель Android (например, Redmi, Samsung)
        if 'redmi' in ua or 'xiaomi' in ua: return 'Xiaomi / Redmi 📱'
        if 'samsung' in ua: return 'Samsung Galaxy 📱'
        if 'huawei' in ua: return 'Huawei 📱'
        return 'Android Device 🤖'
    elif 'windows' in ua:
        return 'Компьютер (Windows) 💻'
    elif 'macintosh' in ua:
        return 'Компьютер (MacBook) 💻'
    elif 'linux' in ua:
        return 'Компьютер (Linux) 🐧'
    return 'Неизвестный гаджет ❓'

# Главная страница: просмотр списка задач
@app.route('/')
def index():
    tasks = Task.query.order_by(Task.id.desc()).all()
    return render_template('index.html', tasks=tasks)

# Маршрут для добавления задачи
@app.route('/add', methods=['POST'])
def add():
    title = request.form.get('title')
    if title and title.strip():
        # Считываем User-Agent зашедшего друга!
        raw_ua = request.headers.get('User-Agent', '')
        device_name = get_clean_device(raw_ua)
        
        new_task = Task(title=title.strip(), device=device_name)
        db.session.add(new_task)
        db.session.commit()
    return redirect(url_for('index'))

# Маршрут для удаления задачи
@app.route('/delete/<int:id>')
def delete(id):
    task_to_delete = Task.query.get_or_404(id)
    db.session.delete(task_to_delete)
    db.session.commit()
    return redirect(url_for('index'))

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=7777, debug=True)
