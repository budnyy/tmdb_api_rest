from flask import Flask, render_template, request, redirect, url_for, flash, get_flashed_messages
from flask_login import LoginManager, UserMixin, login_required, login_user, logout_user
from flask_bcrypt import Bcrypt
from flask_sqlalchemy import SQLAlchemy
from datetime import timedelta
from dotenv import load_dotenv
import os
import requests

load_dotenv()
api_key = os.getenv("API_KEY")
secret_key = os.getenv("SECRET_KEY")

app = Flask(__name__)
app.secret_key = secret_key
lm = LoginManager(app)
lm.login_view = "login"
bcrypt = Bcrypt(app)
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///users.sqlite3"
app.config["SQLACLHEMY_TRACK_MODIFICATIONS"] = False
app.permanent_session_lifetime = timedelta(minutes=5)
db = SQLAlchemy(app)

dummy_hash = bcrypt.generate_password_hash('dummy_password')

class User(db.Model, UserMixin):
    id = db.Column("id",db.Integer, primary_key=True)
    name = db.Column("name",db.String(20), unique=True, nullable=False)
    email = db.Column("email",db.String(100), unique=True, nullable=False)
    password = db.Column("password", db.String(100), nullable=False)

    def __init__(self, name, email, password):
        self.name = name
        self.email = email
        self.password = password


languages_url = "https://api.themoviedb.org/3/configuration/primary_translations"
headers = {
    "accept": "application/json",
    "Authorization": api_key
}

@lm.user_loader
def user_loader(id):
    user = db.session.query(User).filter_by(id=id).first()
    return user

@app.route("/", methods=["POST", "GET"])
def home():
    if request.method == "POST":
        search_title = request.form["search_title"]
        lang = request.form["lang"]
        return redirect(url_for("moviepage", title = search_title, lang=lang))
    else:
        return render_template("index.html", languages = requests.get(languages_url, headers=headers).json())

    
@app.route("/register", methods=["POST","GET"])
def register():
    if request.method == "POST":
        name = request.form["nm"]
        email = request.form["email"]

        if User.query.filter_by(name=name, email=email).first() == None:    
            password = request.form["password"]
            hashed_password = bcrypt.generate_password_hash(password).decode("utf-8")

            new_user = User(name, email, hashed_password)
            db.session.add(new_user)
            db.session.commit()

            login_user(new_user)
        
        else:
            flash("Username already in use")
            return redirect(url_for("register"))
    
    else:
        return render_template("register.html")


@app.route("/login", methods= ["POST", "GET"])
def login():
    if request.method == "POST":
        email = request.form["email"]
        password = request.form["password"]

        user = User.query.filter_by(email=email).first()
        if user:        
            if bcrypt.check_password_hash(user.password, password):
                login_user(user)
                return redirect(url_for("user", user=user.name))
        else:
            bcrypt.check_password_hash(dummy_hash, password)
            flash("Invalid credentials.")
            return redirect(url_for("login"))
    else:
        return render_template("login.html")
    

@app.route("/<user>")
@login_required
def user(user):
    return render_template("user.html", name=user)


@app.route("/view")
def view():
    return render_template("view.html", values = User.query.all())

@app.route("/logout")
@login_required
def logout():
    return logout_user()

@app.route("/movie/<lang>/<title>")
def moviepage(title, lang):
    response = requests.get(f"https://api.themoviedb.org/3/search/movie?query={title}&include_adult=false&language={lang}&page=1", headers=headers)
    movie_info = response.json()
    try:
        return render_template("moviepage.html", info = movie_info["results"])
    except IndexError:
        return f"No results :("

if __name__ == "__main__":
    with app.app_context():
        db.create_all()
    app.run(debug=True)
