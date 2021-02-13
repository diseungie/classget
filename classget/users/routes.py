import random

from flask import Blueprint, url_for, render_template, request
from flask_login import current_user, login_user, login_required, logout_user
from werkzeug.utils import redirect

from classget import bcrypt, db
from classget.models import User, Like, get_count, Subject
from classget.users.forms import RegistrationForm, LoginForm, UpdateAccountForm

users = Blueprint('users', __name__)


@users.route("/createaccount", methods=['GET', 'POST'])
def createaccount():
    if current_user.is_authenticated:
        return redirect(url_for('main.mainpage'))
    form = RegistrationForm()
    # アカウント作成フォームを提出したら
    if form.validate_on_submit():
        # パスワードの暗号化
        hashed_pw = bcrypt.generate_password_hash(form.password.data).decode('utf-8')
        # ユーザー情報をデータベースに入れる
        user = User(username=form.username.data, iduser=form.iduser.data, password=hashed_pw,
                    faculty=form.faculty.data, year=form.year.data)
        db.session.add(user)
        db.session.commit()
        # さっき作られたアカウントでログインさせる
        user = User.query.filter_by(iduser=form.iduser.data).first()
        login_user(user)
        # キャラ診断ページに送る
        return redirect(url_for('users.typetest'))
    return render_template('createaccount.html', title='アカウント作成', form=form)


@users.route("/login", methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('main.mainpage'))
    form = LoginForm()
    login_error = 0
    # ログインフォームを提出したら
    if form.validate_on_submit():
        # 入力したIDでユーザー情報を持ってくる
        user = User.query.filter_by(iduser=form.iduser.data).first()
        # そのユーザー情報のPWとログインフォームで入力したPWが一致する場合
        if user and bcrypt.check_password_hash(user.password, form.password.data):
            # ログインさせる
            login_user(user, remember=form.remember.data)
            # 行こうとしたページがあったらそのページに送る
            next_page = request.args.get('next')
            return redirect(next_page) if next_page else redirect(url_for('main.mainpage'))
        # パスワードが一致しない場合：パスワードエラー
        else:
            login_error = 1
    return render_template('login.html', title='ログイン', form=form, login_error=login_error)


@users.route("/updateaccount", methods=['GET', 'POST'])
@login_required
def updateaccount():
    form = UpdateAccountForm()
    password_error = 0
    # アカウント修正フォームを提出した場合
    if form.validate_on_submit():
        # 入力したPWが現在のPWと一致したら
        if bcrypt.check_password_hash(current_user.password, form.current_password.data):
            # 修正情報をデータベースに入れる
            current_user.username = form.username.data
            current_user.faculty = form.faculty.data
            current_user.year = form.year.data
            db.session.commit()
            # パスワードを変更（新しいパスワードを入力した場合）
            if form.new_password.data:
                current_user.password = bcrypt.generate_password_hash(form.new_password.data).decode('utf-8')
                db.session.commit()
            # 修正が終わったらマイページに戻る
            return redirect(url_for('users.mypage', my_term='春'))
        # 入力したPWが現在PWと一致しない場合：パスワードエラー
        else:
            password_error = 1
    # ページを読み取った場合に書いてあるデフォルトユーザー情報
    elif request.method == 'GET':
        form.username.data = current_user.username
        form.faculty.data = current_user.faculty
        form.year.data = current_user.year

    return render_template('updateaccount.html', title='アカウント情報修正', form=form, password_error=password_error)


@users.route("/logout")
def logout():
    logout_user()
    return redirect(url_for('main.mainpage'))


@users.route("/mypage/<my_term>")
@login_required
def mypage(my_term):
    image_file = url_for('static', filename='img/profile_pics/' + current_user.type + '.png')
    liked_subject = Like.query.filter_by(user_id=current_user.id)\
        .filter(Like.subject_term.like('%{}%'.format(my_term))).all()

    def timetable(i):
        result = []
        for l in liked_subject:
            for t in l.subject.time.split(','):
                if t == i:
                    result.append([l.subject.id, l.subject.name])
        return result
    return render_template('mypage.html', title='マイページ', image_file=image_file, liked=liked_subject,
                           timetable=timetable, my_term=my_term)


@users.route("/typetest", methods=['GET', 'POST'])
@login_required
def typetest():
    question = ['初対面の人と友達になるのが得意だ。', '人助けをしたり、されたりすることが多い。', '課題の期限は守るほうだし、遅刻もしない。',
                '普段ストレスや不安をなかなか感じない性格を持っている。', '芸術や美術は結構好きだ。',
                'しばしば新しい冒険についてのアイデアが思い浮かぶ。', '他の人にどう思われるかなんて気にしない超マイウェイ。',
                '人との約束のためなら無理もする。', 'みんなで何かを成し遂げることが好きだ。', '面白い話で場を盛り上げることができる。']
    # すでにキャラ診断した人は結果ページに送る
    if current_user.type != 'none':
        return redirect(url_for('users.typeresult'))
    if request.method == 'POST':
        # formのdataから属性ごとにスコアを集計
        kaisou_score = int(request.form['Q1']) + int(request.form['Q10'])
        penguin_score = int(request.form['Q2']) + int(request.form['Q9'])
        iruka_score = int(request.form['Q3']) + int(request.form['Q8'])
        kame_score = int(request.form['Q4']) + int(request.form['Q7'])
        taco_score = int(request.form['Q5']) + int(request.form['Q6'])
        scores = {'海藻': kaisou_score, 'ペンギン': penguin_score, 'イルカ': iruka_score,
                  'カメ': kame_score, 'タコ': taco_score}
        # 一番高いスコアのキャラを入れる（複数の場合は共同１位のうちランダムで）
        max_score = max(scores.items(), key=lambda x: x[1])
        list_max = []
        for key, value in scores.items():
            if value == max_score[1]:
                list_max.append(key)
        current_user.type = random.choice(list_max)
        db.session.commit()
        return redirect(url_for('users.typeresult'))
    return render_template('typetest.html', question=question, title='キャラ診断')


@users.route("/typeresult", methods=['GET'])
@login_required
def typeresult():
    recommended_subjects = current_user.recommend_by_likes()
    catchphrase = {'海藻': '楽しいこと大好き！いつもノリノリな陽キャ',
                   'ペンギン': '冷たい氷も溶けちゃう優しさ！協力的なサポーター',
                   'イルカ': '頼まれたら裏切らない！信頼のメガバンク',
                   'カメ': '100人乗っても大丈夫！屋久杉のような安定感',
                   'タコ': '好奇心が止まらない！圧倒的な柔軟性'}
    description = {'海藻': ['おしゃべりで周りを楽しませることができる', '誰かと一緒にいることが好き', '自己主張がしっかりできる', '行動的なみんなのリーダータイプ'],
                   'ペンギン': ['やさしく、思いやりがある', '面倒見がいい', '共感力が高く、人の痛みが良く分かる', '人を疑わない'],
                   'イルカ': ['計画的に集中して物事に取り組むことができる', '責任感が強い', '誠実で頼られやすい', '時間や期限をきちんと守る'],
                   'カメ': ['大勢の人の前でもあまり緊張せずにいられる', '環境が変わってもなじみやすい', 'ものごとを根に持たない', 'あまり激しい感情にならない'],
                   'タコ': ['クリエイティブだとよく言われる', '原宿が好きだったりする', '人とかぶらないものが好き', '異なる解釈が可能な映画や本などに興味がある']}
    type_number = get_count(User.query.filter_by(type=current_user.type))
    user_number = get_count(User.query)
    type_com = get_count(User.query.filter_by(type=current_user.type, faculty='商学部'))
    type_eco = get_count(User.query.filter_by(type=current_user.type, faculty='経済学部'))
    type_law = get_count(User.query.filter_by(type=current_user.type, faculty='法学部'))
    type_soc = get_count(User.query.filter_by(type=current_user.type, faculty='社会学部'))
    type_proportion = "{:.1f}".format((type_number/user_number)*100)
    com_proportion = "{:.1f}".format((type_com/type_number)*100)
    eco_proportion = "{:.1f}".format((type_eco / type_number) * 100)
    law_proportion = "{:.1f}".format((type_law / type_number) * 100)
    soc_proportion = "{:.1f}".format((type_soc / type_number) * 100)
    return render_template('typeresult.html', recommended_subjects=recommended_subjects, type_pp=type_proportion,
                           com_pp=com_proportion, eco_pp=eco_proportion, law_pp=law_proportion, soc_pp=soc_proportion,
                           catchphrase=catchphrase, get_count=get_count, description=description, title='診断結果')


@users.route('/like', methods=['POST'])
@login_required
def like():
    subject_id = request.form['subject_id']
    action = request.form['action']
    subject = Subject.query.filter_by(id=subject_id).first_or_404()
    if action == 'like':
        current_user.like_subject(subject)
        db.session.commit()
    if action == 'unlike':
        current_user.unlike_subject(subject)
        db.session.commit()

    return render_template('like_button.html', subject=subject)