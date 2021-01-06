from flask import render_template, url_for, redirect, request
from classget import app, db, bcrypt
from classget.forms import RegistrationForm, LoginForm, UpdateAccountForm
from classget.models import User, Post
from flask_login import login_user, current_user, logout_user, login_required


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


@app.route("/logout")
def logout():
    logout_user()
    return redirect(url_for('mainpage'))


@app.route("/mypage")
@login_required
def mypage():
    image_file = url_for('static', filename='img/profile_pics/' + current_user.type + '.jpg')
    return render_template('mypage.html', title='mypage', image_file=image_file)


@app.route("/updateaccount", methods=['GET', 'POST'])
@login_required
def updateaccount():
    form = UpdateAccountForm()
    if form.validate_on_submit():
        current_user.username = form.username.data
        current_user.faculty = form.faculty.data
        current_user.year = form.year.data
        print(form.year.data)
        db.session.commit()
        if form.new_password.data:
            current_user.password = bcrypt.generate_password_hash(form.new_password.data).decode('utf-8')
            db.session.commit()
        return redirect(url_for('mypage'))
    elif request.method == 'GET':
        form.username.data = current_user.username
        form.faculty.data = current_user.faculty
        form.year.data = current_user.year
    #     if bcrypt.check_password_hash(current_user.password, form.current_password.data):

    return render_template('updateaccount.html', title='update account', form=form)


@app.route("/typetest")
def typetest():
    return render_template('typetest.html')