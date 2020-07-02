from flask import Flask, render_template, url_for, request, redirect, send_file
from flask_sqlalchemy import SQLAlchemy
from models import Verification, Admin
import datetime as dt
import os


app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///notilyze.db'
db = SQLAlchemy(app)
v = Verification()
a = Admin()


class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    e_mail = db.Column(db.String(100), nullable=False)
    password = db.Column(db.String(100), nullable=False)
    last_login = db.Column(db.DateTime, nullable=True)

    def __repr__(self):
        return '<User %r>' % self.id


class File(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, nullable=False)
    name = db.Column(db.String(150), nullable=False)
    data = db.Column(db.LargeBinary, nullable=False)

    def __repr__(self):
        return '<File %r>' % self.name


class Report(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    url = db.Column(db.String(400), nullable=False)
    report_uri = db.Column(db.String(400), nullable=False)

    def __repr__(self):
        return '<Report %r>' % self.id


class UsersReport(db.Model):
    user_id = db.Column(db.Integer, primary_key=True)
    report_id = db.Column(db.Integer, primary_key=True)

    def __repr__(self):
        return '<ReportUser %r>' % self.report_id


@app.route('/', methods=['GET', 'POST'])
@app.route('/signin', methods=['GET', 'POST'])
def sign_in():
    v.SignOut()
    if request.method == 'POST':
        try:
            email = request.form['email']
            password = request.form['password']
            user = User.query.filter_by(e_mail=email).filter_by(password=password).first()
            user.last_login = dt.datetime.now()
            db.session.commit()
            v.Verificate(user.id)
            return redirect(f'/client_page/{user.id}')
        except NotImplemented:
            return "Error"
    return render_template('sign_in.html')


@app.route("/registration", methods=['GET', 'POST'])
def registration():
    v.SignOut()
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']
        user = User(e_mail=email, password=password)
        try:
            db.session.add(user)
            db.session.commit()
            return redirect('/signin')
        except NotImplemented:
            return "Error"
    else:
        return render_template('registration.html')


@app.route("/client_page")
@app.route("/client_page/<int:uid>", methods=['GET', 'POST'])
def client(uid: int):
    if v.verificated is True and v.id == uid:
        user = User.query.filter_by(id=uid).first()
        return render_template('client.html', email=user.e_mail, user=user, info_username=f"Username: {user.e_mail}",
                               info_login=f"Last log in: {str(user.last_login).split('.')[0]}")
    else:
        return redirect('/signin')


@app.route("/client_page/<int:uid>/reports", methods=['GET', 'POST'])
def reports(uid: int):
    if v.verificated is True and v.id == uid:
        user = User.query.filter_by(id=uid).first()
        users_reports = Report.query.filter(UsersReport.user_id == user.id).filter(Report.id == UsersReport.report_id)
        return render_template('reports.html', report=users_reports, email=user.e_mail, user=user)
    else:
        return redirect('/signin')


@app.route("/report/r<int:rid>/u<int:uid>", methods=['GET', 'POST'])
def report(rid: int, uid: int):
    if v.verificated is True and v.id == uid:
        user = User.query.filter_by(id=uid).first()
        user_report = Report.query.filter_by(id=rid).first()
        return render_template('report.html', email=user.e_mail, user=user, rep=user_report)
    else:
        return redirect('/signin')


@app.route("/client_page/<int:uid>/uploadfile", methods=['GET', 'POST'])
def upload_file(uid: int):
    if v.verificated is True and v.id == uid:
        user = User.query.filter_by(id=uid).first()
        return render_template('upload.html', email=user.e_mail, user=user)
    else:
        return redirect('/signin')


@app.route('/admin', methods=['GET', 'POST'])
def admin():
    a.SignOut()
    if request.method == 'POST':
        try:
            email = request.form['email']
            password = request.form['password']
            if email == 'admin@admin.notilyze' and password == 'password':
                a.verificated = True
                return redirect(f'/admin_page')
        except NotImplemented:
            return "Error"
    return render_template('sign_in.html')


@app.route('/admin_page', methods=['GET', 'POST'])
def admin_page():
    if a.verificated:
        return render_template('admin.html')
    else:
        return redirect('/admin')


@app.route('/admin_page/file_manager')
def file_manager():
    if a.verificated:
        return render_template('file_manager.html', users=User.query.all())
    else:
        return redirect('/admin')


@app.route('/admin_page/file_manager/<int:uid>')
def folder(uid: int):
    if a.verificated:
        files = File.query.filter_by(user_id=uid).all()
        return render_template('folder.html', folders=files)
    else:
        return redirect('/admin')


@app.route('/admin_page/file_manager/download/<int:fid>')
def download(fid: int):
    if a.verificated is True:
        try:
            db_file = File.query.filter_by(id=fid).first()
            file_data = db_file.data
            ready_file = open(db_file.name, 'wb')
            ready_file.write(file_data)
            ready_file.close()
            result = send_file(f'{db_file.name}', attachment_filename=db_file.name)
            os.remove(db_file.name)
            return result
        except NotImplemented:
            return redirect('/admin_page')
    else:
        return redirect('/admin')


@app.route('/admin_page/about_access', methods=['GET', 'POST'])
def about_access():
    if a.verificated:
        if request.method == 'POST':
            try:
                chose_user = request.form['client_id']
                chose_report = request.form['report_id']
                users_report = UsersReport(user_id=chose_user, report_id=chose_report)
                check = UsersReport.query.filter_by(user_id=users_report.user_id)\
                    .filter_by(report_id=users_report.report_id).first()
                if check is None:
                    db.session.add(users_report)
                    db.session.commit()
            except NotImplemented:
                return redirect('/admin_page/about_access')
    else:
        return redirect('/admin')
    return render_template('giving_access.html', clients=User.query.all(), reports=Report.query.all())


@app.route("/upload", methods=['GET', 'POST'])
def upload():
    if v.verificated is True:
        permitted_files = ['csv', 'xlsx', 'CSV', 'XLSX']
        if request.method == 'POST':
            file = request.files['file']
            if file and file.filename.split('.')[1] in permitted_files:
                new_file = File(name=file.filename, user_id=v.id, data=file.read())
                db.session.add(new_file)
                db.session.commit()
                return redirect(f'/client_page/{v.id}')
            else:
                return redirect(f'/client_page/{v.id}/uploadfile')
        else:
            return redirect(f'/client_page/{v.id}/uploadfile')
    else:
        return redirect('/signin')


if __name__ == "__main__":
    app.run()(debug=True)
