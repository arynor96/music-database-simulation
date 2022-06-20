import random
import sys

import pandas as pd
import numpy as np


def delete_sql_tables(db):
    cursor = db.cursor()

    # do not change the order, constraints problem may happen due to foreign key

    cursor.execute("DROP TABLE IF EXISTS Follows")
    cursor.execute("DROP TABLE IF EXISTS Likes")
    cursor.execute("DROP TABLE IF EXISTS Review")
    cursor.execute("DROP TABLE IF EXISTS Song")
    cursor.execute("DROP TABLE IF EXISTS Album")
    cursor.execute("DROP TABLE IF EXISTS Artist")
    cursor.execute("DROP TABLE IF EXISTS Users")

    db.commit()
    cursor.close()
    return True


def create_sql_tables(db):
    cursor = db.cursor()

    sql_statement = '''
    
            CREATE TABLE Artist (
                artist_id INTEGER NOT NULL AUTO_INCREMENT,
                artist_name VARCHAR(50) NOT NULL,
                artist_genre VARCHAR(50),
                PRIMARY KEY (artist_id)
            );
    
            CREATE TABLE Album (
                album_id INTEGER NOT NULL AUTO_INCREMENT,
                album_name VARCHAR(50) NOT NULL,
                album_release_date DATE NOT NULL,
                artist_id INTEGER NOT NULL,
                PRIMARY KEY (album_id),
                FOREIGN KEY (artist_id) REFERENCES Artist(artist_id) ON DELETE CASCADE
            );
            
            CREATE TABLE Users(
                email VARCHAR(50) NOT NULL,
                username VARCHAR(50) NOT NULL,
                password VARCHAR(50) NOT NULL,
                user_registration_date DATE NOT NULL,
                PRIMARY KEY (email)
                
            );
            
            CREATE TABLE Follows(
                email_current VARCHAR(50) NOT NULL,
                followed_by VARCHAR(50) NOT NULL,
                FOREIGN KEY (email_current) REFERENCES Users(email) ON DELETE CASCADE,
                FOREIGN KEY (followed_by) REFERENCES Users(email) ON DELETE CASCADE,
                PRIMARY KEY (email_current,followed_by)
            );
            
            CREATE TABLE Song(
                song_id INTEGER NOT NULL AUTO_INCREMENT,
                song_title VARCHAR(50) NOT NULL,
                song_length INTEGER,
                song_release_date DATE,
                album_id INTEGER,
                PRIMARY KEY (song_id),
                FOREIGN KEY (album_id) REFERENCES Album(album_id) ON DELETE CASCADE                
            );
            
            CREATE TABLE Review(
                 album_id INTEGER,
                 email VARCHAR(50),
                 text VARCHAR(200),
                 review_rating INTEGER NOT NULL,
                 review_date DATE NOT NULL,
                 CHECK (review_rating<=5),
                 CHECK (review_rating>=0),
                 FOREIGN KEY (album_id) REFERENCES Album(album_id) ON DELETE CASCADE,
                 FOREIGN KEY (email) REFERENCES Users(email),
                 PRIMARY KEY (album_id,email)  
            );
            
            CREATE TABLE Likes(
                song_id INTEGER,
                email VARCHAR(50),
                FOREIGN KEY (song_id) REFERENCES Song(song_id) ON DELETE CASCADE,
                FOREIGN KEY (email) REFERENCES Users(email) ON DELETE CASCADE,
                PRIMARY KEY (song_id,email)
            );
            
            
            
           
    
    '''

    # source: https://pythonexamples.org/python-iterate-over-words-of-string/
    for part in sql_statement.split(';'):
        if len(part.strip()) > 0:
            cursor.execute(part)

    db.commit()
    cursor.close()
    return True


def fill_sql_tables(db):
    cursor = db.cursor()

    # artists
    document = pd.read_csv('app/helpers/db_data/artists.csv')
    numberOfArtists = len(document.index)
    for index, line in document.iterrows():
        cursor.execute("INSERT INTO imse_m2_db.Artist (artist_name, artist_genre) VALUES" + " ('%s', '%s')" %
                       (line['artist_name'], line['artist_genre']))

        print("Added | Artist: " + line['artist_name'] + " | Genre: " + str(line['artist_genre']), file=sys.stderr)

    print("########## Artists added", file=sys.stderr)

    cursor.execute("UPDATE imse_m2_db.Artist SET artist_genre=NULL WHERE artist_genre='nan'")

    # albums

    document = pd.read_csv('app/helpers/db_data/albums.csv')
    numberOfAlbums = len(document.index)
    for index, line in document.iterrows():
        randomArtistId = random.randint(1, numberOfArtists)
        cursor.execute(
            "INSERT INTO imse_m2_db.Album (album_name, album_release_date, artist_id) VALUES" + " ('%s', '%s', %d)" %
            (line['album_name'], line['album_release_date'], randomArtistId))
        print("Added | Album: " + line['album_name'] + " | Date: " + str(
            line['album_release_date']) + " | Artist: " + str(randomArtistId), file=sys.stderr)

    print("########## Albums added", file=sys.stderr)

    # users

    document = pd.read_csv('app/helpers/db_data/users.csv')
    numberOfUsers = len(document.index)
    for index, line in document.iterrows():
        cursor.execute(
            "INSERT INTO imse_m2_db.Users (email, username, password, user_registration_date) VALUES" + " ('%s', '%s', '%s', '%s')" %
            (line['email'], line['username'], line['password'], line['user_registration_date']))
        print("Added | User " + line['email'] + " | Username: " + line['username'] + " | RegDate: " + str(
            line['user_registration_date']), file=sys.stderr)

    print("########## Users added", file=sys.stderr)

    # follows

    document = pd.read_csv('app/helpers/db_data/follows.csv')
    for index, line in document.iterrows():
        cursor.execute(
            "INSERT INTO imse_m2_db.Follows (email_current,followed_by) VALUES" + " ('%s', '%s')" %
            (line['email_current'], line['followed_by']))

    print("########## Followers created", file=sys.stderr)

    # songs

    document = pd.read_csv('app/helpers/db_data/songs.csv')
    numberOfSongs = len(document.index)
    for index, line in document.iterrows():
        randomAlbumId = random.randint(1, numberOfAlbums)
        cursor.execute(
            "INSERT INTO imse_m2_db.Song (song_title,song_length,song_release_date,album_id) VALUES" + " ('%s', %s, '%s',%d)" %
            (line['song_title'], line['song_length'], line['song_release_date'], randomAlbumId))

    print("########## Songs added", file=sys.stderr)

    # reviews

    document = pd.read_csv('app/helpers/db_data/reviews.csv')
    albumList = list(np.random.choice(np.arange(1, numberOfAlbums), len(document.index), replace=False))
    for index, line in document.iterrows():
        cursor.execute(
            "INSERT INTO imse_m2_db.Review (album_id,email,text,review_rating,review_date) VALUES" + " (%d, '%s', '%s',%d,'%s')" %
            (albumList.pop(),
             line['email'], line['text'], line['review_rating'], line['review_date']))

    albumList = list(np.random.choice(np.arange(1, numberOfAlbums), len(document.index), replace=False))
    random.shuffle(albumList)
    for index, line in document.iterrows():
        try : cursor.execute(
            "INSERT INTO imse_m2_db.Review (album_id,email,text,review_rating,review_date) VALUES" + " (%d, '%s', '%s',%d,'%s')" %
            (albumList.pop(),
             line['email'], line['text'], line['review_rating'], line['review_date']))
        except:
            print("Skipped, already reviewed", file=sys.stderr)

    albumList = list(np.random.choice(np.arange(1, numberOfAlbums), len(document.index), replace=False))
    random.shuffle(albumList)
    for index, line in document.iterrows():
        try:
            cursor.execute(
                "INSERT INTO imse_m2_db.Review (album_id,email,text,review_rating,review_date) VALUES" + " (%d, '%s', '%s',%d,'%s')" %
                (albumList.pop(),
                 line['email'], line['text'], line['review_rating'], line['review_date']))
        except:
            print("Skipped, already reviewed", file=sys.stderr)

    albumList = list(np.random.choice(np.arange(1, numberOfAlbums), len(document.index), replace=False))
    random.shuffle(albumList)
    random.shuffle(albumList)
    for index, line in document.iterrows():
        try:
            cursor.execute(
                "INSERT INTO imse_m2_db.Review (album_id,email,text,review_rating,review_date) VALUES" + " (%d, '%s', '%s',%d,'%s')" %
                (albumList.pop(),
                 line['email'], line['text'], line['review_rating'], line['review_date']))
        except:
            print("Skipped, already reviewed", file=sys.stderr)

    print("########## Reviews added", file=sys.stderr)


    # likes
    # will need some fixes for report

    document = pd.read_csv('app/helpers/db_data/likes.csv')
    songsList = list(np.random.choice(np.arange(1, numberOfSongs), len(document.index), replace=False))
    for index, line in document.iterrows():
        cursor.execute(
            "INSERT INTO imse_m2_db.Likes (song_id,email) VALUES" + " (%d, '%s')" %
            (songsList.pop(), line['email']))

    print("########## Likes added", file=sys.stderr)

    db.commit()
    cursor.close()

    return True
