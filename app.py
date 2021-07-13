from flask import Flask, render_template, request, flash, redirect, session, jsonify
from flask_debugtoolbar import DebugToolbarExtension
from sqlalchemy.exc import IntegrityError
import requests
import json

from models import db, connect_db, User, Movie_or_Show, WatchLater, Favorite, Comment
from forms import EditUserForm, SearchForm, SignupForm, LoginForm, CommentForm

app = Flask(__name__)

app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql:///capstone1'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SQLALCHEMY_ECHO'] = False
app.config['DEBUG_TB_INTERCEPT_REDIRECTS'] = False
app.config['SECRET_KEY'] = "password"

connect_db(app)
toolbar = DebugToolbarExtension(app)

API_KEY='7044c73ec9077f9a062f7b1cdeaf0a81'

IMG_BASE_URL='https://image.tmdb.org/t/p/w500'

SEARCH_MOVIE = 'https://api.themoviedb.org/3/search/movie?api_key=7044c73ec9077f9a062f7b1cdeaf0a81&language=en-US&page=1&include_adult=false'
SEARCH_TV = 'https://api.themoviedb.org/3/search/tv?api_key=7044c73ec9077f9a062f7b1cdeaf0a81&language=en-US&page=1&include_adult=false'

SEARCH_MOVIE_ID = 'https://api.themoviedb.org/3/movie/'
SEARCH_TV_ID = 'https://api.themoviedb.org/3/tv/'

def do_login(user):
    session['user'] = user.id

def do_logout():
    if 'user' in session:
        del session['user']

@app.route('/')
def homepage():
    return render_template('homepage.html')

@app.route('/search', methods=['GET', 'POST'])
def search():
    form = SearchForm()
    if form.validate_on_submit():
        term = form.search_term.data
        type = form.type.data

        if type == 'movie':
            resp = requests.get(f'{SEARCH_MOVIE}&query={term}')
            dict = json.loads(resp.text)
            results = dict['results']
            session['type'] = type
            return render_template('search_results.html', results=results, term=term)

        if type == 'tv':
            resp = requests.get(f'{SEARCH_TV}&query={term}')
            dict = json.loads(resp.text)
            results = dict['results']
            session['type'] = type
            return render_template('search_results.html', results=results, term=term)
    else:
        return render_template('search.html', form=form)    

@app.route('/details/<int:id>', methods=['GET'])
def movie_details(id):
    query_watch_later = WatchLater.query.filter_by(user_id=session['user'], movie_or_show_id=id, type=session['type']).first()
    query_favorites = Favorite.query.filter_by(user_id=session['user'], movie_or_show_id=id, type=session['type']).first()
    
    comments = Comment.query.filter_by(movie_or_show_id=id).all()
    if session['type'] == 'movie':
        resp = requests.get(f'{SEARCH_MOVIE_ID}{id}?api_key=7044c73ec9077f9a062f7b1cdeaf0a81&language=en-US')
        results = json.loads(resp.text)

        genres = results['genres']
        genres_list = []

        for genre in genres:
            genres_list.append(genre['name'])

        genres_string = ' '.join([str(item) for item in genres_list]).replace(' ', ', ')
            
        budget = results['budget']
        budget = '{:,}'.format(budget)
        
        revenue = results['revenue']
        revenue = '{:,}'.format(revenue)

        return render_template('movie_details.html', comments=comments, watch_later=query_watch_later, favorites=query_favorites, results=results, genres=genres_string, budget=budget, revenue=revenue)
    elif session['type'] == 'tv':
        resp = requests.get(f'{SEARCH_TV_ID}{id}?api_key=7044c73ec9077f9a062f7b1cdeaf0a81&language=en-US')
        results = json.loads(resp.text)

        genres = results['genres']
        genres_list = []

        for genre in genres:
            genres_list.append(genre['name'])
        
        genres_string = ' '.join([str(item) for item in genres_list]).replace(' ', ', ')

        return render_template('tv_details.html', comments=comments, watch_later=query_watch_later, favorites=query_favorites, results=results, genres=genres_string, id=id)

@app.route('/details/<int:id>/seasons')
def show_seasons(id):
    resp = requests.get(f'{SEARCH_TV_ID}{id}?api_key=7044c73ec9077f9a062f7b1cdeaf0a81&language=en-US')
    results = json.loads(resp.text)
    
    seasons = results['seasons']
    return render_template('seasons.html', seasons=seasons, results=results)

@app.route('/details/<int:id>/comment', methods=['GET', 'POST'])
def comment(id):
    form = CommentForm()
    exists = Movie_or_Show.query.filter_by(id=id, type=session['type']).first()
    if form.validate_on_submit():
        if exists:
            if Comment.query.filter_by(user_id=session['user'], movie_or_show_id=id).first():
                flash('You can only comment once per movie!', 'danger')
                return redirect(f'/details/{id}')
            else:
                title = form.title.data
                content = form.content.data
                user_id = session['user']
                type = session['type']
                movie_or_show_id = id
                
                new_comment = Comment(title=title, content=content, user_id=user_id, type=type, movie_or_show_id=movie_or_show_id)
                db.session.add(new_comment)
                db.session.commit()
                return redirect(f'/details/{id}')
        else:
            resp = requests.get(f"https://api.themoviedb.org/3/{session['type']}/{id}?api_key={API_KEY}")
            dict = json.loads(resp.text)
            if session['type'] == 'movie':
                new_result = Movie_or_Show(id=dict['id'], type=session['type'], title=dict['title'], poster=f"{IMG_BASE_URL}{dict['poster_path']}", overview=dict['overview'], tmdb_rating=dict['vote_average'], tmdb_votes=dict['vote_count'])
                db.session.add(new_result)
                db.session.commit()
            if session['type'] == 'tv':
                new_result = Movie_or_Show(id=dict['id'], type=session['type'], title=dict['name'], poster=f"{IMG_BASE_URL}{dict['poster_path']}", overview=dict['overview'], tmdb_rating=dict['vote_average'], tmdb_votes=dict['vote_count'])
                db.session.add(new_result)
                db.session.commit()
            
            title = form.title.data
            content = form.content.data
            user_id = session['user']
            type = session['type']
            movie_or_show_id = id
            
            new_comment = Comment(title=title, content=content, user_id=user_id, type=type, movie_or_show_id=movie_or_show_id)
            db.session.add(new_comment)
            db.session.commit()
            return redirect(f'/details/{id}')
    else:
        return render_template('comment.html', form=form)

@app.route('/details/<int:id>/comment/remove', methods=['POST'])
def delete_comment(id):
    comment = Comment.query.filter_by(movie_or_show_id=id, user_id=session['user']).first()
    db.session.delete(comment)
    db.session.commit()
    return redirect(f'/details/{id}')

@app.route('/details/<int:id>/favorite', methods=['POST'])
def favorite(id):
    resp = requests.get(f"https://api.themoviedb.org/3/{session['type']}/{id}?api_key={API_KEY}")
    dict = json.loads(resp.text)
    exists = Movie_or_Show.query.filter_by(id=dict['id'], type=session['type']).first()

    if exists:
        new_favorite = Favorite(user_id=session['user'], movie_or_show_id=dict['id'], type=session['type'])
        db.session.add(new_favorite)
        db.session.commit()
    else:
        if session['type'] == 'movie':
            new_result = Movie_or_Show(id=dict['id'], type=session['type'], title=dict['title'], poster=f"{IMG_BASE_URL}{dict['poster_path']}", overview=dict['overview'], tmdb_rating=dict['vote_average'], tmdb_votes=dict['vote_count'])
            db.session.add(new_result)
            db.session.commit()
        if session['type'] == 'tv':
            new_result = Movie_or_Show(id=dict['id'], title=dict['name'], poster=f"{IMG_BASE_URL}{dict['poster_path']}", overview=dict['overview'], tmdb_rating=dict['vote_average'], tmdb_votes=dict['vote_count'])
            db.session.add(new_result)
            db.session.commit()
        
        new_favorite = Favorite(user_id=session['user'], movie_or_show_id=dict['id'], type=session['type']  )
        db.session.add(new_favorite)
        db.session.commit()

    return redirect('/profile')

@app.route('/details/<int:id>/favorite/remove', methods=['POST'])
def remove_favorite(id):
    favorite = Favorite.query.filter_by(user_id=session['user'], movie_or_show_id=id).first()
    db.session.delete(favorite)
    db.session.commit()
    return redirect('/profile')

@app.route('/details/<int:id>/watch-later', methods=['POST'])
def watch_later(id):
    resp = requests.get(f"https://api.themoviedb.org/3/{session['type']}/{id}?api_key={API_KEY}")
    dict = json.loads(resp.text)
    exists = Movie_or_Show.query.filter_by(id=dict['id'], type=session['type']).first()

    if exists:
        new_watch_later = WatchLater(user_id=session['user'], movie_or_show_id=dict['id'], type=session['type'])
        db.session.add(new_watch_later)
        db.session.commit()
    else:    
        if session['type'] =='movie':
            new_result = Movie_or_Show(id=dict['id'], type=session['type'], title=dict['title'], poster=f"{IMG_BASE_URL}{dict['poster_path']}", overview=dict['overview'], tmdb_rating=dict['vote_average'], tmdb_votes=dict['vote_count'])
            db.session.add(new_result)
            db.session.commit()
        if session['type'] == 'tv':
            new_result = Movie_or_Show(id=dict['id'], title=dict['name'], poster=f"{IMG_BASE_URL}{dict['poster_path']}", overview=dict['overview'], tmdb_rating=dict['vote_average'], tmdb_votes=dict['vote_count'])
            db.session.add(new_result)
            db.session.commit()
        
        new_watch_later = WatchLater(user_id=session['user'], movie_or_show_id=dict['id'], type=session['type'])
        db.session.add(new_watch_later)
        db.session.commit()

    return redirect('/profile')

@app.route('/details/<int:id>/watch-later/remove', methods=['POST'])
def remove_watch_later(id):
    watch_later = WatchLater.query.filter_by(user_id=session['user'], movie_or_show_id=id).first()
    db.session.delete(watch_later)
    db.session.commit()
    return redirect('/profile')

@app.route('/profile')
def profile():
    user = User.query.get_or_404(session['user'])
    return render_template('users/profile.html', user=user)

@app.route('/profile/edit', methods=['GET', 'POST'])
def edit_profile():
    if not session['user']:
        flash('Access Denied!', 'danger')
        return redirect('/')
    
    user = User.query.get_or_404(session['user'])
    form = EditUserForm(obj=user)

    if form.validate_on_submit():
        if User.authenticate(username=user.username, password=form.password.data):
            try:
                user.name = form.name.data
                user.username = form.username.data
                user.email = form.email.data

                db.session.commit()
                return redirect('/profile')
            except IntegrityError:
                form.username.errors.append('Username already taken!')
                return render_template('users/edit.html', form=form)
        
        else:
            form.password.errors.append('Wrong password!')
            return render_template('users/edit.html', form=form)
    else:
        return render_template('users/edit.html', form=form)

@app.route('/signup', methods=['GET', 'POST'])
def signup():
    form = SignupForm()
    if form.validate_on_submit():
        if form.password.data == form.confirm_password.data:
            try:
                name = form.name.data
                username = form.username.data
                password = form.password.data
                email = form.email.data

                user = User.signup(
                    name=name,
                    username=username,
                    password=password,
                    email=email
                )

                db.session.commit()
            except IntegrityError:
                form.username.errors.append('Username already taken!')
                return render_template('users/signup.html', form=form)

            do_login(user)
            return redirect('/')
        else:
            form.password.errors.append("Passwords don't match!")
            return render_template('users/signup.html', form=form)
    else:
        return render_template('users/signup.html', form=form)

@app.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()

    if form.validate_on_submit():
        username = form.username.data
        password = form.password.data
        user = User.authenticate(username, password)

        if user:
            do_login(user)
            flash(f'Welcome back, {user.username}!', 'success')
            return redirect('/')
        else:
            flash('Incorrect username/password', 'danger')
            return render_template('users/login.html', form=form)
    else:
        return render_template('users/login.html', form=form)


@app.route('/logout')
def logout():
    do_logout()
    flash('Goodbye, see you later!', 'danger')
    return redirect('/')