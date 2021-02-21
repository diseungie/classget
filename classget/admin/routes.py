from flask import Blueprint, url_for, request, render_template
from flask_login import current_user
from werkzeug.utils import redirect

from classget import db
from classget.admin.forms import UpdateClassForm
from classget.models import Subject

admin = Blueprint('admin', __name__)


@admin.route("/updateclass/<int:subject_id>", methods=["GET", "POST"])
def updateclass(subject_id):
    # UserIDが「admin」の場合だけ
    if current_user.is_authenticated and current_user.iduser == 'admin':
        subject = Subject.query.get_or_404(subject_id)
        form = UpdateClassForm()
        # 修正フォームが提出されたら、DBに適用する
        if form.validate_on_submit():
            subject.sort = form.sort.data
            subject.term = form.term.data
            subject.time = form.time.data
            subject.name = form.name.data
            subject.teacher = form.teacher.data
            subject.language = form.language.data
            subject.draw = form.draw.data
            subject.keyword = form.keyword.data
            db.session.commit()
            return redirect(url_for('reviews.classinfo', subject_id=subject_id))
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
            return render_template('admin/update_class.html', subject=subject, form=form)
    else:
        return 'access denied'


@admin.route("/createclass", methods=["GET", "POST"])
def createclass():
    form = UpdateClassForm()
    if current_user.is_authenticated and current_user.iduser == 'admin':
        if form.validate_on_submit():
            new_subject = Subject(sort=form.sort.data, term=form.term.data, time=form.time.data, name=form.name.data,
                                  teacher=form.teacher.data, language=form.language.data, draw=form.draw.data,
                                  keyword=form.keyword.data)
            db.session.add(new_subject)
            db.session.commit()
            return redirect(url_for('reviews.classinfo', subject_id=new_subject.id))
    else:
        return 'access denied'

    return render_template('admin/createclass.html', form=form)

@admin.route("/report.html")
def report_html():
    return render_template('report.html')
