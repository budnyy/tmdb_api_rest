from flask import Flask, render_template, request, redirect, url_for
from dotenv import load_dotenv
import os
import requests

load_dotenv()
api_key = os.getenv("API_KEY")

app = Flask(__name__)
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

@app.route("/movie/<lang>/<title>")
def moviepage(title, lang):
    response = requests.get(f"https://api.themoviedb.org/3/search/movie?query={title}&include_adult=false&language={lang}&page=1", headers=headers)
    movie_info = response.json()
    try:
        return render_template("moviepage.html", info = movie_info["results"])
    except IndexError:
        return f"No results :("

if __name__ == "__main__":
    app.run(debug=True)
