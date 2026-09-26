from flask import Flask, render_template, request, redirect, url_for
from flask_sqlalchemy import SQLAlchemy
import os
try:
    from werkzeug.security import generate_password_hash, check_password_hash
except ModuleNotFoundError:
    os.system("pip install werkzeug")
    from werkzeug.security import generate_password_hash, check_password_hash

app = Flask(__name__)

# Настройка базы данных SQLite
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///todo.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

# Модель задачи для БД (Добавили новое поле device)
class Task(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False)
    device = db.Column(db.String(150), default="Неизвестное устройство") # Сюда пишем марку

    def repr(self):
        return f'<Task {self.id}>'

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(50), nullable=False, unique=True)
    password = db.Column(db.String(200), nullable=False)

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

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')

        existing_user = User.query.filter_by(username=username).first()
        if existing_user:
            return "Такой полльзователь уже существует"

        hashed_password=generate_password_hash(password)
        new_user = User(username=username, password=hashed_password)

        db.session.add(new_user)
        db.session.commit()
        return f"полльзователь {username} успешно зарегистрирован! теперь можно войти"
    return '''
<form method="POST">
    <h2>Регистрация</h2>
    <input type="text" name="username" placeholder="Придумайте логин" required><br><br>
    <input type="password" name="password" placeholder="придумайте пароль" required><br><br>
    <button type="sumbit">Зарегистрироватся</button>
</form>
'''

@app.route('/users')
def show_users():
    all_users=User.query.all()
    output = "<h2>Список зарегистрованих пользователей: </h2>"
    for u in all_users:
        output += f"<p>Логин: {u.username} | хеш: {u.password}</p>"
    return output

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=7777, debug=True)
