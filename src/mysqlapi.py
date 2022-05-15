from datetime import datetime, timedelta
import mysql.connector as msqc
from typing import List
import toml
import os
import config


class MySqlAPI:

    def __init__(self):
        self.connection = msqc.connect(**config.MYSQL_CONFIG)
        self._cursor = self.connection.cursor(prepared=True)

    def get_account(self, username, password):
        self._cursor.execute(
            'SELECT * FROM Users WHERE username = %s AND password = %s',
            (username, password,)
        )
        return self._cursor.fetchone()

    def create_account(self, username, password):
        self._cursor.execute(
            'INSERT INTO Users (username, password, dob) VALUES (%s, %s, %s)',
            (username, password, datetime.now().strftime('%Y-%m-%d %H:%M:%S'),)
        )
        self.connection.commit()

    def find_user(self, username):
        self._cursor.execute('SELECT * FROM Users WHERE username = %s', (username,))
        return self._cursor.fetchone()

    def get_view(self, table, attrs: List[str] = None):
        raise NotImplementedError

    def fetch_albums(self):
        self._cursor.execute(
            'SELECT album_name, artist_name, alpha.album_id, song_count, artist_id FROM ' + \
            '(SELECT Albums.name as album_name, Artists.name as artist_name, Albums.album_id, Albums.artist_id FROM ' + \
            'musik4lyfe.Albums INNER JOIN musik4lyfe.Artists ON musik4lyfe.Albums.artist_id = musik4lyfe.Artists.artist_id) alpha ' + \
            'INNER JOIN (SELECT album_id, count(*) as song_count FROM musik4lyfe.Songs GROUP BY album_id) beta ON alpha.album_id = beta.album_id'
        )
        return self._cursor.fetchall() 

    def fetch_single_album(self, album_id):
        self._cursor.execute(
            'SELECT Songs.name, Artists.name, Artists.artist_id FROM ' + \
            '(musik4lyfe.Songs Songs JOIN musik4lyfe.Albums Albums ON (Songs.album_id = Albums.album_id AND Songs.album_id = %s)) ' + \
            'INNER JOIN musik4lyfe.Artists ON Artists.artist_id = Albums.artist_id', (album_id,)
        )
        return self._cursor.fetchall()

    def fetch_artists(self):
        self._cursor.execute(
            'SELECT Artists.name as artist_name, count(distinct Albums.album_id) as album_count, count(Songs.song_id) as song_count, Artists.artist_id as artist_id ' +\
            'FROM (musik4lyfe.Artists Artists INNER JOIN musik4lyfe.Albums Albums ON Artists.artist_id = Albums.artist_id) INNER JOIN musik4lyfe.Songs Songs ON Artists.artist_id = Songs.artist_id ' +\
            'GROUP BY Artists.artist_id'
        )
        return self._cursor.fetchall()
    
    def fetch_single_artist(self, artist_id):
        self._cursor.execute(
            'SELECT album_name, alpha.album_id as album_id, song_count FROM ' + \
            '(SELECT Albums.name as album_name, Artists.name as artist_name, Albums.album_id, Albums.artist_id ' +\
            'FROM musik4lyfe.Albums INNER JOIN musik4lyfe.Artists ON musik4lyfe.Albums.artist_id = musik4lyfe.Artists.artist_id) ' +\
            'alpha INNER JOIN (SELECT album_id, count(*) as song_count FROM musik4lyfe.Songs GROUP BY album_id) beta ON ' + \
            'alpha.album_id = beta.album_id and alpha.artist_id = %s', (artist_id,)
        )
        return self._cursor.fetchall()

    def fetch_songs(self):
        self._cursor.execute(
            'select distinct Songs.name as song_name, Artists.name, Albums.name as album_name, Albums.artist_id as artist_id, Albums.album_id as album_id from ' +\
            'musik4lyfe.Songs Songs inner join musik4lyfe.Albums Albums on Songs.album_id = Albums.album_id inner join musik4lyfe.Artists Artists on ' + \
            'Songs.artist_id = Artists.artist_id order by Songs.name'
        )
        return self._cursor.fetchall()

    def search_artist(self, artist_string):
        string = '%' + artist_string + '%'
        self._cursor.execute(
            'SELECT * FROM (SELECT DISTINCT Artists.name as artist_name, count( distinct Albums.album_id) as album_count, count(Songs.song_id) as song_count, ' + \
            'Artists.artist_id as artist_id FROM (musik4lyfe.Artists Artists INNER JOIN musik4lyfe.Albums Albums ON Artists.artist_id = Albums.artist_id) ' + \
            'INNER JOIN musik4lyfe.Songs Songs ON Artists.artist_id = Songs.artist_id GROUP BY Artists.artist_id) a WHERE artist_name LIKE %s', (string,))    
        return self._cursor.fetchall()

    def search_album(self, album_string):
        string = '%' + album_string + '%'
        self._cursor.execute(
            'SELECT * FROM (SELECT DISTINCT album_name, artist_name, alpha.album_id, song_count, artist_id FROM ' + \
            '(SELECT Albums.name as album_name, Artists.name as artist_name, Albums.album_id, Albums.artist_id FROM musik4lyfe.Albums ' + \
            'INNER JOIN musik4lyfe.Artists ON musik4lyfe.Albums.artist_id = musik4lyfe.Artists.artist_id) alpha INNER JOIN (SELECT album_id, count(*) ' + \
            'as song_count FROM musik4lyfe.Songs GROUP BY album_id) beta ON alpha.album_id = beta.album_id) a WHERE album_name LIKE %s', (string,))    
        return self._cursor.fetchall()

    def search_song(self, song_string):
        string = '%' + song_string + '%'
        self._cursor.execute(
            'SELECT * FROM (select DISTINCT Songs.name as song_name, Artists.name, Albums.name as album_name, Albums.artist_id as artist_id, Albums.album_id as album_id from ' + \
            'musik4lyfe.Songs Songs inner join musik4lyfe.Albums Albums on Songs.album_id = Albums.album_id join musik4lyfe.Artists Artists on Songs.artist_id = Artists.artist_id ' + \
            'order by Songs.name) a WHERE song_name LIKE %s', (string,))
        return self._cursor.fetchall()

    def add_song(self, song, artist, album):
        self._cursor.execute('call add_song(?, ?, ?, ?)', (song, artist, album, None))
