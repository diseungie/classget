from flask_wtf import FlaskForm
from flask_login import current_user
from wtforms import StringField, PasswordField, SubmitField, BooleanField, SelectField, RadioField, ValidationError
from wtforms.validators import DataRequired, Length, EqualTo
from classget.models import User


class RegistrationForm(FlaskForm):
    faculty_choices = [('商学部', '商学部'), ('経済学部', '経済学部'), ('法学部', '法学部'), ('社会学部', '社会学部')]
    username = StringField('Username',
                           validators=[DataRequired(), Length(min=2, max=10)])
    iduser = StringField('UserID',
                         validators=[DataRequired(), Length(min=2, max=50)])
    password = PasswordField('Password', validators=[DataRequired()])
    confirm_password = PasswordField('Confirm Password',
                                     validators=[DataRequired(), EqualTo('password')])
    faculty = SelectField('Faculty', choices=faculty_choices)
    year = SelectField('Year', choices=[(1, 1), (2, 2), (3, 3), (4, 4)])
    submit = SubmitField('Sign Up')

    def validate_username(self, username):
        user = User.query.filter_by(username=username.data).first()
        if user:
            raise ValidationError('That username is taken, Please choose a different one')

    def validate_iduser(self, iduser):
        user = User.query.filter_by(iduser=iduser.data).first()
        if user:
            raise ValidationError('That ID is taken, Please choose a different one')


class LoginForm(FlaskForm):
    iduser = StringField('UserID',
                         validators=[DataRequired(), Length(min=2, max=50)])
    password = PasswordField('Password', validators=[DataRequired()])
    remember = BooleanField('Remember Me')
    submit = SubmitField('Login')


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
    submit = SubmitField('Update')

    def validate_username(self, username):
        if username.data != current_user.username:
            user = User.query.filter_by(username=username.data).first()
            if user:
                raise ValidationError('That username is taken, Please choose a different one')


class TypeTestForm(FlaskForm):
    typetest_choices = [(-30, '1'), (-20, '2'), (-10, '3'), (0, '4'), (3, '5'), (7, '6'), (15, '7')]
    Q1 = RadioField('Q01.初対面の人と友達になるのが得意だ。', choices=typetest_choices, validators=[DataRequired()])
    Q2 = RadioField('Q02.人助けをしたり、されたりすることが多い。', choices=typetest_choices, validators=[DataRequired()])
    Q3 = RadioField('Q03.課題の期限は守るほうだし、遅刻もしない。', choices=typetest_choices, validators=[DataRequired()])
    Q4 = RadioField('Q04.普段ストレスや不安をなかなか感じないブッダみたいな性格を持っている。', choices=typetest_choices, validators=[DataRequired()])
    Q5 = RadioField('Q05.芸術や美術は結構好きだ。', choices=typetest_choices, validators=[DataRequired()])
    Q6 = RadioField('Q06.しばしば新しい冒険についてのアイデアが思い浮かぶ。', choices=typetest_choices, validators=[DataRequired()])
    Q7 = RadioField('Q07.他の人にどう思われるかなんて気にしない超マイウェイ。', choices=typetest_choices, validators=[DataRequired()])
    Q8 = RadioField('Q08.人との約束のためなら無理もする。', choices=typetest_choices, validators=[DataRequired()])
    Q9 = RadioField('Q09.みんなで何かを成し遂げることが好きだ。', choices=typetest_choices, validators=[DataRequired()])
    Q10 = RadioField('Q10.面白い話で場を盛り上げることができる。', choices=typetest_choices, validators=[DataRequired()])
    submit = SubmitField('診断結果へ')
