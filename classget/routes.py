from flask import render_template, url_for, redirect, request
from classget import app, db, bcrypt
from classget.forms import RegistrationForm, LoginForm, UpdateAccountForm, TypeTestForm
from classget.models import User, Post
from flask_login import login_user, current_user, logout_user, login_required
import random


@app.route("/")
def mainpage():
    return render_template('mainpage.html')


@app.route("/createaccount", methods=['GET', 'POST'])
def createaccount():
    if current_user.is_authenticated:
        return redirect(url_for('mainpage'))
    # ----create user with data from RegistrationForm----
    form = RegistrationForm()
    if form.validate_on_submit():
        hashed_pw = bcrypt.generate_password_hash(form.password.data).decode('utf-8')
        user = User(username=form.username.data, iduser=form.iduser.data, password=hashed_pw,
                    faculty=form.faculty.data, year=form.year.data)
        db.session.add(user)
        db.session.commit()
        # ----complete creating user-----
        # ----login and send user to typetest----
        user = User.query.filter_by(iduser=form.iduser.data).first()
        login_user(user)
        return redirect(url_for('typetest'))
    return render_template('createaccount.html', title='Register', form=form)


@app.route("/login", methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('mainpage'))
    # ----login with data from LoginForm----
    form = LoginForm()
    login_error = 0
    if form.validate_on_submit():
        user = User.query.filter_by(iduser=form.iduser.data).first()
        if user and bcrypt.check_password_hash(user.password, form.password.data):
            login_user(user, remember=form.remember.data)
            next_page = request.args.get('next')
            return redirect(next_page) if next_page else redirect(url_for('mainpage'))
        else:
            login_error = 1
    return render_template('login.html', title='login', form=form, login_error=login_error)


@app.route("/updateaccount", methods=['GET', 'POST'])
@login_required
def updateaccount():
    form = UpdateAccountForm()
    password_error = 0
    if form.validate_on_submit():
        if bcrypt.check_password_hash(current_user.password, form.current_password.data):
            current_user.username = form.username.data
            current_user.faculty = form.faculty.data
            current_user.year = form.year.data
            db.session.commit()
            if form.new_password.data:
                current_user.password = bcrypt.generate_password_hash(form.new_password.data).decode('utf-8')
                db.session.commit()
            return redirect(url_for('mypage'))
        else:
            password_error = 1
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
def typetest():
    form = TypeTestForm()
    # すでにキャラ診断した人は結果ページに送る
    if current_user.type != 'none':
        return redirect(url_for('typeresult'))
    if form.validate_on_submit():
        # formのdataから属性ごとにスコアを集計
        kaisou_score = int(form.Q1.data) + int(form.Q10.data)
        penguin_score = int(form.Q2.data) + int(form.Q9.data)
        iruka_score = int(form.Q3.data) + int(form.Q8.data)
        kame_score = int(form.Q4.data) + int(form.Q7.data)
        taco_score = int(form.Q5.data) + int(form.Q6.data)
        scores = {'kaisou': kaisou_score, 'penguin': penguin_score, 'iruka': iruka_score,
                  'kame': kame_score, 'taco': taco_score}
        # 一番高いスコアのキャラを入れる（複数の場合は共同１位のうちランダムで）
        max_score = max(scores.items(), key=lambda x: x[1])
        list_max = []
        for key, value in scores.items():
            if value == max_score[1]:
                list_max.append(key)
        current_user.type = random.choice(list_max)
        db.session.commit()
        return redirect(url_for('typeresult'))
    return render_template('typetest.html', form=form)


@app.route("/typeresult", methods=['GET'])
def typeresult():
    return render_template('typeresult.html')


@app.route("/mypage")
@login_required
def mypage():
    image_file = url_for('static', filename='img/profile_pics/' + current_user.type + '.jpg')
    return render_template('mypage.html', title='mypage', image_file=image_file)


