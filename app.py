from flask import Flask, render_template, request, redirect, url_for
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)

# Настройка базы данных SQLite
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///todo.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

# Модель задачи для БД
class Task(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False)

    def repr(self):
        return f'<Task {self.id}>'

# Автоматическое создание таблиц при запуске
with app.app_context():
    db.create_all()

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
        new_task = Task(title=title.strip())
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
    app.run(host='0.0.0.0', port=5000, debug=True)