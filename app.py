from flask import Flask, render_template, url_for, request, redirect, send_file, session
from flask_sqlalchemy import SQLAlchemy
from models import Verification, Admin
from flask_session import Session  # https://pythonhosted.org/Flask-Session
import datetime as dt
import os
import msal
import app_config
import uuid
import json
import requests


app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///notilyze.db'
app.config.from_object(app_config)
db = SQLAlchemy(app)
Session(app)
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


class ApiUser(db.Model):
    api_id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, primary_key=True)


class API(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable= False)
    input_fields = db.Column(db.String, nullable=True)
    href = db.Column(db.String(400), nullable=False)


@app.route('/', methods=['GET', 'POST'])
@app.route('/signin', methods=['GET', 'POST'])
def sign_in():
    v.SignOut()
    session["state"] = str(uuid.uuid4())
    # Technically we could use empty list [] as scopes to do just sign in,
    # here we choose to also collect end user consent upfront
    auth_url = f'https://login.microsoftonline.com/a111daf6-3065-41cb-9b63-ab81be54bafd/oauth2/v2.0/authorize?' \
        f'client_id=52e6e094-6eb2-4dfa-8726-2b6843bd3205&response_type=code&' \
        f'redirect_uri=https://notilyzeclientapp.herokuapp.com/getAToken&' \
        f'scope=User.ReadBasic.All+offline_access+openid+profile&state={session["state"]}'
    return render_template('sign_in.html', auth_url=auth_url)


@app.route(app_config.REDIRECT_PATH)
def authorized():
    if request.args.get('state') != session.get("state"):
        return redirect('/client_page')
    if request.args.get('code'):
        cache = _load_cache()
        result = _build_msal_app(cache=cache).acquire_token_by_authorization_code(
            request.args['code'],
            scopes=app_config.SCOPE,
            redirect_uri='https://notilyzeclientapp.herokuapp.com/getAToken')
        session["user"] = result.get("id_token_claims")
        _save_cache(cache)
    return redirect('/client_page')


@app.route("/client_page", methods=['GET', 'POST'])
def tmp_client():
    if not session.get("user"):
        return redirect('/signin')
    else:
        check = User.query.filter_by(e_mail=session["user"].get("name")).first()
        if check is None:
            new_user = User(e_mail=session["user"].get("name"), password='tmp')
            db.session.add(new_user)
            db.session.commit()
            user_id = User.query.filter_by(e_mail=session["user"].get("name")).first().id
        else:
            user_id = User.query.filter_by(e_mail=session["user"].get("name")).first().id
        v.Verificate(user_id)
        return redirect(f'/client_page/{user_id}')


@app.route("/client_page/<int:uid>", methods=['GET', 'POST'])
def client(uid: int):
    if v.verificated is True and v.id == uid:
        user = User.query.filter_by(id=uid).first()
        user.last_login = dt.datetime.now()
        db.session.commit()
        return render_template('client.html', email=user.e_mail, user=user, info_username=f"Username: {user.e_mail}",
                               info_login=f"Last log in: {str(user.last_login).split('.')[0]}")
    else:
        return redirect('/signin')


@app.route("/client_page/apis")
def apis(uid: int):
    if v.verificated is True and v.id == uid:
        user = User.query.filter_by(id=uid).first()
        users_apis = API.query.filter(ApiUser.user_id == user.id).filter(API.id == ApiUser.api_id)
        return render_template('apis.html', api=users_apis, email=user.e_mail, user=user)
    else:
        return redirect('/signin')


@app.route("/client_page/<int:uid>/<int:aid>/api", methods=['GET', 'POST'])
def api(uid: int, aid: int):
    if v.verificated is True and v.id == uid:
        user = User.query.filter_by(id=uid).first()
        api = API.query.filter_by(id=aid).first()
        inputs = str(api.input_fields).split(',')
        if request.method == 'POST':
            try:
                headers = {
                    'Content-Type': 'application/x-www-form-urlencoded',
                    'Accept': 'application/json',
                }

                data = {
                    'grant_type': 'password',
                    'username': 'hro',
                    'password': 'o5PyWC@Mis85'
                }

                response = requests.post('https://devanalytics-notilyze.saasnow.com/SASLogon/oauth/token',
                                         headers=headers,
                                         data=data, auth=('hroapp', 'P6UzU5C4Wr8c'))
                if response.status_code is 200:
                    result_token = json.loads(response.text)["access_token"]

                    headers = {
                        'Accept': 'application/vnd.sas.microanalytic.module.step.output+json,application/json',
                        'Content-Type': 'application/json',
                        'Authorization': 'Bearer ' + result_token,
                    }

                    data_from_forms = ''
                    for i in inputs:
                        if str(request.form[i]).isdecimal():
                            data_from_forms += "{" + f'"name": "{i}", "value": {str(request.form[i])}' + "},"
                        else:
                            data_from_forms += "{" + f'"name": "{i}", "value": "{str(request.form[i])}"' + "},"
                    data = '{"inputs": [' + f'{data_from_forms}' + ']}'

                    response = requests.post(
                            api.href,
                            headers=headers, data=data)
                    result = json.loads(response.text)["outputs"]
                    return render_template('api.html', inputs=inputs, email=user.e_mail, user=user,
                                           status_code=str(response.status_code), respond=result)
            except:
                return render_template('api.html', inputs=inputs, email=user.e_mail, user=user, status_code='error',
                                       respond="Seems like you've entered invalid credentials.")
        return render_template('api.html', email=user.e_mail, user=user, status_code="", respond="")
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
        except:
            return "Error"
    return render_template('sign_in_for_admin.html')


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
        return render_template('folder.html', files=files)
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
        except:
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
            except:
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
                return redirect(f'/client_page/{v.id}/upload_info/1')
            else:
                return redirect(f'/client_page/{v.id}/upload_info/0')
    else:
        return redirect('/signin')


@app.route("/client_page/<int:uid>/upload_info/<int:eid>")
def upload_info(uid: int, eid: int):
    if v.verificated is True and v.id is uid:
        user = User.query.filter_by(id=uid).first()
        if eid == 0:
            return render_template('unsuccessful_upload.html', email=user.e_mail, user=user)
        elif eid == 1:
            return render_template('successful_upload.html', email=user.e_mail, user=user)
        else:
            return redirect('/signin')
    else:
        return redirect('/signin')


@app.route('/admin_page/remove_access')
def removing_access():
    if a.verificated:
        return render_template('remove_access.html', users=User.query.all())
    else:
        return redirect('/admin')


@app.route('/admin_page/remove_access/<int:uid>')
def accesses(uid: int):
    if a.verificated:
        username = User.query.filter_by(id=uid).first().e_mail
        users_reports = Report.query.filter(UsersReport.user_id == uid).filter(Report.id == UsersReport.report_id).all()
        return render_template('removing_accesses.html', username=username, uid=uid, reports=users_reports)
    else:
        return redirect('/admin')


@app.route('/admin_page/remove_access/<int:uid>/<int:rid>')
def remove(uid: int, rid: int):
    if a.verificated is True:
        try:
            user_report = UsersReport.query.filter_by(user_id=uid) \
                .filter_by(report_id=rid).first()
            db.session.delete(user_report)
            db.session.commit()
            return redirect(f'/admin_page/remove_access/{uid}')
        except:
            return render_template('unsuccessful_removing.html')
    else:
        return redirect('/admin')


@app.route('/admin_page/add_report', methods=['GET', 'POST'])
def add_report():
    if a.verificated:
        if request.method == 'POST':
            name = request.form['name']
            url = request.form['url']
            uri = request.form['uri']
            if name != '' and url != '' and uri != '':
                report = Report(name=name, url=url, report_uri=uri)
                try:
                    db.session.add(report)
                    db.session.commit()
                    return render_template('successful_addition_of_report.html')
                except:
                    return render_template('unsuccessful_addition_of_report.html')
            else:
                return render_template('unsuccessful_addition_of_report.html')
        return render_template('add_report.html')
    else:
        return redirect('/admin')


def _load_cache():
    cache = msal.SerializableTokenCache()
    if session.get("token_cache"):
        cache.deserialize(session["token_cache"])
    return cache


def _build_msal_app(cache=None, authority=None):
    return msal.ConfidentialClientApplication(
        app_config.CLIENT_ID, authority=authority or app_config.AUTHORITY,
        client_credential=app_config.CLIENT_SECRET, token_cache=cache)


def _save_cache(cache):
    if cache.has_state_changed:
        session["token_cache"] = cache.serialize()


if __name__ == "__main__":
    app.run()(debug=True)
