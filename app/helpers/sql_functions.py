def delete_sql_tables(db):
    cursor = db.cursor()

    # do not change the order, constraints problem may happen due to foreign key
    cursor.execute('''DROP TABLE IF EXISTS Likes''')
    cursor.execute('''DROP TABLE IF EXISTS Review''')
    cursor.execute('''DROP TABLE IF EXISTS Song''')
    cursor.execute('''DROP TABLE IF EXISTS Album''')
    cursor.execute('''DROP TABLE IF EXISTS Artist''')
    cursor.execute('''DROP TABLE IF EXISTS Users''')
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
                album_release_date DATE,
                artist_id INTEGER NOT NULL,
                PRIMARY KEY (album_id),
                FOREIGN KEY (artist_id) REFERENCES Artist(artist_id) ON DELETE CASCADE
            );
            
            CREATE Table Users(
                email VARCHAR(50) NOT NULL,
                username VARCHAR(50) NOT NULL,
                password VARCHAR(50) NOT NULL,
                user_registration_date DATE,
                followed_by VARCHAR(50),
                PRIMARY KEY (email),
                FOREIGN KEY (followed_by) REFERENCES Users(email)
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
                FOREIGN KEY (email) REFERENCES Users(email) ON DELETE CASCADE,
                FOREIGN KEY (song_id) REFERENCES Song(song_id) ON DELETE CASCADE,
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
