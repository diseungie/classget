from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField
from wtforms.validators import DataRequired


class UpdateClassForm(FlaskForm):
    sort = StringField('・時間割区分', validators=[DataRequired()])
    term = StringField('・学期', validators=[DataRequired()])
    time = StringField('・曜日と時限', validators=[DataRequired()])
    name = StringField('・授業名', validators=[DataRequired()])
    teacher = StringField('・教授名', validators=[DataRequired()])
    language = StringField('・言語', validators=[DataRequired()])
    draw = StringField('・抽選', validators=[DataRequired()])
    keyword = StringField('・キーワード', validators=[DataRequired()])
    submit = SubmitField('授業情報修正')