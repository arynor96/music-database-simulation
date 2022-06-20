import sys

import pymongo
from flask import Flask, render_template, redirect, session, flash, request, url_for
import mysql.connector
import datetime
import re

from app.helpers.migration import migrate_database
from app.helpers.sql_functions import create_sql_tables, delete_sql_tables, fill_sql_tables

app = Flask(__name__)
app.config['DB_STATUS'] = ''
app.config['SECRET_KEY'] = 'SECRET'

sql_config = {'user': 'user', 'password': 'password', 'host': 'sql', 'port': '3306', 'database': 'imse_m2_db'}
db = mysql.connector.connect(**sql_config)

mongo_client = pymongo.MongoClient('mongodb://user:password@mongo:27017/?authSource=admin')
mongo_db = mongo_client['imse_m2_mongo']

cursor = db.cursor()


@app.route('/')
@app.route('/home')
def home():
    if app.config['DB_STATUS'] == '':
        return render_template("init.html")
    else:
        return render_template("index.html")


@app.route('/login', methods=["POST", "GET"])
def login():
    if app.config['DB_STATUS'] == '':
        flash("Please initialize database first!")
        return render_template("init.html")

    if request.method == "POST" and 'email' in request.form and 'pass' in request.form:
        session.permanent = True
        user = request.form['email']
        user_password = request.form['pass']
        cursor.execute('SELECT * FROM Users WHERE email = %s AND password = %s', (user, user_password,))
        account = cursor.fetchone()
        if account:
            session["user"] = user
            flash("Login succesful!")
            return redirect(url_for("home"))
        else:
            flash("Incorrect email/password!")
            return render_template("login.html")
    else:
        if "user" in session:
            flash("Already logged in!")
            return redirect(url_for("home"))
        return render_template("login.html")


@app.route("/logout")
def logout():
    if app.config['DB_STATUS'] == '':
        flash("Please initialize database first!")
        return render_template("init.html")

    if "user" in session:
        user = session["user"]
        flash(f"You have been logged out, {user}", "info")
    session.pop("user", None)
    return redirect(url_for("home"))


@app.route("/register", methods=["POST", "GET"])
def register():
    if request.method == 'POST' and 'email' in request.form and 'username' in request.form and 'pass' in request.form:
        email = request.form['email']
        username = request.form['username']
        user_password = request.form['pass']
        cursor.execute('SELECT * FROM Users WHERE email = %s', (email,))
        account = cursor.fetchone()
        if account:
            flash("Account already exists!")
        elif not re.match(r'[^@]+@[^@]+\.[^@]+', email):
            flash("Invalid email address!")
        elif not re.match(r'[A-Za-z0-9]+', username):
            flash("Username must contain only characters and numbers!")
        elif not username or not user_password or not email:
            flash("Please fill out the form!")
        else:
            current_date = datetime.date.today()
            cursor.execute('INSERT INTO Users VALUES (%s, %s, %s, %s)',
                           (email, username, user_password, current_date.strftime('%Y-%m-%d %H:%M:%S'),))
            db.commit()
            flash("You have successfully registered!")
    elif request.method == 'POST':
        flash('Please fill out the form!')
    return render_template("register.html")


@app.route('/albums')
def albums():
    if app.config['DB_STATUS'] == '':
        flash("Please initialize database first!")
        return render_template("init.html")

    cursor.execute("SELECT * FROM Album")
    results = cursor.fetchall()
    return render_template("albums.html", data=results)


@app.route('/artists')
def artists():
    if app.config['DB_STATUS'] == '':
        flash("Please initialize database first!")
        return render_template("init.html")

    cursor.execute("SELECT * FROM Artist")
    results = cursor.fetchall()
    return render_template("artists.html", data=results)


@app.route('/songs')
def songs():
    if app.config['DB_STATUS'] == '':
        flash("Please initialize database first!")
        return render_template("init.html")

    cursor.execute("SELECT * FROM Song")
    results = cursor.fetchall()
    return render_template("songs.html", data=results)


@app.route('/users')
def users():
    cursor.execute("SELECT * FROM Users")
    results = cursor.fetchall()
    return render_template("users.html", data=results)


@app.route('/follows')
def follows():
    cursor.execute("SELECT * FROM Follows")
    results = cursor.fetchall()
    return render_template("follows.html", data=results)


@app.route('/reviews')
def reviews():
    if app.config['DB_STATUS'] == '':
        flash("Please initialize database first!")
        return render_template("init.html")

    cursor.execute("SELECT * FROM Review")
    results = cursor.fetchall()
    return render_template("reviews.html", data=results)


@app.route('/topalbums')
def topalbums():
    if app.config['DB_STATUS'] == '':
        flash("Please initialize database first!")
        return render_template("init.html")

    cursor.execute(
        "SELECT artist_name, album_name, averageRating FROM (SELECT Review.album_id, Artist.artist_id, Artist.artist_name, Album.album_name, avg(review_rating) As averageRating FROM Review  LEFT JOIN Album ON Album.album_id = Review.album_id LEFT JOIN Artist ON Artist.artist_id = Album.artist_id GROUP BY Artist.artist_id, Review.album_id) a WHERE NOT EXISTS (SELECT * FROM (SELECT Review.album_id, Artist.artist_id, Artist.artist_name,  avg(review_rating) As averageRating FROM Review LEFT JOIN Album ON Album.album_id = Review.album_id LEFT JOIN Artist ON Artist.artist_id = Album.artist_id GROUP BY Artist.artist_id, Review.album_id) b WHERE a.artist_id = b.artist_id AND a.averageRating < b.averageRating ) ORDER BY averageRating DESC")
    results = cursor.fetchall()
    return render_template("topalbums.html", data=results)


@app.route('/mostreviews')
def mostreviews():
    if app.config['DB_STATUS'] == '':
        flash("Please initialize database first!")
        return render_template("init.html")

    cursor.execute(
        "SELECT Album.album_name, COUNT(Review.album_id) as review_count FROM Album LEFT JOIN Review ON Album.album_id = Review.album_id LEFT JOIN Users ON Review.email = Users.email WHERE YEAR(Users.user_registration_date) = YEAR(NOW()) - 1 GROUP BY Album.album_name ORDER BY review_count DESC")
    results = cursor.fetchall()
    return render_template("mostreviews.html", data=results)


@app.route('/delete_db')
def delete_db():
    app.config['DB_STATUS'] = ''
    if delete_sql_tables(db): return 'Database is empty now'


@app.route('/create_db')
def create_db():
    if create_sql_tables(db): return 'Database tables created'


@app.route('/fill_db')
def fill_db():
    fill_sql_tables(db)


# if database is already initialized then it will return to home page
# TODO: when we have a proper website -> a proper redirect and warning message
@app.route('/initialize')
def initialize_db():
    if not app.config['DB_STATUS']:
        app.config['DB_STATUS'] = 'SQL'
        delete_sql_tables(db)
        create_sql_tables(db)
        if fill_sql_tables(db):
            return render_template("index.html")
    else:
        return redirect('/')


@app.route('/reset')
def reset_db():
    if not app.config['DB_STATUS']:
        flash("Noothing to reset, please initialize database first!")
        return render_template("init.html")

    delete_sql_tables(db)
    # create_sql_tables(db)
    mongo_client.drop_database('imse_m2_mongo')
    app.config['DB_STATUS'] = ''
    # if fill_sql_tables(db): return render_template("index.html")
    return home()

# if a user has already reviewed an album, the review will be updated and the user will be notified
@app.route('/review_add', methods=["POST", "GET"])
def review_add():
    try:
        session["user"]
    except:
        flash("Please login first!")
        return render_template("index.html")

    if request.method == "POST" and 'album' in request.form and 'rating' in request.form and 'review' in request.form:
        name = request.form['album']
        if name == '':
            flash("Please add an album name")
            return render_template("review_add.html")
        rating = request.form['rating']

        if rating == '':
            flash("Please add a rating")
            return render_template("review_add.html")
        else:
            rating = int(request.form['rating'])

        review = request.form['review']
        cursor.execute('SELECT album_id FROM Album WHERE album_name LIKE %s', (name,))
        album = cursor.fetchone()
        if album is None:
            flash("Incorrect Album")
            return render_template("review_add.html")
        if rating < 1 or rating > 5:
            flash("Rating must be between 1 and 5")
            return render_template("review_add.html")
        if review is None:
            review = ''
        for row in album:
            albumid = row

        print(albumid, file=sys.stderr)
        current_date = datetime.date.today()
        try:
            cursor.execute('INSERT INTO Review VALUES (%s, %s, %s, %s, %s)',
                           (albumid, session["user"], review, rating, current_date.strftime('%Y-%m-%d %H:%M:%S')))
        except:
            flash("Review on album updated")
            email_current = session["user"]
            cursor.execute('DELETE FROM  Review WHERE album_id = %s and email = %s', (albumid, email_current))
            cursor.execute('INSERT INTO Review VALUES (%s, %s, %s, %s, %s)',
                           (albumid, session["user"], review, rating, current_date.strftime('%Y-%m-%d %H:%M:%S')))
            db.commit()
            return render_template("review_add.html")
        db.commit()
        flash("Review successfully submitted!")

    elif request.method == 'POST':
        flash('Please fill out the form!')

    return render_template("review_add.html")


@app.route('/migrate')
def migrate():
    if app.config['DB_STATUS'] == '':
        flash("Please initialize database first!")
        return render_template("init.html")

    try:
        migrate_database(db, mongo_client, mongo_db)
    except:
        flash('Migration already done')
        return render_template("index.html")

    app.config['DB_STATUS'] = 'MONGO'
    flash('Migration to MongoDB done')
    return render_template("index.html")

