import pymongo
from flask import Flask, render_template, redirect
import mysql.connector

from app.helpers.sql_functions import create_sql_tables, delete_sql_tables, fill_sql_tables

app = Flask(__name__)
app.config['DB_STATUS'] = ''
app.config['SECRET_KEY'] = 'ERROR'

sql_config = {'user': 'user', 'password': 'password', 'host': 'sql', 'port': '3306', 'database': 'imse_m2_db'}
db = mysql.connector.connect(**sql_config)

mongo_client = pymongo.MongoClient('mongodb://user:password@mongo:27017')
mongo_db = mongo_client['imse_m2_mongo']

cursor = db.cursor()
@app.route('/')
@app.route('/home')
def home():
    return render_template("index.html")

@app.route('/albums')
def albums():
    cursor.execute("SELECT * FROM Album")
    results = cursor.fetchall()
    return render_template("albums.html", data=results)

@app.route('/artists')
def artists():
    cursor.execute("SELECT * FROM Artist")
    results = cursor.fetchall()
    return render_template("artists.html", data=results)

@app.route('/songs')
def songs():
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
    cursor.execute("SELECT * FROM Review")
    results = cursor.fetchall()
    return render_template("reviews.html", data=results)

@app.route('/delete_db')
def delete_db():
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
        if fill_sql_tables(db): return 'Database initialization done'
    else:
        return redirect('/')



@app.route('/reset')
def reset_db():
    delete_sql_tables(db)
    create_sql_tables(db)
    if fill_sql_tables(db): return 'Database reset done'
