from flask import Flask, render_template, request, redirect, url_for, session, flash
from flask_sqlalchemy import SQLAlchemy
import os   # ← 新增這行

app = Flask(__name__)
app.secret_key = '124549768'

BASE_DIR = os.path.dirname(os.path.abspath(__file__))  # ← 新增這行
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + os.path.join(BASE_DIR, 'points.db')  # ← 修改這行
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    phone = db.Column(db.String(20), unique=True, nullable=False)  # 用 phone 當唯一值

class Points(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    points = db.Column(db.Integer, default=0)
    updated_at = db.Column(db.DateTime, server_default=db.func.now(), onupdate=db.func.now())

@app.route('/')
def index():
    if 'user_id' in session:
        user = User.query.get(session['user_id'])
        if user:
            points = Points.query.filter_by(user_id=user.id).first()
            points_value = points.points if points else 0
            return render_template('index.html', phone=user.phone, points=points_value)
        else:
            session.pop('user_id', None)
    return render_template('index.html', phone=None)

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        phone = request.form['phone']
        user = User.query.filter_by(phone=phone).first()
        if not user:
            user = User(phone=phone)
            db.session.add(user)
            db.session.commit()
            points = Points(user_id=user.id, points=0)
            db.session.add(points)
            db.session.commit()
            flash('首次登入，已自動建立帳號')
        session['user_id'] = user.id
        flash('登入成功')
        return redirect(url_for('index'))
    return render_template('login.html')

@app.route('/logout')
def logout():
    session.pop('user_id', None)
    flash('已登出')
    return redirect(url_for('index'))

@app.route('/add_point')
def add_point():
    if 'user_id' not in session:
        flash('請先登入')
        return redirect(url_for('login'))
    points = Points.query.filter_by(user_id=session['user_id']).first()
    if points:
        points.points += 1
        db.session.commit()
    flash('集點成功！')
    return redirect(url_for('index'))

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(debug=True)
