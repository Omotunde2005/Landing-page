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
DATE = dt.datetime.now().year
PASSWORD = "wtkkbbynyxxwhbfw"
EMAIL = "Oyinloyequareeboyinloye@gmail.com"


app = Flask(__name__)

login_manager = LoginManager()
login_manager.init_app(app)
Bootstrap(app)
ckeditor = CKEditor(app)
app.secret_key = "EmilojuEdunOmobolanlesimfc2005."
app.config['SECRET_KEY'] = 'my_secret_key'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///users.db'
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
        message = MIMEMultipart("alternative")
        message["Subject"] = "Lets Goo! Your 6-Figure Ebook is inside!"
        message["From"] = EMAIL
        message["To"] = user_email
        html = f"""\
        <h1>Hi, {user_name}</h1>

<p style="font-size: 1rem;" >Oyinloye Quareeb here..</p>

<p style="line-height: 2; font-size: 1.2rem; font-family: Montserrat;">Super excited to share this new ebook with you...
<br>

I will get into the details on how Jonathan left his soul sucking 9-5 job tomorrow...<br>

But for now, follow these next few steps. I want to help you because TRUST me, he hated his job so bad. Do this now…<br>

Step 1:  Make sure to whitelist my emails or add me as a contact. Just in case my emails don't end up in your inbox..
<br>
If you use Gmail, just drag this email over to the “Primary” tab and drop it there.<br>

Trust me, you don't want to miss anything these next few days...<br>

Step 2: Here is my new ebook: <a href='https://bit.ly/3nLvviu'>7 Steps to Becoming A Super Affiliate</a>
<br>
This is my manual on how Jonathan became a super affiliate in under a year and left his job as an electrical engineer…
<br>

This is the exact blueprint that has now helped thousands of students...</p><br>

<h4 style="font-size: 1.3rem;">Thank you for taking the time to open and read...</h4><br>
<br>

<p style="font-size: 1.3rem;">I would love to get to know you as well, reply to this email and let me know WHY you want 
to do this...</p>
<br>
<h4>Thank you,</h4>
<br>
Oyinloye Quareeb
               """
        text = MIMEText(html, "html")
        message.attach(text)
        try:
            with smtplib.SMTP("smtp.gmail.com") as connection:
                connection.starttls()
                connection.login(password=PASSWORD, user=EMAIL)
                connection.sendmail(from_addr=EMAIL, to_addrs=user_email,
                                    msg=message.as_string())
        except:
            print("error")
        else:
            new_user = User(email=user_email, name=user_name)
            db.session.add(new_user)
            db.session.commit()
            return redirect(url_for('offer'))
    return render_template("register.html", date=DATE)


@app.route("/send/emails/", methods=["POST", "GET"])
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
