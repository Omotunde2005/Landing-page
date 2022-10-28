from flask import Flask, render_template, request, url_for, redirect, flash, session
from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin, login_user, LoginManager
from flask_wtf import FlaskForm
from flask_ckeditor import CKEditorField, CKEditor
from wtforms import SubmitField, StringField, validators
from wtforms.validators import DataRequired
from flask_bootstrap import Bootstrap
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import datetime as dt
import smtplib
import time
import os
DATE = dt.datetime.now().year
PASSWORD = os.getenv("PASSWORD")
EMAIL = os.getenv("EMAIL")


app = Flask(__name__)

login_manager = LoginManager()
login_manager.init_app(app)
Bootstrap(app)
ckeditor = CKEditor(app)
app.secret_key = os.getenv("SECRET_KEY")
app.config['SECRET_KEY'] = os.getenv("DATA_KEY")
app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv("URL"). replace ("postgres://", "postgresql://", 1)
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)


@login_manager.user_loader
def load_user(user_id):
    return User.query.get(str(user_id))


# CREATE TABLE IN DB
class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(100), unique=True)
    name = db.Column(db.String(1000))


class MailForm(FlaskForm):
    subject = StringField("Mail Subject", validators=[DataRequired()])
    message = CKEditorField("Mail Message", validators=[DataRequired()])
    submit = SubmitField("Send Mail")


# Line below only required once, when creating DB.
#db.create_all()


@app.route('/')
def home():
    date = dt.datetime.now().year
    return render_template("index.html", date=date)


@app.route('/register', methods=["POST", "GET"])
def register():
    if request.method == "POST":
        user_email = request.form["email"]
        user_name = request.form["name"]
        new_user = User(email=user_email, name=user_name)
        db.session.add(new_user)
        db.session.commit()
        return redirect(url_for('offer'))
    return render_template("register.html", date=DATE)


@app.route("/send/emails", methods=["POST", "GET"])
def mails():
    form = MailForm()
    all_users = db.session.query(User).all()
    if form.validate_on_submit():
        for user in all_users:
            message = MIMEMultipart("alternative")
            message["Subject"] = form.subject.data
            message["From"] = EMAIL
            message["To"] = user.email
            html = f"""\
            {form.message.data}
            """
            text = MIMEText(html, "html")
            message.attach(text)
            try:
                with smtplib.SMTP("smtp.gmail.com") as connection:
                    connection.starttls()
                    connection.login(password=PASSWORD, user=EMAIL)
                    connection.sendmail(from_addr=EMAIL, to_addrs=user.email,
                                        msg=message.as_string())
            except:
                pass
            else:
                pass
            time.sleep(1)
        flash("Mails successfully sent")
        return redirect(url_for('mails'))
    return render_template("mail.html", form=form, date=DATE)


@app.route("/offer")
def offer():
    return render_template("offer.html", date=DATE)


if __name__ == "__main__":
    app.run(debug=True)
