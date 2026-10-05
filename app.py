from flask import Flask, render_template, request, redirect, url_for, session
from flask_sqlalchemy import SQLAlchemy
import os
try:
    from werkzeug.security import generate_password_hash, check_password_hash
except ModuleNotFoundError:
    os.system("pip install werkzeug")
    from werkzeug.security import generate_password_hash, check_password_hash

app = Flask(__name__)
app.config['SECRET_KEY'] = 'my-super-secret-key-123'

# Настройка базы данных SQLite
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///todo.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(50), nullable=False, unique=True)
    password = db.Column(db.String(200), nullable=False)

    tasks = db.relationship('Task', backref='author', lazy=True)

# Модель задачи для БД (Добавили новое поле device)
class Task(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False)
    device = db.Column(db.String(150), default="Неизвестное устройство") # Сюда пишем марку

    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)

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
    # Если пользователя нет в сессии - выкидывает на вход
    if 'user_id' not in session:
        return redirect(url_for('login'))
    
    # ФИЛЬТР: Вытаскивает задачи только этого пользователя
    current_user_id = session['user_id']
    my_tasks = Task.query.filter_by(user_id=current_user_id).all()
    
    # Ищет имя юзера в SQLite
    user = User.query.get(current_user_id)

    # Передает личные задачи и имя юзера в HTML-шаблон
    return render_template('index.html', tasks=my_tasks, username=user.username)

# Маршрут для добавления задачи
@app.route('/add', methods=['POST'])
def add():
    # Если неавторизованный гость - выкидывает его
    if 'user_id' not in session:
        return redirect(url_for('index'))

    # Забирает текст из формочки (из поля 'title')
    title_text = request.form.get('title')
    
    if title_text and title_text.strip():
        # Считывает User-Agent зашедшего
        raw_ua = request.headers.get('User-Agent', '')
        device_name = get_clean_device(raw_ua)
        
        # Вытаскивает ID текущего вошедшего из сессии
        current_user_id = session['user_id']
        
        # записывает текст в title (как в базе), а владельца в user_id
        new_task = Task(title=title_text.strip(), device=device_name, user_id=current_user_id)
        
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

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')

        user = User.query.filter_by(username=username).first()

        if user and check_password_hash(user.password, password):
            session['user_id'] = user.id
            return redirect(url_for('index'))
        else:
            return "Неверное имя пользователя или пароль! Попробуйте снова."

    return '''
<form method="POST">
    <h2>Вход</h2>
    <input type="text" name="username" placeholder="Введите логин" required><br><br>
    <input type="password" name="password" placeholder="Введите пароль" required><br><br>
    <button type="submit">Войти</button>
</form>
'''

@app.route('/logout', methods=['GET', 'POST'])
def logout():
    session.clear()
    return redirect(url_for('login'))

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=7777, debug=True)
