from config import db, UserMixin

class User(db.Model, UserMixin):
    id = db.Column("id",db.Integer, primary_key=True)
    name = db.Column("name",db.String(20), unique=True, nullable=False)
    email = db.Column("email",db.String(100), unique=True, nullable=False)
    password = db.Column("password", db.String(100), nullable=False)

    def __init__(self, name, email, password):
        self.name = name
        self.email = email
        self.password = password