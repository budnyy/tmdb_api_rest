from config import db, request, redirect, url_for, render_template, requests, lm, app, bcrypt, api_key, login_user, login_required, flash, dummy_hash, current_user, logout_user, languages_url, headers, trending_url
from classes import User, MovieCache

@lm.user_loader
def user_loader(id):
    user = db.session.query(User).filter_by(id=id).first()
    return user

@app.route("/", methods=["POST", "GET"])
def home():
    languages_response = requests.get(languages_url, headers=headers).json()
    trending_response = requests.get(trending_url, headers=headers).json()
    if request.method == "POST":
        search_title = request.form["search_title"]
        lang = request.form["lang"]
        return redirect(url_for("moviepage", title=search_title, lang=lang, page=1))
    else:

        return render_template("index.html", languages = languages_response, trending = trending_response["results"])
    
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
            return redirect(url_for("user",user=new_user.name))
        
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
                flash("Invalid credentials.")
                return redirect(url_for("login"))
        else:
            bcrypt.check_password_hash(dummy_hash, password)
            flash("Invalid credentials.")
            return redirect(url_for("login"))
    else:
        return render_template("login.html")

@app.route("/profile")
@login_required
def profile():
    return redirect(url_for("user", user=current_user.name))

@app.route("/search")
def search():
    search_user_name = request.args["search_user"]
    search_user = User.query.filter_by(name=search_user_name).first()
    if search_user:
        return redirect(url_for("user", user=search_user.name))
    else:
        flash("User not found! :(")
        return redirect(url_for("home"))

@app.route("/<user>")
def user(user):
    user_found = User.query.filter_by(name=user).first()

    if user_found:
        if user_found == current_user:
            return render_template("user.html", user=user_found, admin=True, favorites=current_user.fav_movies)
        else:
            return render_template("user.html", user=user_found, admin=False, favorites=user_found.fav_movies)
    else:
        return f"Something went wrong! Try again later"

@app.route("/logout")
@login_required
def logout():
    flash("Logged out!")
    logout_user()
    return redirect("/")

@app.route("/movie/<lang>/<title>/<page>")
def moviepage(title, lang, page=1):
        response = requests.get(f"https://api.themoviedb.org/3/search/movie?query={title}&include_adult=false&language={lang}&page={page}", headers=headers)
        movie_info = response.json()
        results = movie_info["results"]
        page = movie_info["page"]

        for movie in results:
            search_movie = MovieCache.query.filter_by(tmdb_id=movie["id"]).first()
            if search_movie == None:
                movie_cache = MovieCache(movie["id"], movie["title"], movie["poster_path"], movie["release_date"])
                db.session.add(movie_cache)
                db.session.commit()

        try:
            return render_template("moviepage.html", info=results, logged_in=current_user.is_authenticated, title=title, lang=lang, page=page, max_pages = movie_info["total_pages"])
        except IndexError:
            return f"No results :("

@app.route("/movie/details/<id>")
def details(id):
    details_response = requests.get(f"https://api.themoviedb.org/3/movie/{id}", headers=headers).json()
    return render_template("moviedetails.html", movie=details_response)


@app.route("/movie/favorite", methods=["POST"])
def favorite():
    fav_id = request.form["fav_id"]
    title = request.form["title"]
    lang = request.form["lang"]
    search_movie = MovieCache.query.filter_by(tmdb_id=int(fav_id)).first()

    if search_movie not in current_user.fav_movies:
        current_user.fav_movies.append(search_movie)
        db.session.commit()
    
    return redirect(url_for("moviepage", title=title, lang=lang))

if __name__ == "__main__":
    with app.app_context():
        db.create_all()
    app.run(debug=True)
