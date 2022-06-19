import sys
import pandas as pd

# https://pandas.pydata.org/docs/reference/api/pandas.read_sql_table.html
# https://blog.panoply.io/how-to-read-a-sql-query-into-a-pandas-dataframe
# https://stackoverflow.com/questions/49221550/pandas-insert-a-dataframe-to-mongodb

import pymongo


# all collections should have an index, good for searching

def migrate_database(db, mongo_client, mongo_db):
    dataFrame_artist = pd.read_sql_query(sql='SELECT * FROM Artist', con=db)
    col = mongo_db['artists']
    col.create_index([('artist_id', pymongo.ASCENDING)], unique=True)
    col.insert_many(dataFrame_artist.to_dict('records'))

    dataFrame_albums = pd.read_sql_query(sql='SELECT * FROM Album', con=db)
    dataFrame_albums['album_release_date'] = pd.to_datetime(dataFrame_albums['album_release_date'])
    col = mongo_db['albums']
    col.create_index([('album_id', pymongo.ASCENDING)], unique=True)
    col.create_index([('artist_id', pymongo.ASCENDING)])
    col.insert_many(dataFrame_albums.to_dict('records'))

    dataFrame_users = pd.read_sql_query(sql='SELECT * FROM Users', con=db)
    dataFrame_users['user_registration_date'] = pd.to_datetime(dataFrame_users['user_registration_date'])
    col = mongo_db['users']
    col.create_index([('email', pymongo.ASCENDING)], unique=True)
    col.insert_many(dataFrame_users.to_dict('records'))

    dataFrame_songs = pd.read_sql_query(sql='SELECT * FROM Song', con=db)
    dataFrame_songs['song_release_date'] = pd.to_datetime(dataFrame_songs['song_release_date'])
    col = mongo_db['songs']
    col.create_index([('song_id', pymongo.ASCENDING)], unique=True)
    col.create_index([('album_id', pymongo.ASCENDING)])
    col.insert_many(dataFrame_songs.to_dict('records'))

    dataFrame_follows = pd.read_sql_query(sql='SELECT * FROM Follows', con=db)
    col = mongo_db['follows']
    col.create_index([('email_current', pymongo.ASCENDING),('followed_by', pymongo.ASCENDING)], unique=True)
    col.create_index([('email_current', pymongo.ASCENDING)])
    col.create_index([('followed_by', pymongo.ASCENDING)])
    col.insert_many(dataFrame_follows.to_dict('records'))

    dataFrame_likes = pd.read_sql_query(sql='SELECT * FROM Likes', con=db)
    col = mongo_db['likes']
    col.create_index([('song_id', pymongo.ASCENDING),('email', pymongo.ASCENDING)], unique=True)
    col.create_index([('song_id', pymongo.ASCENDING)])
    col.create_index([('email', pymongo.ASCENDING)])
    col.insert_many(dataFrame_likes.to_dict('records'))

    dataFrame_review = pd.read_sql_query(sql='SELECT * FROM Review', con=db)
    dataFrame_review['review_date'] = pd.to_datetime(dataFrame_review['review_date'])
    col = mongo_db['review']
    col.create_index([('album_id', pymongo.ASCENDING),('email', pymongo.ASCENDING)], unique=True)
    col.create_index([('album_id', pymongo.ASCENDING)])
    col.create_index([('email', pymongo.ASCENDING)])
    col.insert_many(dataFrame_review.to_dict('records'))

    return None
