from classget import db, login_manager
from datetime import datetime
from flask_login import UserMixin


@login_manager.user_loader
def load_user(iduser):
    return User.query.get(int(iduser))


class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    iduser = db.Column(db.String(20), unique=True, nullable=False)
    username = db.Column(db.String(10), unique=True, nullable=False)
    password = db.Column(db.String(50), nullable=False)
    faculty = db.Column(db.String(10), nullable=False)
    year = db.Column(db.Integer, nullable=False)
    type = db.Column(db.String(10), nullable=False, default='none')
    posts = db.relationship('Post', backref='author', lazy=True)

    def __repr__(self):
        return f"User('{self.username}', '{self.iduser}', '{self.image_file}')"


class Post(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(50), nullable=False)
    date_posted = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    content = db.Column(db.Text, nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.iduser'), nullable=False)

    def __repr__(self):
        return f"User('{self.title}', '{self.date_posted}')"
