from datetime import datetime
from enum import auto
import sqlalchemy
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import Column, Integer, String, ForeignKey
from sqlalchemy.orm import relation, relationship
import pandas as pd
import config


# load engine
engine = sqlalchemy.create_engine(
    "mysql+mysqlconnector://{}:{}@{}:3306/{}".format(
        config.MYSQL_CONFIG['user'], 
        config.MYSQL_CONFIG['password'], 
        config.MYSQL_CONFIG['host'], 
        config.MYSQL_CONFIG['database']
))

# define and create the table
Base = declarative_base()

# Create a session
Session = sqlalchemy.orm.sessionmaker()
Session.configure(bind=engine)
session = Session()


# define tables
class Artists(Base):
    __tablename__ = 'Artists'

    artist_id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(length=30), index=True)
    songs = relationship("Songs")
    albums = relationship("Albums")


class Songs(Base):
    __tablename__ = 'Songs'

    song_id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(length=20), index=True)
    artist_id = Column(Integer, ForeignKey('Artists.artist_id'), index=True)
    album_id = Column(Integer, ForeignKey('Albums.album_id'), index=True)
    playlists = relationship("Playlists")


class Albums(Base):
    __tablename__ = 'Albums'

    album_id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(length=30), index=True)
    artist_id = Column(Integer, ForeignKey('Artists.artist_id'), index=True)


class Users(Base):
    __tablename__ = 'Users'

    user_id = Column(Integer, primary_key=True, autoincrement=True)
    username = Column(String(length=30))
    password = Column(String(length=30))
    dob = Column(sqlalchemy.types.DateTime(timezone=True))
    playlists = relationship("Playlists")
    sqlalchemy.Index('index', username, password)


class Playlists(Base):
    __tablename__ = 'Playlists'

    playlist_id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(length=30), index=True)
    song_id = Column(Integer, ForeignKey('Songs.song_id'), index=True)
    user_id = Column(Integer, ForeignKey('Users.user_id'), index=True)


def loadData(file: str):
    df = pd.read_csv(file)
    df = df.where((pd.notnull(df)), None)
    return df

def addDataToDB(file: str, cols: list):
    df = loadData(file, cols)

    data = []
    for _, (song_name, artist_name, album_name) in df.iterrows():
        artist = Artists(name=artist_name)
        album = Albums(name=album_name, artist_id=artist.artist_id)
        song = Songs(name=song_name, artist_id=artist.artist_id, album_id=album.album_id)
        data.append(artist)
        data.append(album)
        data.append(song)

    n = len(data)
    for i in range(0, n, 100):
        session.add_all(data[i:i+100])
        session.commit()
        print(f"first {i+100}/{n} data committed")


def main():
    # creates all tables based on metadata
    Base.metadata.create_all(engine)

    # addDataToDB('./resources/spotify_cleaned.csv', ['artist_name', 'album', 'track_name'])

    artist1 = Artists(name='Olivia Rodrigo')
    artist2 = Artists(name='Drake')
    artist3 = Artists(name='Pink Guy')

    album1 = Albums(name='sour', artist_id=1)
    album2 = Albums(name='Certified Lover Boy', artist_id=2)
    album3 = Albums(name='Pink Season', artist_id=3)

    song1 = Songs(name='Brutal', artist_id=1, album_id=1)
    song2 = Songs(name='Traitor', artist_id=1, album_id=1)
    song3 = Songs(name='Drivers License', artist_id=1, album_id=1)
    song4 = Songs(name='Champaign Poetry', artist_id=2, album_id=1)
    song5 = Songs(name="Papi's Home", artist_id=2, album_id=2)
    song6 = Songs(name='Fried Noodles', artist_id=3, album_id=3)
    song7 = Songs(name='We Fall Again', artist_id=3, album_id=3)

    user1 = Users(username='Ham Bone', password='mysecurepassword123', dob='2000-08-19')
    user2 = Users(username='Jeb Smith', password='mysecurepassword456', dob='1990-08-14')
    user3 = Users(username='Drake Ricardo', password='passpasspass', dob='1998-04-26')

    playlist1 = Playlists(name='Super Good Music', song_id=1, user_id=1)
    playlist2 = Playlists(name='Super Good Music', song_id=2, user_id=1)
    playlist3 = Playlists(name='Super Good Music', song_id=3, user_id=1)
    playlist4 = Playlists(name='Groovy Tunes', song_id=2, user_id=2)
    playlist5 = Playlists(name='Groovy Tunes', song_id=4, user_id=2)
    playlist6 = Playlists(name='Ebig Mix', song_id=3, user_id=3)
    playlist7 = Playlists(name='Ebig Mix', song_id=4, user_id=3)
    playlist8 = Playlists(name='Ebig Mix', song_id=5, user_id=3)

    session.add_all([
        artist1, artist2, artist3,
        album1, album2, album3,
        song1, song2, song3, song4, song5, song6, song7,
        user1, user2, user3,
        playlist1, playlist2, playlist3, playlist4, playlist5, playlist6, playlist7, playlist8
    ])
    session.commit()

    print("All data loaded and committed!!")

if __name__=="__main__":
    main()
    