from flask_sqlalchemy import SQLAlchemy
from flask_bcrypt import Bcrypt

db = SQLAlchemy()
bcrypt = Bcrypt()

def connect_db(app):
    """Connect to database"""
    db.app = app
    db.init_app(app)

class User(db.Model):
    """User table"""
    __tablename__ = 'users'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    name = db.Column(db.Text, nullable=False)
    username = db.Column(db.Text, unique=True, nullable=False)
    password = db.Column(db.Text, nullable=False)
    email = db.Column(db.Text, nullable=False)
    watch_later = db.relationship('Movie_or_Show', secondary='watch_later')
    favorites = db.relationship('Movie_or_Show', secondary='favorites')

    def __repr__(self):
        return f'<User #{self.id}: {self.username}, {self.email}>'
    
    @classmethod
    def signup(cls, name, username, password, email):
        hashed_pw = bcrypt.generate_password_hash(password).decode('UTF-8')

        user = User(name=name, username=username, password=hashed_pw, email=email)
        db.session.add(user)
        return user
    
    @classmethod
    def authenticate(cls, username, password):
        user = User.query.filter_by(username=username).first()
        if user and bcrypt.check_password_hash(user.password, password):
            return user
        else:
            return False

class Movie_or_Show(db.Model):
    __tablename__ = 'movie_or_show'

    id = db.Column(db.Integer, primary_key=True)
    type = db.Column(db.Text)
    title = db.Column(db.Text)
    poster = db.Column(db.Text, nullable=False, default='https://encrypted-tbn0.gstatic.com/images?q=tbn:ANd9GcS9dI2vOEBq9ApxwOBoucjQHHZW1DWpMdwQgA&usqp=CAU')
    overview = db.Column(db.Text)
    tmdb_rating = db.Column(db.Integer)
    tmdb_votes = db.Column(db.Integer)
    comments = db.relationship('User', secondary='comments')

class WatchLater(db.Model):
    __tablename__ = 'watch_later'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    movie_or_show_id = db.Column(db.Integer, db.ForeignKey('movie_or_show.id'))
    type = db.Column(db.Text)

class Favorite(db.Model):
    __tablename__ = 'favorites'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    movie_or_show_id = db.Column(db.Integer, db.ForeignKey('movie_or_show.id'))
    type = db.Column(db.Text)

class Comment(db.Model):
    __tablename__ = 'comments'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    title = db.Column(db.Text, nullable=False)
    content = db.Column(db.Text, nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    movie_or_show_id = db.Column(db.Integer, db.ForeignKey('movie_or_show.id'))
    type = db.Column(db.Text)