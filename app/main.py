import sys
import re
import uuid

import numpy
import pymongo
from flask import Flask, render_template, redirect, session, flash, request, url_for, jsonify
import mysql.connector
import datetime
import re
import pandas as pd
import uuid

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

##### var
song_id = None


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
    if app.config['DB_STATUS'] != 'MONGO':
        if request.method == "POST" and 'email' in request.form and 'pass' in request.form:
            session.permanent = True
            user = request.form['email']
            user_password = request.form['pass']
            cursor.execute('SELECT * FROM Users WHERE email = %s AND password = %s', (user, user_password,))
            account = cursor.fetchone()
            if account:
                session["user"] = user
                flash("Login successful!")
                return redirect(url_for("home"))
            else:
                flash("Incorrect email/password!")
                return render_template("login.html")
        else:
            if "user" in session:
                flash("Already logged in!")
                return redirect(url_for("home"))
            return render_template("login.html")
    else:
        if request.method == "POST" and 'email' in request.form and 'pass' in request.form:
            session.permanent = True
            user = mongo_db.users.find_one({
                "email": request.form.get('email'),
                "password": request.form.get('pass')
            })
            if user:
                session["user"] = request.form.get('email')
                flash("Login successful!")
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
    if app.config['DB_STATUS'] != 'MONGO':
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
    else:
        if request.method == 'POST' and 'email' in request.form and 'username' in request.form and 'pass' in request.form:
            user = {
                "_id": uuid.uuid4().hex,
                "email": request.form.get('email'),
                "username": request.form.get('username'),
                "password": request.form.get('pass'),
                "user_registration_date": datetime.datetime.now()
            }
            if mongo_db.users.find_one({"email": user['email']}):
                flash("Account already exists!")
            mongo_db.users.insert_one(user)
            flash("You have successfully registered!")
            return redirect(url_for('home'))
        elif request.method == 'POST':
            flash('Please fill out the form!')
        return render_template("register.html")


@app.route('/albums')
def albums():
    if app.config['DB_STATUS'] == '':
        flash("Please initialize database first!")
        return render_template("init.html")

    if app.config['DB_STATUS'] == 'MONGO':
        collection = mongo_db['albums']
        results = []
        for document in collection.find({}, {"_id": 0}):
            results.append(document.values())
        return render_template("albums.html", data=results, mongoyes="MongoDB results")

    cursor.execute("SELECT * FROM Album")
    results = cursor.fetchall()
    return render_template("albums.html", data=results)


@app.route('/artists')
def artists():
    if app.config['DB_STATUS'] == '':
        flash("Please initialize database first!")
        return render_template("init.html")

    if app.config['DB_STATUS'] == 'MONGO':
        collection = mongo_db['artists']
        results = []
        for document in collection.find({}, {"_id": 0}):
            results.append(document.values())
        return render_template("artists.html", data=results, mongoyes="MongoDB results")
    else:
        cursor.execute("SELECT * FROM Artist")
        results = cursor.fetchall()
        return render_template("artists.html", data=results)


@app.route('/songs')
def songs():
    if app.config['DB_STATUS'] == '':
        flash("Please initialize database first!")
        return render_template("init.html")

    if app.config['DB_STATUS'] == 'MONGO':
        collection = mongo_db['songs']
        results = []
        for document in collection.find({}, {"_id": 0}):
            results.append(document.values())
        return render_template("songs.html", data=results, mongoyes="MongoDB results")

    cursor.execute("SELECT * FROM Song")
    results = cursor.fetchall()
    return render_template("songs.html", data=results)


@app.route('/liked')
def likes():
    if app.config['DB_STATUS'] == '':
        flash("Please initialize database first!")
        return render_template("init.html")
    try:
        session["user"]
    except:
        flash("Please login first!")
        return render_template("index.html")

    if app.config['DB_STATUS'] == 'MONGO':
        pipeline = [
            {
                '$lookup': {
                    'from': 'songs',
                    'localField': 'song_id',
                    'foreignField': 'song_id',
                    'as': 'songs_new'
                }
            },

            {'$unwind': "$songs_new"},

            {
                '$lookup': {
                    'from': 'users',
                    'localField': 'email',
                    'foreignField': 'email',
                    'as': 'users_new'
                }
            },

            {'$unwind': "$users_new"},

            {
                '$project': {
                    "_id": 0,
                    "song_id": 1,
                    "song_name": '$songs_new.song_title',
                    "song_release_date": '$songs_new.song_release_date',
                    "user_email": '$users_new.email',

                }
            }

        ]

        # this sorts the data so that only the liked songs by the current user are displayed
        df = pd.DataFrame(list(mongo_db['likes'].aggregate(pipeline)))
        # filter = df["user_email"] == session["user"]
        df = df[df.user_email == session["user"]]
        df = df.drop('user_email', 1)
        results = df.values
        return render_template("liked.html", data=results, mongoyes="MongoDB results")

    cursor.execute(
        'SELECT song_title, song_length, song_release_date  FROM Likes LEFT JOIN Song ON Likes.song_id = Song.song_id WHERE email = %s',
        (session["user"],))
    results = cursor.fetchall()
    return render_template("liked.html", data=results)


@app.route('/search_song', methods=['POST', 'GET'])
def search_song():
    if app.config['DB_STATUS'] == '':
        flash("Please initialize database first!")
        return render_template("init.html")

    if app.config['DB_STATUS'] == 'SQL':
        if request.method == "POST" and 'song' in request.form:
            songname = request.form['song']
            if songname == '':
                flash("Please add a song name")
                return render_template("search_songs.html")
            # flash("This has not been implemented for SQL. Please migrate to MongoDB!")
            cursor.execute("SELECT * FROM Song WHERE song_title LIKE %s", (songname,))
            results = cursor.fetchall()
            cursor.execute("SELECT song_id FROM Song WHERE song_title LIKE %s", (songname,))

            global song_id
            row = cursor.fetchone()

            try:
                data = row[0]
            except:
                flash("Song not found!")
                return render_template("search_songs.html")

            song_id = int(data)
            print(song_id, file=sys.stderr)

            return render_template("results.html", data=results, mongoyes="Search results")
    else:
        if request.method == "POST" and 'song' in request.form:
            songname = request.form['song']
            if songname == '':
                flash("Please add a song name")
                return render_template("search_songs.html")

            song = mongo_db['songs'].find_one({'song_title': re.compile('^' + songname + '$', re.IGNORECASE)})

            try:
                song_title = song.get('song_title')
                song_id = song.get('song_id')
                song_length = song.get('song_length')
                song_release_date = song.get('song_release_date')
                album_id = song.get('album_id')
            except:
                flash("Song not found!")
                return render_template("search_songs.html")

            lst = [song_id, song_title, song_length, song_release_date, album_id]
            df = pd.DataFrame(list(lst))

            results = df.values

            return render_template("results.html", data=results, mongoyes="Search results")

    return render_template("search_songs.html")


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


@app.route('/addtofavs')
def addToFavs():
    if app.config['DB_STATUS'] == '':
        flash("Please initialize database first!")
        return render_template("init.html")
    if song_id == None:
        flash("Song not found, can't be added to favorites!")
        return render_template("index.html")

    if app.config['DB_STATUS'] == 'MONGO':
        mydict = {"song_id": song_id,
                  "email": session["user"]
                  }
        try:
            mongo_db.likes.insert_one(mydict)
            flash("Song added to favorites!")
            return render_template("index.html")
        except:
            flash("You already like this song!")
            return render_template("index.html")

    try:
        cursor.execute('INSERT INTO Likes VALUES (%s, %s)',
                       (song_id, session["user"]))
    except:
        flash("You already like this song!")
        return render_template("index.html")

    flash("Song added to favorites!")
    return render_template("index.html")


@app.route('/reviews')
def reviews():
    if app.config['DB_STATUS'] == '':
        flash("Please initialize database first!")
        return render_template("init.html")

    if app.config['DB_STATUS'] == 'MONGO':
        collection = mongo_db['review']
        results = []
        for document in collection.find({}, {"_id": 0}):
            results.append(document.values())
        return render_template("reviews.html", data=results, mongoyes="MongoDB results")

    cursor.execute("SELECT * FROM Review")
    results = cursor.fetchall()
    return render_template("reviews.html", data=results)


@app.route('/topalbums')
def topalbums():
    if app.config['DB_STATUS'] == '':
        flash("Please initialize database first!")
        return render_template("init.html")

    if app.config['DB_STATUS'] == 'SQL':
        cursor.execute(
            "SELECT album_name, artist_name, averageRating FROM (SELECT Review.album_id, Artist.artist_id, Artist.artist_name, Album.album_name, avg(review_rating) As averageRating FROM Review  LEFT JOIN Album ON Album.album_id = Review.album_id LEFT JOIN Artist ON Artist.artist_id = Album.artist_id GROUP BY Artist.artist_id, Review.album_id) a WHERE NOT EXISTS (SELECT * FROM (SELECT Review.album_id, Artist.artist_id, Artist.artist_name,  avg(review_rating) As averageRating FROM Review LEFT JOIN Album ON Album.album_id = Review.album_id LEFT JOIN Artist ON Artist.artist_id = Album.artist_id GROUP BY Artist.artist_id, Review.album_id) b WHERE a.artist_id = b.artist_id AND a.averageRating < b.averageRating ) ORDER BY averageRating DESC")
        results = cursor.fetchall()
        return render_template("topalbums.html", data=results)
    else:
        pipeline = [
            {
                '$lookup': {
                    'from': 'review',
                    'localField': 'album_id',
                    'foreignField': 'album_id',
                    'as': 'reviews_new'
                }
            },

            {'$unwind': "$reviews_new"},
            {
                '$lookup': {
                    'from': 'artists',
                    'localField': 'artist_id',
                    'foreignField': 'artist_id',
                    'as': 'artist_id2'
                }
            },
            {'$unwind': "$artist_id2"},

            {
                '$project': {
                    "_id": 0,
                    "album_name": 1,
                    "artist_name": '$artist_id2.artist_name',
                    "review_rating": '$reviews_new.review_rating'

                }
            }

        ]

        df = pd.DataFrame(list(mongo_db['albums'].aggregate(pipeline)))

        cols = ['album_name', 'artist_name']
        df2 = df.groupby(cols)['review_rating'].mean().reset_index()
        df2 = df2.sort_values(by='review_rating', ascending=False)
        df2 = df2.drop_duplicates(subset=['artist_name'], keep="first")

        results = df2.values
        return render_template("topalbums.html", data=results, mongoyes="MongoDB results")


@app.route('/mostreviews')
def mostreviews():
    if app.config['DB_STATUS'] == '':
        flash("Please initialize database first!")
        return render_template("init.html")
    if app.config['DB_STATUS'] == 'SQL':
        cursor.execute(
            "SELECT Album.album_name, COUNT(Review.album_id) as review_count FROM Album LEFT JOIN Review ON Album.album_id = Review.album_id LEFT JOIN Users ON Review.email = Users.email WHERE YEAR(Users.user_registration_date) = YEAR(NOW()) - 1 GROUP BY Album.album_name ORDER BY review_count DESC")
        results = cursor.fetchall()
        return render_template("mostreviews.html", data=results)
    else:
        pipeline = [
            {
                '$lookup': {
                    'from': 'review', 
                    'localField': 'album_id', 
                    'foreignField': 'album_id', 
                    'as': 'reviews_new'
                }
            }, {
                '$unwind': '$reviews_new'
            }, {
                '$lookup': {
                    'from': 'users', 
                    'localField': 'reviews_new.email', 
                    'foreignField': 'email', 
                    'as': 'users_new'
                }
            }, {
                '$unwind': '$users_new'
            }, {
                '$match': {
                    'users_new.user_registration_date': {
                        '$gte': datetime.datetime(2021, 1, 1, 0, 0, 0, tzinfo=datetime.timezone.utc), 
                        '$lte': datetime.datetime(2021, 12, 31, 23, 59, 59, tzinfo=datetime.timezone.utc)
                    }
                }
            }, {
                '$group': {
                    '_id': {
                        'album_name': '$album_name'
                    }, 
                    'review_count': {
                        '$sum': 1
                    }
                }
            }, {
                '$sort': {
                    'review_count': -1
                }
            }
        ]
        df = pd.DataFrame(list(mongo_db['albums'].aggregate(pipeline)))
        results = df.values
        return render_template("mostreviews.html", data=results, mongoyes="MongoDB results")



@app.route('/delete_db')
def delete_db():
    app.config['DB_STATUS'] = ''
    delete_sql_tables(db)
    # if delete_sql_tables(db): return 'Database is empty now'


@app.route('/create_db')
def create_db():
    if create_sql_tables(db): return 'Database tables created'


@app.route('/fill_db')
def fill_db():
    fill_sql_tables(db)


# if database is already initialized then it will return to home page
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

    # create_sql_tables(db)
    mongo_client.drop_database('imse_m2_mongo')
    delete_db()
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

    if app.config['DB_STATUS'] == 'SQL':
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
    else:
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

            # collectionAlbums = mongo_db['albums']
            # print(collectionAlbums.findOne({"artist_name": name}),file=sys.stderr)

            album = mongo_db['albums'].find_one({'album_name': re.compile('^' + name + '$', re.IGNORECASE)})

            try:
                album_name = album.get('album_name')
                album_id = album.get('album_id')
                # flash(album_name + " found!")
            except:
                flash("Album not found!")
                return render_template("review_add.html")

            current_time = datetime.date.today()
            mydict = {"album_id": album_id,
                      "email": session["user"],
                      "text": review,
                      "review_rating": rating,
                      "review_date": pd.to_datetime(current_time)}

            try:
                mongo_db['review'].insert_one(mydict)
                flash("Review Added!")
            except:
                mongo_db['review'].delete_one({'album_id': album_id,
                                               'email': session["user"]})
                mongo_db['review'].insert_one(mydict)
                flash("Review updated!")
                # filter2 = {"album_id": album_id,
                #          "email": session["user"]}
                # newValues = {"$set": {"text": review},
                #             "review_date": pd.to_datetime(current_time)}
                # mongo_db['review'].update_one(filter2, newValues)
                # flash("Review updated!")

        return render_template("review_add.html")


@app.route('/migrate')
def migrate():
    if app.config['DB_STATUS'] == '':
        flash("Please initialize database first!")
        return render_template("init.html")

    if app.config['DB_STATUS'] == 'SQL':
        # migrate_database(db, mongo_client, mongo_db)
        mongo_client.drop_database('imse_m2_mongo')
        # reset_db()
        # initialize_db()
        migrate_database(db, mongo_client, mongo_db)

    else:
        flash('Migration already done')
        return render_template("index.html")

    delete_sql_tables(db)
    app.config['DB_STATUS'] = 'MONGO'

    flash('Migration to MongoDB done')
    return render_template("index.html")
