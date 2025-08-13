from config import db, request, redirect, url_for, render_template, requests, lm, app, bcrypt, api_key, login_user, login_required, flash, dummy_hash, current_user, logout_user, languages_url, headers
from classes import User

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
            return render_template("user.html", user=user_found, admin=True)
        else:
            return render_template("user.html", user=user_found, admin=False)
    else:
        return f"Something went wrong! Try again later"


@app.route("/view")
def view():
    return render_template("view.html", values = User.query.all())

@app.route("/logout")
@login_required
def logout():
    flash("Logged out!")
    logout_user()
    return redirect("/")

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
