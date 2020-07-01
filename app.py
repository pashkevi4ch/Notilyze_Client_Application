from flask import Flask, render_template, url_for, request, redirect, flash
from flask_sqlalchemy import SQLAlchemy
from models import Verification
import os


app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///notilyze.db'
app.config['SQLALCHEMY_TRACK_MODIFICATION  '] = False
db = SQLAlchemy(app)
v = Verification()


class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    e_mail = db.Column(db.String(100), nullable=False)
    password = db.Column(db.String(100), nullable=False)

    def __repr__(self):
        return '<User %r>' % self.id


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
            v.Verificate(user.id)
            return redirect(f'/client_page/{user.id}')
        except:
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
        except:
            return "Error"
    else:
        return render_template('registration.html')


@app.route("/client_page/<int:id>", methods=['GET', 'POST'])
def client(id: int):
    if v.verificated is True and v.id == id:
        user = User.query.filter_by(id=id).first()
        return render_template('client.html', email=user.e_mail, user=user)
    else:
        return redirect('/signin')


@app.route("/client_page/<int:id>/reports", methods=['GET', 'POST'])
def reports(id:int):
    if v.verificated is True and v.id == id:
        user = User.query.filter_by(id=id).first()
        reports = Report.query.filter(UsersReport.user_id == user.id).filter(Report.id == UsersReport.report_id)
        return render_template('reports.html', report=reports, email=user.e_mail, user=user)
    else:
        return redirect('/signin')


@app.route("/report/r<int:rid>/u<int:uid>", methods=['GET', 'POST'])
def report(rid: int, uid:int):
    if v.verificated is True and v.id == uid:
        user = User.query.filter_by(id=id).first()
        report = Report.query.filter_by(id=rid).first()
        return render_template('report.html', email=user.e_mail, user=user, rep=report)
    else:
        return redirect('/signin')


@app.route("/client_page/<int:id>/uploadfile", methods=['GET', 'POST'])
def upload_file(id: int):
    if v.verificated is True and v.id == id:
        user = User.query.filter_by(id=id).first()
        return render_template('upload.html', email=user.e_mail, user=user)
    else:
        return redirect('/signin')


@app.route("/upload", methods=['GET', 'POST'])
def upload():
    if v.verificated is True:
        permitted_files = ['csv', 'xlsx', 'CSV', 'XLSX']
        if request.method == 'POST':
            file = request.files['file']
            if file and file.filename.split('.')[1] in permitted_files:
                if os.path.exists(f'storage/{v.id}'):
                    upload_file = file.read()
                    new_file = open(f'storage/{v.id}/{file.filename}', 'wb')
                    new_file.write(upload_file)
                    new_file.close()
                    return redirect(f'/client_page/{v.id}')
                else:
                    os.mkdir(f'storage/{v.id}')
                    upload_file = file.read()
                    new_file = open(f'storage/{v.id}/{file.filename}', 'wb')
                    new_file.write(upload_file)
                    new_file.close()
                    return redirect(f'/client_page/{v.id}')
            else:
                return redirect(f'/client_page/{v.id}/uploadfile')
        else:
            return redirect(f'/client_page/{v.id}/uploadfile')
    else:
        return redirect('/signin')


if __name__ == "__main__":
    app.run()(debug=True)
