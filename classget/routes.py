from flask import render_template, url_for, redirect, request
from classget import app, db, bcrypt
from classget.forms import RegistrationForm, LoginForm, UpdateAccountForm, ReviewForm
from classget.models import User, Subject, Review
from flask_login import login_user, current_user, logout_user, login_required
import random


@app.route("/")
def mainpage():
    return render_template('mainpage.html')


@app.route("/createaccount", methods=['GET', 'POST'])
def createaccount():
    if current_user.is_authenticated:
        return redirect(url_for('mainpage'))
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
        return redirect(url_for('typetest'))
    return render_template('createaccount.html', title='Register', form=form)


@app.route("/login", methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('mainpage'))
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
            return redirect(next_page) if next_page else redirect(url_for('mainpage'))
        # パスワードが一致しない場合：パスワードエラー
        else:
            login_error = 1
    return render_template('login.html', title='login', form=form, login_error=login_error)


@app.route("/updateaccount", methods=['GET', 'POST'])
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
            return redirect(url_for('mypage'))
        # 入力したPWが現在PWと一致しない場合：パスワードエラー
        else:
            password_error = 1
    # ページを読み取った場合に書いてあるデフォルトユーザー情報
    elif request.method == 'GET':
        form.username.data = current_user.username
        form.faculty.data = current_user.faculty
        form.year.data = current_user.year

    return render_template('updateaccount.html', title='update account', form=form, password_error=password_error)


@app.route("/logout")
def logout():
    logout_user()
    return redirect(url_for('mainpage'))


@app.route("/typetest", methods=['GET', 'POST'])
@login_required
def typetest():
    question = ['Q01.初対面の人と友達になるのが得意だ。', 'Q02.人助けをしたり、されたりすることが多い。', 'Q03.課題の期限は守るほうだし、遅刻もしない。',
                'Q04.普段ストレスや不安をなかなか感じないブッダみたいな性格を持っている。', 'Q05.芸術や美術は結構好きだ。',
                'Q06.しばしば新しい冒険についてのアイデアが思い浮かぶ。', 'Q07.他の人にどう思われるかなんて気にしない超マイウェイ。',
                'Q08.人との約束のためなら無理もする。', 'Q09.みんなで何かを成し遂げることが好きだ。', 'Q10.面白い話で場を盛り上げることができる。']
    # すでにキャラ診断した人は結果ページに送る
    if current_user.type != 'none':
        return redirect(url_for('typeresult'))
    if request.method == 'POST':
        # formのdataから属性ごとにスコアを集計
        kaisou_score = int(request.form['Q1']) + int(request.form['Q10'])
        penguin_score = int(request.form['Q2']) + int(request.form['Q9'])
        iruka_score = int(request.form['Q3']) + int(request.form['Q8'])
        kame_score = int(request.form['Q4']) + int(request.form['Q7'])
        taco_score = int(request.form['Q5']) + int(request.form['Q6'])
        scores = {'kaisou': kaisou_score, 'penguin': penguin_score, 'iruka': iruka_score,
                  'kame': kame_score, 'taco': taco_score}
        print(kaisou_score, penguin_score, iruka_score, kame_score, taco_score)
        # 一番高いスコアのキャラを入れる（複数の場合は共同１位のうちランダムで）
        max_score = max(scores.items(), key=lambda x: x[1])
        list_max = []
        for key, value in scores.items():
            if value == max_score[1]:
                list_max.append(key)
        current_user.type = random.choice(list_max)
        db.session.commit()
        return redirect(url_for('typeresult'))
    return render_template('typetest.html', question=question)


@app.route("/typeresult", methods=['GET'])
@login_required
def typeresult():
    return render_template('typeresult.html')


@app.route("/mypage")
@login_required
def mypage():
    image_file = url_for('static', filename='img/profile_pics/' + current_user.type + '.png')
    return render_template('mypage.html', title='mypage', image_file=image_file)


@app.route("/searchresult")
def searchresult():
    subject = Subject.query.all()
    return render_template('searchresult.html', title='検索結果', subject=subject)


@app.route("/classinfo/<int:subject_id>", methods=["GET", "POST"])
def classinfo(subject_id):
    # PKのIDでその授業の情報を持ってくる
    subject = Subject.query.get_or_404(subject_id)
    form = ReviewForm()
    # 授業IDでその授業のレビューを全部持ってくる
    reviews = Review.query.filter_by(subject_id=subject_id).all()
    # レビューフォームを提出したら
    if form.validate_on_submit():
        # ログインしている場合
        if current_user.is_authenticated:
            # キーワードをListから一つのStringにする
            keywords = ' '.join([str(i) for i in form.keyword.data])
            # レビューをデータベースに入れる
            review = Review(title=form.title.data, rating=form.rating.data, content=form.content.data,
                            keyword=keywords, author=current_user, subject_id=subject_id)
            db.session.add(review)
            db.session.commit()
            return redirect(url_for('classinfo', subject_id=subject_id))
        # ログインしていない場合→ログイン画面へ
        else:
            return redirect(url_for('login'))
    return render_template('classinfo.html', title=subject.name, subject=subject, form=form, reviews=reviews,
                           enumerate=enumerate)