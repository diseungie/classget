import smtplib
import yaml
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

from flask import Blueprint, request, url_for, render_template
from flask_login import current_user
from werkzeug.exceptions import abort
from werkzeug.utils import redirect

from classget import db
from classget.admin.forms import UpdateClassForm
from classget.models import Subject, Review, get_count
from classget.reviews.forms import ReviewForm

reviews = Blueprint('reviews', __name__)
yml = yaml.load(open('classget/configure.yaml'), Loader=yaml.BaseLoader)


@reviews.route("/classinfo/<int:subject_id>", methods=["GET", "POST"])
def classinfo(subject_id):
    # PKのIDでその授業の情報を持ってくる
    subject = Subject.query.get_or_404(subject_id)
    page = request.args.get('page', 1, type=int)
    form = ReviewForm()
    subject_keyword = subject.keyword.split('　')
    # 授業IDでその授業のレビューを全部持ってくる
    reviews = Review.query.filter_by(subject_id=subject_id).order_by(Review.date_posted.desc())
    reviews_num = get_count(reviews)
    reviews = reviews.paginate(page=page, per_page=5)
    # レビューに基づいたおすすめ授業（３つ）
    recommended = subject.recommended_by_review()
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
            return redirect(url_for('users.login'))
    return render_template('reviews/classinfo.html', title=subject.name, subject=subject, form=form, reviews=reviews,
                           enumerate=enumerate, subject_keyword=subject_keyword, get_count=get_count, Review=Review,
                           recommended=recommended, reviews_num=reviews_num)


@reviews.route("/delete_review/<int:review_id>_<int:subject_id>", methods=["GET"])
def delete_review(review_id, subject_id):
    review = Review.query.get_or_404(review_id)
    if review.author != current_user:
        abort(403)
    db.session.delete(review)
    db.session.commit()
    return redirect(url_for('reviews.classinfo', subject_id=subject_id))


@reviews.route("/report/<int:subject_id>", methods=["GET", "POST"])
def report(subject_id):
    subject = Subject.query.get_or_404(subject_id)
    form = UpdateClassForm()
    if form.validate_on_submit():
        # 送信者情報
        sender = "machikado.cookingclass@gmail.com"
        sender_password = yml['email_pw']
        # メールサーバーにログイン
        s = smtplib.SMTP_SSL('smtp.gmail.com')
        s.login(sender, sender_password)
        # 宛名
        receiver = "hit.classget@gmail.com"
        # メール送信情報
        msg = MIMEMultipart('alternative')
        msg['Subject'] = "ユーザーからの授業情報修正の報告"
        msg['From'] = sender
        msg['To'] = receiver
        # メール本文
        content = f'''
        ・開講区分：{form.sort.data}
        ・学期：{form.term.data}
        ・曜日時限：{form.time.data}
        ・授業名：{form.name.data}
        ・教授名：{form.teacher.data}
        ・言語：{form.language.data}
        ・抽選：{form.draw.data}
        ・キーワード：{form.keyword.data}
        '''
        part2 = MIMEText(content, 'plain')
        msg.attach(part2)
        # メール送信、サーバーを閉じる
        s.sendmail(sender, receiver, msg.as_string())
        s.quit()
        return render_template('reviews/report_complete.html')
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
    return render_template('reviews/report.html', subject=subject, form=form, title='授業情報報告')
