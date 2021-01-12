from flask_wtf import FlaskForm
from flask_login import current_user
from wtforms import StringField, PasswordField, SubmitField, BooleanField, SelectField, ValidationError
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
