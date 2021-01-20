from classget import db, login_manager
from datetime import datetime
from flask_login import UserMixin


@login_manager.user_loader
def load_user(id):
    return User.query.get(int(id))


class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    iduser = db.Column(db.String(50), unique=True, nullable=False)
    username = db.Column(db.String(10), unique=True, nullable=False)
    password = db.Column(db.String(50), nullable=False)
    faculty = db.Column(db.String(10), nullable=False)
    year = db.Column(db.Integer, nullable=False)
    type = db.Column(db.String(10), nullable=False, default='none')
    reviews = db.relationship('Review', backref='author', lazy=True)

    liked = db.relationship('Like', foreign_keys='Like.user_id', backref='user', lazy='dynamic')

    def __repr__(self):
        return f"User('{self.username}', '{self.iduser}', '{self.faculty}', '{self.year}', '{self.type}')"

    def like_subject(self, subject):
        if not self.has_liked_subject(subject):
            like = Like(user_id=self.id, subject_id=subject.id, subject_term=subject.term)
            db.session.add(like)

    def unlike_subject(self, subject):
        if self.has_liked_subject(subject):
            Like.query.filter_by(
                user_id=self.id, subject_id=subject.id, subject_term=subject.term).delete()

    def has_liked_subject(self, subject):
        return Like.query.filter(
            Like.user_id == self.id,
            Like.subject_id == subject.id,
            Like.subject_term == subject.term).count() > 0


class Subject(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    sort = db.Column(db.String(20), nullable=False)
    term = db.Column(db.String(20), nullable=False)
    time = db.Column(db.String(20), nullable=False)
    name = db.Column(db.String(60), nullable=False)
    teacher = db.Column(db.String(30), nullable=False)
    language = db.Column(db.String(20), nullable=False)
    draw = db.Column(db.String(10), nullable=False)
    keyword = db.Column(db.String(200))

    likes = db.relationship('Like', backref='subject', lazy='dynamic')

    def __repr__(self):
        return f"Subject('{self.id}', '{self.sort}', '{self.term}', '{self.time}', '{self.name}', '{self.teacher}', " \
               f"'{self.language}', '{self.draw}', '{self.keyword}')"


class Review(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(30), nullable=False)
    rating = db.Column(db.Integer, nullable=False)
    content = db.Column(db.Text, nullable=False)
    keyword = db.Column(db.String(200))
    date_posted = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    subject_id = db.Column(db.Integer, db.ForeignKey('subject.id'), nullable=False)


class Like(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    subject_id = db.Column(db.Integer, db.ForeignKey('subject.id'))
    subject_term = db.Column(db.String(10), nullable=False)