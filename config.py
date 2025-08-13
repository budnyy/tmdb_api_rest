from flask import Flask, render_template, request, redirect, url_for, flash, get_flashed_messages
from flask_login import LoginManager, UserMixin, login_required, login_user, logout_user, current_user
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

languages_url = "https://api.themoviedb.org/3/configuration/primary_translations"
headers = {
    "accept": "application/json",
    "Authorization": api_key
}