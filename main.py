from flask import Flask, render_template, request, redirect, url_for, session
from flask_sqlalchemy import SQLAlchemy
from datetime import timedelta
from dotenv import load_dotenv
import os
import requests

load_dotenv()
api_key = os.getenv("API_KEY")

app = Flask(__name__)
app.secret_key = "hello"
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///users.sqlite3"
app.config["SQLACLHEMY_TRACK_MODIFICATIONS"] = False
app.permanent_session_lifetime = timedelta(minutes=5)
db = SQLAlchemy(app)

class User(db.Model):
    _id = db.Column("id",db.Integer, primary_key=True)
    name = db.Column("name",db.String(100), unique=True, nullable=False)
    email = db.Column("email",db.String(100), unique=True, nullable=False)

    def __init__(self, name, email):
        self.name = name
        self.email = email

languages_url = "https://api.themoviedb.org/3/configuration/primary_translations"
headers = {
    "accept": "application/json",
    "Authorization": api_key
}


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
        email = request.form["email"]

        if User.query.filter_by(email=email).first() == None:
            name = request.form["nm"]
            session["name"] = name
            session["email"] = email
            #register password (future)

            new_user = User(name, email)
            db.session.add(new_user)
            db.session.commit()
            
            return redirect(url_for("user", user=session["name"]))
        
        else:
            return redirect(url_for("login"))
    else:
        if "name" in session:
            return redirect(url_for("user", user=session["name"]))
        return render_template("register.html")
                

@app.route("/login", methods= ["POST", "GET"])
def login():
    if request.method == "POST":
        email = request.form["email"]
        
        if User.query.filter_by(email=email).first() == None:
            return redirect(url_for("register"))
        
        else:
            #verify password (future)
            print()
    else:
        if "name" in session:
            return redirect(url_for("user", user=session["name"]))
        else:
            return render_template("login.html")
    

@app.route("/<user>")
def user(user):
    return render_template("user.html", name=user)


@app.route("/view")
def view():
    return render_template("view.html", values = User.query.all())


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
