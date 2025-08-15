from config import db, UserMixin

favorites = db.Table("favorites",
    db.Column("user_id", db.Integer, db.ForeignKey("user.id")),
    db.Column("tmdb_id", db.Integer, db.ForeignKey("moviecache.tmdb_id"))
)   

class User(db.Model, UserMixin):
    id = db.Column("id",db.Integer, primary_key=True)
    name = db.Column("name",db.String(20), unique=True, nullable=False)
    email = db.Column("email",db.String(100), unique=True, nullable=False)
    password = db.Column("password", db.String(100), nullable=False)
    fav_movies = db.relationship("MovieCache", secondary=favorites, backref="fav_for_user")

    def __init__(self, name, email, password):
        self.name = name
        self.email = email
        self.password = password

class MovieCache(db.Model):
    __tablename__ = "moviecache"

    id = db.Column("id", db.Integer, primary_key=True)
    tmdb_id = db.Column("tmdb_id",db.Integer)
    title = db.Column("title", db.String(50))
    poster_path = db.Column("poster_path", db.String(80))
    release_date = db.Column("release_date", db.String(15))

    def __init__(self, tmdb_id, title, poster_path, release_date):
        self.tmdb_id = tmdb_id
        self.title = title
        self.poster_path = poster_path
        self.release_date = release_date

    def __repr__(self):
        return f"{self.tmdb_id}, {self.title}, {self.poster_path}, {self.release_date}"