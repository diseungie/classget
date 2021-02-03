from flask import render_template, url_for, redirect, request, session
from werkzeug.exceptions import abort
from classget import app, db, bcrypt
from classget.forms import RegistrationForm, LoginForm, UpdateAccountForm, ReviewForm, SearchClassForm, UpdateClassForm
from classget.models import User, Subject, Review, Like, get_count
from flask_login import login_user, current_user, logout_user, login_required
from sqlalchemy import or_
import random


@app.route("/", methods=["GET", "POST"])
def mainpage():
    form = SearchClassForm()
    return render_template('mainpage.html', form=form)


@app.route("/searchresult", methods=['GET', 'POST'])
def searchresult():
    form = SearchClassForm()
    result = Subject.query
    if form.validate_on_submit():
        session['form.sort.data'] = form.sort.data
        session['form.term.data'] = form.term.data
        session['form.day.data'] = form.day.data
        session['form.time.data'] = form.time.data
        session['form.draw.data'] = form.draw.data
        session['form.title.data'] = form.title.data
        session['form.keyword.data'] = form.keyword.data
    # 所属
    if session['form.sort.data']:
        result = result.filter(Subject.sort.in_(session['form.sort.data']))
    # 開講区分
    if session['form.term.data']:
        result = result.filter(Subject.term.in_(session['form.term.data']))
    # 曜日
    if session['form.day.data']:
        day = [0, 0, 0, 0, 0]
        for i in range(len(session['form.day.data'])):
            day[i] = session['form.day.data'][i]
        result = result.filter(or_(Subject.time.like(f'%{day[0]}%'), Subject.time.like(f'%{day[1]}%'),
                                   Subject.time.like(f'%{day[2]}%'), Subject.time.like(f'%{day[3]}%'),
                                   Subject.time.like(f'%{day[4]}%')))
    # 時限
    if session['form.time.data']:
        time = [0, 0, 0, 0, 0]
        for i in range(len(session['form.time.data'])):
            time[i] = session['form.time.data'][i]
        result = result.filter(or_(Subject.time.like(f'%{time[0]}%'), Subject.time.like(f'%{time[1]}%'),
                                   Subject.time.like(f'%{time[2]}%'), Subject.time.like(f'%{time[3]}%'),
                                   Subject.time.like(f'%{time[4]}%')))
    # 抽選
    if session['form.draw.data']:
        result = result.filter(Subject.draw.in_(session['form.draw.data']))
    # 授業名
    if session['form.title.data']:
        result = result.filter(Subject.name.like(f"%{session['form.title.data']}%"))
    # キーワード
    if session['form.keyword.data']:
        for keyword in session['form.keyword.data']:
            result = result.filter(Subject.keyword.notlike(f'%{keyword}%'))
    # 検索結果を１０個ずつ分けてページを作る
    page = request.args.get('page', 1, type=int)
    result_num = get_count(result)
    result = result.paginate(page=page, per_page=10)
    if not result:
        result = "検索結果がありません。"
    return render_template('searchresult.html', title='検索結果', result=result, get_count=get_count, form=form,
                           Review=Review, result_num=result_num)


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
            return redirect(url_for('mypage', my_term='春'))
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
    question = ['初対面の人と友達になるのが得意だ。', '人助けをしたり、されたりすることが多い。', '課題の期限は守るほうだし、遅刻もしない。',
                '普段ストレスや不安をなかなか感じないブッダみたいな性格を持っている。', '芸術や美術は結構好きだ。',
                'しばしば新しい冒険についてのアイデアが思い浮かぶ。', '他の人にどう思われるかなんて気にしない超マイウェイ。',
                '人との約束のためなら無理もする。', 'みんなで何かを成し遂げることが好きだ。', '面白い話で場を盛り上げることができる。']
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
        return redirect(url_for('typeresult'))
    return render_template('typetest.html', question=question)


@app.route("/typeresult", methods=['GET'])
@login_required
def typeresult():
    recommended_subjects = current_user.recommend_by_likes()
    type_number = get_count(User.query.filter_by(type=current_user.type))
    user_number = get_count(User.query)
    type_com = get_count(User.query.filter_by(type=current_user.type, faculty='商学部'))
    type_eco = get_count(User.query.filter_by(type=current_user.type, faculty='経済学部'))
    type_law = get_count(User.query.filter_by(type=current_user.type, faculty='法学部'))
    type_soc = get_count(User.query.filter_by(type=current_user.type, faculty='社会学部'))
    type_proportion = (type_number/user_number)*100
    com_proportion = (type_com/type_number)*100
    eco_proportion = (type_eco / type_number) * 100
    law_proportion = (type_law / type_number) * 100
    soc_proportion = (type_soc / type_number) * 100
    return render_template('typeresult.html', recommended_subjects=recommended_subjects, type_pp=type_proportion,
                           com_pp=com_proportion, eco_pp=eco_proportion, law_pp=law_proportion, soc_pp=soc_proportion)


@app.route("/mypage/<my_term>")
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
    return render_template('mypage.html', title='mypage', image_file=image_file, liked=liked_subject, timetable=timetable)


@app.route("/classinfo/<int:subject_id>", methods=["GET", "POST"])
def classinfo(subject_id):
    # PKのIDでその授業の情報を持ってくる
    subject = Subject.query.get_or_404(subject_id)
    page = request.args.get('page', 1, type=int)
    form = ReviewForm()
    subject_keyword = subject.keyword.split('　')
    # 授業IDでその授業のレビューを全部持ってくる
    reviews = Review.query.filter_by(subject_id=subject_id).order_by(Review.date_posted.desc())\
        .paginate(page=page, per_page=5)
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
            return redirect(request.referrer)
        # ログインしていない場合→ログイン画面へ
        else:
            return redirect(url_for('login'))
    return render_template('classinfo.html', title=subject.name, subject=subject, form=form, reviews=reviews,
                           enumerate=enumerate, subject_keyword=subject_keyword, get_count=get_count, Review=Review)


@app.route("/delete_review/<int:review_id>_<int:subject_id>", methods=["GET"])
def delete_review(review_id, subject_id):
    review = Review.query.get_or_404(review_id)
    if review.author != current_user:
        abort(403)
    db.session.delete(review)
    db.session.commit()
    return redirect(url_for('classinfo', subject_id=subject_id))


@app.route('/like', methods=['POST'])
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


@app.route("/updateclass/<int:subject_id>", methods=["GET", "POST"])
def updateclass(subject_id):
    # UserIDが「admin」の場合だけ
    if current_user.iduser == 'admin':
        subject = Subject.query.get_or_404(subject_id)
        form = UpdateClassForm()
        # 修正フォームが提出されたら、DBに適用する
        if form.validate_on_submit():
            subject.sort=form.sort.data
            subject.term=form.term.data
            subject.time=form.time.data
            subject.name=form.name.data
            subject.teacher=form.teacher.data
            subject.language=form.language.data
            subject.draw=form.draw.data
            subject.keyword=form.keyword.data
            db.session.commit()
            return redirect(url_for('classinfo', subject_id=subject_id))
        # ページを開いたら既存の情報がすでに入っている
        elif request.method == 'GET':
            form.sort.data = subject.sort
            form.term.data = subject.term
            form.time.data = subject.time
            form.name.data = subject.name
            form.teacher.data = subject.teacher
            form.language.data = subject.language
            form.draw.data = subject.draw
            form.keyword.data = subject.keyword
            return render_template('update_class.html', subject=subject, form=form)
    else:
        return 'access denied'


@app.route("/createclass", methods=["GET", "POST"])
def createclass():
    form = UpdateClassForm()
    if current_user.iduser == 'admin':
        if form.validate_on_submit():
            new_subject = Subject(sort=form.sort.data, term=form.term.data, time=form.time.data, name=form.name.data,
                                  teacher=form.teacher.data, language=form.language.data, draw=form.draw.data,
                                  keyword=form.keyword.data)
            db.session.add(new_subject)
            db.session.commit()
            return redirect(url_for('classinfo', subject_id=new_subject.id))
    else:
        return 'access denied'

    return render_template('createclass.html', form=form)
