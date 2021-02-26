import os

from flask import Blueprint, render_template, session, request, send_from_directory, current_app
from flask_login import current_user
from sqlalchemy import or_

from classget.main.forms import SearchClassForm
from classget.models import Subject, get_count, Review

main = Blueprint('main', __name__)


@main.route("/", methods=["GET", "POST"])
def mainpage():
    form = SearchClassForm()
    return render_template('main/mainpage.html', form=form)


@main.route("/searchresult", methods=['GET', 'POST'])
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
        day = [0, 0, 0, 0, 0, 0]
        for i in range(len(session['form.day.data'])):
            day[i] = session['form.day.data'][i]
        result = result.filter(or_(Subject.time.like(f'%{day[0]}%'), Subject.time.like(f'%{day[1]}%'),
                                   Subject.time.like(f'%{day[2]}%'), Subject.time.like(f'%{day[3]}%'),
                                   Subject.time.like(f'%{day[4]}%'), Subject.time.like(f'%{day[5]}%')))
    # 時限
    if session['form.time.data']:
        time = [0, 0, 0, 0, 0, 0]
        for i in range(len(session['form.time.data'])):
            time[i] = session['form.time.data'][i]
        result = result.filter(or_(Subject.time.like(f'%{time[0]}%'), Subject.time.like(f'%{time[1]}%'),
                                   Subject.time.like(f'%{time[2]}%'), Subject.time.like(f'%{time[3]}%'),
                                   Subject.time.like(f'%{time[4]}%'), Subject.time.like(f'%{time[5]}%')))
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
    return render_template('main/searchresult.html', title='検索結果', result=result, get_count=get_count, form=form,
                           Review=Review, result_num=result_num)


@main.route('/about_us')
def aboutus():
    return render_template('main/aboutus.html', title='About Us')


@main.route('/ham_menu', methods=['POST'])
def ham_menu():
    action = request.form['action']
    if action == 'show_menu':
        if current_user.is_authenticated:
            return render_template('main/show_ham_menu.html')
        else:
            return render_template('main/nouser_show_ham_menu.html')
    elif action == 'close_menu':
        return render_template('main/close_ham_menu.html')
    else:
        pass


@main.route('/favicon.ico')
def favicon():
    return send_from_directory(os.path.join(current_app.root_path, 'static/img/icon'), 'favicon.ico',
                               mimetype='image/vnd.microsoft.icon')


@main.route('/sw.js')
def sw_js():
    return send_from_directory(os.path.join(current_app.root_path, 'static/js'), 'sw.js')


@main.route('/mobile_install')
def mobile_install():
    return render_template('main/mobile_install.html')
