from unittest import TestCase
from models import db, User, Movie_or_Show, WatchLater, Favorite, Comment
from flask import session
from app import app, do_login

app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql:///capstone1_test'

app.config['WTF_CSRF_ENABLED']=False

class UserViewTestCase(TestCase):
    def setUp(self):
        db.drop_all()
        db.create_all()

        self.test_user1 = User.signup(
            name='Test User 1',
            username='test_user1',
            password='password',
            email='test1@gmail.com')
        self.test_user1.id = 999
        db.session.add(self.test_user1)
        db.session.commit()

        self.test_user2 = User.signup(
            name='Test User 2',
            username='test_user2',
            password='password',
            email='test2@gmail.com')
        self.test_user2.id = 888
        db.session.commit()
    
        self.tv_show = Movie_or_Show(
            id=1405,
            type='tv',
            title='Dexter',
            poster='https://image.tmdb.org/t/p/w500/58H6Ctze1nnpS0s9vPmAAzPcipR.jpg',
            overview='Dexter Morgan, a blood spatter pattern analyst for the Miami Metro Police also leads a secret life as a serial killer, hunting down criminals who have slipped through the cracks of justice.',
            tmdb_rating=8.2,
            tmdb_votes=2440)
        db.session.add(self.tv_show)
        db.session.commit()

    def test_home_anon(self):
        with app.test_client() as client:
            response = client.get('/')
            s = str(response.data)

            self.assertIn('Please sign up or log in', s)

    def test_user_home(self):
        with app.test_client() as client:
            with client.session_transaction() as sess:
                sess['user'] = 999
            
            response = client.get('/')
            s = str(response.data)

            self.assertIn('Search for a Movie or TV Show', s)

    def test_login(self):
        with app.test_client() as client:
            response = client.get('/')
            user = User.authenticate(username='test_user1', password='password')
            do_login(user)

            
            self.assertEqual(session['user'], 999)
    
    def test_tv_details(self):
        with app.test_client() as client:
            with client.session_transaction() as sess:
                sess['user'] = 999
                sess['type'] = 'tv'

        response = client.get('/details/1405')
        s = str(response.data)

        self.assertIn('Dexter', s)

    def test_watch_later(self):
        watch_later = WatchLater(
            user_id=999,
            movie_or_show_id=1405,
            type='tv')
        db.session.add(watch_later)
        db.session.commit()

        with app.test_client() as client:
            with client.session_transaction() as sess:
                sess['user'] = 999
        response = client.get('/profile')
        s = str(response.data)
        
        self.assertIn('Dexter', s)
    
    def test_favorite(self):
        favorite = Favorite(
            user_id = 999,
            movie_or_show_id=1405,
            type='tv')
            
        db.session.add(favorite)
        db.session.commit()

        with app.test_client() as client:
            with client.session_transaction() as sess:
                sess['user'] = 999
        response = client.get('/profile')
        s = str(response.data)

        self.assertIn('Dexter', s)

    def test_no_watch_later_or_favorite(self):
        with app.test_client() as client:
            with client.session_transaction() as sess:
                sess['user'] = 999
        response = client.get('/profile')
        s = str(response.data)
        
        self.assertNotIn('Dexter', s)

    def test_anon_comment(self):
        comment = Comment(
            title = 'Test',
            content = 'test comment',
            user_id = 888,
            movie_or_show_id = 1405,
            type = 'tv')

        db.session.add(comment)
        db.session.commit()

        with app.test_client() as client:
            with client.session_transaction() as sess:
                sess['user'] = 999
                sess['type'] = 'tv'
            
            response = client.get('/details/1405?')
            s = str(response.data)

            self.assertNotIn('Delete', s)
            self.assertIn("<h1>Test</h1>", s)

    def test_user_comment(self):
        comment = Comment(
            title = 'Test',
            content = 'test comment',
            user_id = 999,
            movie_or_show_id = 1405,
            type = 'tv')

        db.session.add(comment)
        db.session.commit()

        with app.test_client() as client:
            with client.session_transaction() as sess:
                sess['user'] = 999
                sess['type'] = 'tv'
            
            response = client.get('/details/1405?')
            s = str(response.data)

            self.assertIn('Delete', s)
            self.assertIn("<h1>Test</h1>", s)