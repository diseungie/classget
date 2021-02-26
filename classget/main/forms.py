from flask_wtf import FlaskForm
from wtforms import SelectMultipleField, widgets, StringField, SubmitField


class MultiCheckboxField(SelectMultipleField):
    widget = widgets.ListWidget(prefix_label=False)
    option_widget = widgets.CheckboxInput()


class SearchClassForm(FlaskForm):
    syozoku_choices = [('全学共通教育科目', '全学共通教育科目'), ('商学部', '商学部'), ('経済学部', '経済学部'),
                       ('法学部', '法学部'), ('社会学部', '社会学部'), ('国際交流科目', '国際交流科目'), ('教職科目', '教職科目')]
    term_choices = [('春夏学期', '春夏学期'), ('春学期', '春学期'), ('夏学期', '夏学期'), ('秋冬学期', '秋冬学期'),
                    ('秋学期', '秋学期'), ('冬学期', '冬学期'), ('通年', '通年')]
    day_choices = [('月', '月曜日'), ('火', '火曜日'), ('水', '水曜日'), ('木', '木曜日'), ('金', '金曜日'), ('他', '他')]
    time_choices = [('1', '１限'), ('2', '２限'), ('3', '３限'), ('4', '４限'), ('5', '５限'), ('他', '他')]
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
