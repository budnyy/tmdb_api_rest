from flask import Flask, render_template, request, redirect, url_for
from flask_sqlalchemy import SQLAlchemy
import requests

app = Flask(__name__)
details_url = "https://api.themoviedb.org/3/search/movie?include_adult=false&language=en-US&page=1"

headers = {
    "accept": "application/json",
    "Authorization": "Bearer eyJhbGciOiJIUzI1NiJ9.eyJhdWQiOiI4YjNmNTRlZTllNmQ5ZWU0MzRlMzA2YjhjNTBiNTU1ZiIsIm5iZiI6MTc0OTU2NTEzMi44MTYsInN1YiI6IjY4NDgzZWNjNjZlMTZhNWEzOTIwNjkzYSIsInNjb3BlcyI6WyJhcGlfcmVhZCJdLCJ2ZXJzaW9uIjoxfQ.BxpAUpU5jMx19rLcqHrpH5r7FV6xhTP-7F60HkHw82E"
}

@app.route("/", methods=["POST", "GET"])
def home():
    if request.method == "POST":
        search_title = request.form["search_title"]
        return redirect(url_for("moviepage", title = search_title))
    else:
        return render_template("index.html")

@app.route("/movie/<title>")
def moviepage(title):
    response = requests.get(f"https://api.themoviedb.org/3/search/movie?query={title}&include_adult=false&language=en-US&page=1", headers=headers)
    movie_info = response.json()
    return f"{movie_info["results"][0]}"


if __name__ == "__main__":
    app.run(debug=True)
