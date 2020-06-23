from flask import Flask, render_template, url_for, request, redirect
from flask_sqlalchemy import SQLAlchemy


app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///notilyze.db'
app.config['SQLALCHEMY_TRACK_MODIFICATION  '] = False
db = SQLAlchemy(app)


class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    e_mail = db.Column(db.String(100), nullable=False)
    password = db.Column(db.String(100), nullable=False)

    def __repr__(self):
        return '<User %r>' % self.id


@app.route('/', methods=['GET', 'POST'])
@app.route('/signin', methods=['GET', 'POST'])
def sign_in():
    if request.method == 'POST':
        try:
            email = request.form['email']
            password = request.form['password']
            user = User.query.filter_by(e_mail=email).filter_by(password=password).first()
            return redirect(f'/client_page/{user.id}')
        except:
            return "Error"
    return render_template('sign_in.html')


@app.route("/registration", methods=['GET', 'POST'])
def registration():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']
        user = User(e_mail=email, password=password)
        try:
            db.session.add(user)
            db.session.commit()
            return redirect('/')
        except:
            return "Error"
    else:
        return render_template('registration.html')


@app.route("/client_page/<int:id>", methods=['GET', 'POST'])
def client(id:int):
    user = User.query.filter_by(id=id).first()
    return render_template('client.html', email=user.e_mail)


if __name__ == "__main__":
    app.run()(debug=True)
