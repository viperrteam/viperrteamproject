from flask import Flask, render_template, redirect, url_for, request, flash
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, UserMixin, login_user, logout_user, login_required, current_user
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime
import json, os

app = Flask(__name__)
app.config['SECRET_KEY'] = 'viperr-hub-secret-2024'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///edtech.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)
login_manager = LoginManager(app)
login_manager.login_view = 'login'
login_manager.login_message = 'Войдите в систему для доступа к этой странице.'

# ──────────────────────────────────────────────
#  Модели — по схеме БД
# ──────────────────────────────────────────────

# Связующая таблица: пользователь ↔ теги интересов
user_interests = db.Table('user_interests',
    db.Column('user_id', db.Integer, db.ForeignKey('users.user_id'), primary_key=True),
    db.Column('tag_id',  db.Integer, db.ForeignKey('tags.tag_id'),   primary_key=True)
)

# Material_Tags — связующая таблица материал ↔ тег
class MaterialTag(db.Model):
    __tablename__ = 'material_tags'
    material_tag_id = db.Column(db.Integer, primary_key=True)
    material_id     = db.Column(db.Integer, db.ForeignKey('materials.material_id'), nullable=False)
    tag_id          = db.Column(db.Integer, db.ForeignKey('tags.tag_id'),           nullable=False)

class User(UserMixin, db.Model):
    __tablename__ = 'users'
    user_id       = db.Column(db.Integer,     primary_key=True)
    username      = db.Column(db.String(80),  unique=True, nullable=False)
    email         = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(256), nullable=False)
    created_at    = db.Column(db.DateTime,    default=datetime.utcnow)
    last_login    = db.Column(db.DateTime,    nullable=True)
    interests     = db.relationship('Tag', secondary=user_interests, backref='interested_users')

    def get_id(self):
        return str(self.user_id)

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

class Material(db.Model):
    __tablename__ = 'materials'
    material_id = db.Column(db.Integer, primary_key=True)
    user_id     = db.Column(db.Integer, db.ForeignKey('users.user_id'), nullable=True)
    title       = db.Column(db.String(200), nullable=False)
    content     = db.Column(db.Text,        nullable=False)
    type        = db.Column(db.String(50),  default='course')
    tags        = db.relationship('Tag', secondary='material_tags',
                                  primaryjoin='Material.material_id == MaterialTag.material_id',
                                  secondaryjoin='Tag.tag_id == MaterialTag.tag_id',
                                  backref='materials')

class Tag(db.Model):
    __tablename__ = 'tags'
    tag_id      = db.Column(db.Integer, primary_key=True)
    material_id = db.Column(db.Integer, db.ForeignKey('materials.material_id'), nullable=True)
    tag_name    = db.Column(db.String(80), unique=True, nullable=False)

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

# ──────────────────────────────────────────────
#  Загрузка курсов из JSON в таблицу Materials
# ──────────────────────────────────────────────

def load_courses_from_json():
    json_path = os.path.join(os.path.dirname(__file__), 'courses.json')
    if not os.path.exists(json_path):
        print("courses.json не найден.")
        return
    if Material.query.count() > 0:
        return

    with open(json_path, encoding='utf-8') as f:
        data = json.load(f)

    tag_cache = {}
    for course_data in data['courses']:
        material = Material(
            title=course_data['title'],
            content=course_data['description'],
            type='course'
        )
        db.session.add(material)
        db.session.flush()  # получаем material_id

        for tag_name in course_data['tags']:
            if tag_name not in tag_cache:
                tag = Tag.query.filter_by(tag_name=tag_name).first()
                if not tag:
                    tag = Tag(tag_name=tag_name, material_id=material.material_id)
                    db.session.add(tag)
                    db.session.flush()
                tag_cache[tag_name] = tag

            # проверяем что связь ещё не добавлена
            exists = MaterialTag.query.filter_by(
                material_id=material.material_id,
                tag_id=tag_cache[tag_name].tag_id
            ).first()
            if not exists:
                mt = MaterialTag(material_id=material.material_id,
                                 tag_id=tag_cache[tag_name].tag_id)
                db.session.add(mt)

    db.session.commit()
    print(f"Загружено {Material.query.count()} материалов, {Tag.query.count()} тегов.")

# ──────────────────────────────────────────────
#  Аутентификация
# ──────────────────────────────────────────────

@app.route('/register', methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('catalog'))
    if request.method == 'POST':
        username = request.form.get('username', '').strip()
        email    = request.form.get('email', '').strip()
        password = request.form.get('password', '')
        if not username or not email or not password:
            flash('Заполните все поля.', 'error')
        elif User.query.filter_by(username=username).first():
            flash('Имя пользователя уже занято.', 'error')
        elif User.query.filter_by(email=email).first():
            flash('Email уже зарегистрирован.', 'error')
        else:
            user = User(username=username, email=email)
            user.set_password(password)
            db.session.add(user)
            db.session.commit()
            login_user(user)
            flash('Добро пожаловать!', 'success')
            return redirect(url_for('catalog'))
    return render_template('register.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('catalog'))
    if request.method == 'POST':
        username = request.form.get('username', '').strip()
        password = request.form.get('password', '')
        user = User.query.filter_by(username=username).first()
        if user and user.check_password(password):
            user.last_login = datetime.utcnow()
            db.session.commit()
            login_user(user)
            return redirect(request.args.get('next') or url_for('catalog'))
        flash('Неверный логин или пароль.', 'error')
    return render_template('login.html')

@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('login'))

# ──────────────────────────────────────────────
#  Каталог
# ──────────────────────────────────────────────

@app.route('/')
@app.route('/catalog')
@login_required
def catalog():
    page   = request.args.get('page', 1, type=int)
    search = request.args.get('q', '').strip()
    tag_id = request.args.get('tag', type=int)

    query = Material.query
    if search:
        query = query.filter(Material.title.ilike(f'%{search}%'))
    if tag_id:
        query = query.filter(Material.tags.any(Tag.tag_id == tag_id))

    pagination = query.paginate(page=page, per_page=12, error_out=False)
    all_tags   = Tag.query.order_by(Tag.tag_name).all()
    return render_template('catalog.html',
                           courses=pagination.items,
                           pagination=pagination,
                           all_tags=all_tags,
                           search=search,
                           active_tag=tag_id)

# ──────────────────────────────────────────────
#  Профиль
# ──────────────────────────────────────────────

@app.route('/profile')
@login_required
def profile():
    all_tags = Tag.query.order_by(Tag.tag_name).all()
    return render_template('profile.html', all_tags=all_tags)

@app.route('/profile/interests', methods=['POST'])
@login_required
def save_interests():
    selected_ids  = request.form.getlist('interests', type=int)
    selected_tags = Tag.query.filter(Tag.tag_id.in_(selected_ids)).all()
    current_user.interests = selected_tags
    db.session.commit()
    flash('Интересы сохранены!', 'success')
    return redirect(url_for('profile'))

# ──────────────────────────────────────────────
#  Запуск
# ──────────────────────────────────────────────

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
        load_courses_from_json()
    app.run(debug=True)