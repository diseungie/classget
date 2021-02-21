from flask_wtf import FlaskForm
from wtforms import SelectMultipleField, widgets, StringField, RadioField, TextAreaField, SubmitField
from wtforms.validators import DataRequired, Length, ValidationError


class MultiCheckboxField(SelectMultipleField):
    widget = widgets.ListWidget(prefix_label=False)
    option_widget = widgets.CheckboxInput()


class ReviewForm(FlaskForm):
    keyword_choices = [('期末試験', '期末試験'), ('期末レポート', '期末レポート'), ('中間試験', '中間試験'),
               ('中間レポート', '中間レポート'), ('出席', '出席'), ('課題(毎回)', '課題(毎回)'), ('課題(たまに)', '課題(たまに)'),
               ('ライブ', 'ライブ'), ('オンデマンド', 'オンデマンド'), ('ライブ・オンデマ併用', 'ライブ・オンデマ併用'), ('対面', '対面'),
               ('顔出しアリ', '顔出しアリ'), ('顔出しナシ', '顔出しナシ')]
    title = StringField('タイトル*', validators=[DataRequired(), Length(max=15)])
    rating = RadioField('評　価*', choices=[(0, 'good'), (1, 'soso'), (2, 'bad')])
    content = TextAreaField('本　文*', validators=[DataRequired()])
    keyword = MultiCheckboxField('キーワード', choices=keyword_choices)
    submit = SubmitField('投 稿')

    def validate_title(self, title):
        if len(title.data) > 15:
            raise ValidationError('タイトルは15字以内で書いてください')
