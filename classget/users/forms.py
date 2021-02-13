from flask_login import current_user
from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SelectField, SubmitField, BooleanField
from wtforms.validators import DataRequired, Length, EqualTo, ValidationError

from classget.models import User


class RegistrationForm(FlaskForm):
    faculty_choices = [('商学部', '商学部'), ('経済学部', '経済学部'), ('法学部', '法学部'), ('社会学部', '社会学部')]
    username = StringField('Username',
                           validators=[DataRequired(), Length(min=1, max=16)])
    iduser = StringField('UserID',
                         validators=[DataRequired(), Length(min=2, max=50)])
    password = PasswordField('Password', validators=[DataRequired()])
    confirm_password = PasswordField('Confirm Password',
                                     validators=[DataRequired(), EqualTo('password')])
    faculty = SelectField('Faculty', choices=faculty_choices)
    year = SelectField('Year', choices=[(1, 1), (2, 2), (3, 3), (4, 4)])
    submit = SubmitField('アカウント作成')

    def validate_username(self, username):
        user = User.query.filter_by(username=username.data).first()
        if user:
            raise ValidationError('既に誰かが使用中のユーザー名です')

    def validate_iduser(self, iduser):
        user = User.query.filter_by(iduser=iduser.data).first()
        if user:
            raise ValidationError('既に誰かが使用中のIDです')


class LoginForm(FlaskForm):
    iduser = StringField('UserID',
                         validators=[DataRequired(), Length(min=2, max=50)])
    password = PasswordField('Password', validators=[DataRequired()])
    remember = BooleanField('Remember Me')
    submit = SubmitField('ログイン')


class UpdateAccountForm(FlaskForm):
    faculty_choices = [('商学部', '商学部'), ('経済学部', '経済学部'), ('法学部', '法学部'), ('社会学部', '社会学部')]
    username = StringField('Username',
                           validators=[DataRequired(), Length(min=2, max=10)])
    current_password = PasswordField('Current Password', validators=[DataRequired()])
    new_password = PasswordField('New Password(optional)')
    confirm_password = PasswordField('Confirm New Password(optional)',
                                     validators=[EqualTo('new_password')])
    faculty = SelectField('Faculty', choices=faculty_choices)
    year = SelectField('Year', choices=[(1, 1), (2, 2), (3, 3), (4, 4)])
    submit = SubmitField('アカウント情報修正')

    def validate_username(self, username):
        if username.data != current_user.username:
            user = User.query.filter_by(username=username.data).first()
            if user:
                raise ValidationError('既に誰かが使用中のユーザー名です')