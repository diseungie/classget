from flask_wtf import FlaskForm
from flask_login import current_user
from wtforms import StringField, PasswordField, SubmitField, BooleanField, SelectField, TextAreaField, RadioField, \
    SelectMultipleField, ValidationError, widgets
from wtforms.validators import DataRequired, Length, EqualTo
from classget.models import User


class MultiCheckboxField(SelectMultipleField):
    widget = widgets.ListWidget(prefix_label=False)
    option_widget = widgets.CheckboxInput()


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


class ReviewForm(FlaskForm):
    keyword_choices = [('期末試験', '期末試験'), ('期末レポート', '期末レポート'), ('中間試験', '中間試験'),
               ('中間レポート', '中間レポート'), ('出席', '出席'), ('課題(毎回)', '課題(毎回)'), ('課題(たまに)', '課題(たまに)'),
               ('ライブ', 'ライブ'), ('オンデマンド', 'オンデマンド'), ('ライブ・オンデマ併用', 'ライブ・オンデマ併用'), ('対面', '対面'),
               ('顔出しアリ', '顔出しアリ'), ('顔出しナシ', '顔出しナシ')]
    title = StringField('タイトル*', validators=[DataRequired(), Length(max=30)])
    rating = RadioField('評　価*', choices=[(0, 'good'), (1, 'soso'), (2, 'bad')])
    content = TextAreaField('本　文*', validators=[DataRequired()])
    keyword = MultiCheckboxField('キーワード', choices=keyword_choices)
    submit = SubmitField('投 稿')


class SearchClassForm(FlaskForm):
    syozoku_choices = [('全学共通教育科目', '全学共通教育科目'), ('商学部', '商学部'), ('経済学部', '経済学部'), ('法学部', '法学部'), ('社会学部', '社会学部')]
    term_choices = [('春夏学期', '春夏学期'), ('春学期', '春学期'), ('夏学期', '夏学期'), ('秋冬学期', '秋冬学期'), ('秋学期', '秋学期'), ('冬学期', '冬学期')]
    day_choices = [('月', '月曜日'), ('火', '火曜日'), ('水', '水曜日'), ('木', '木曜日'), ('金', '金曜日')]
    time_choices = [('1', '１限'), ('2', '２限'), ('3', '３限'), ('4', '４限'), ('5', '５限')]
    draw_choices = [('抽選科目', '抽選科目'), ('抽選なし', '抽選なし')]
    keyword_choices = [('期末試験', '期末試験'), ('期末レポート', '期末レポート'), ('中間試験', '中間試験'),
                       ('中間レポート', '中間レポート'), ('出席', '出席'), ('課題(毎回)', '課題(毎回)'), ('課題(たまに)', '課題(たまに)'),
                       ('ライブ', 'ライブ'), ('オンデマンド', 'オンデマンド'), ('ライブ・オンデマ併用', 'ライブ・オンデマ併用'), ('対面', '対面'),
                       ('顔出しアリ', '顔出しアリ'), ('顔出しナシ', '顔出しナシ')]
    sort = MultiCheckboxField('時間割所属', choices=syozoku_choices)
    term = MultiCheckboxField('開講区分', choices=term_choices)
    day = MultiCheckboxField('曜日', choices=day_choices)
    time = MultiCheckboxField('時限', choices=time_choices)
    draw = MultiCheckboxField('抽選', choices=draw_choices)
    title = StringField('授業名')
    keyword = MultiCheckboxField('(避けたい)キーワード', choices=keyword_choices)
    submit = SubmitField('この条件で検索')


class UpdateClassForm(FlaskForm):
    sort = StringField('・時間割区分', validators=[DataRequired(), Length(max=20)])
    term = StringField('・学期', validators=[DataRequired(), Length(max=20)])
    time = StringField('・曜日と時限', validators=[DataRequired(), Length(max=20)])
    name = StringField('・授業名', validators=[DataRequired(), Length(max=50)])
    teacher = StringField('・教授名', validators=[DataRequired(), Length(max=50)])
    language = StringField('・言語', validators=[DataRequired(), Length(max=10)])
    draw = StringField('・抽選', validators=[DataRequired(), Length(max=10)])
    keyword = StringField('・キーワード', validators=[DataRequired(), Length(max=200)])
    submit = SubmitField('授業情報修正')
