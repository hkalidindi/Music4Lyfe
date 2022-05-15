from flask import (
    Flask, 
    render_template,
    session,
    url_for,
    flash,
    redirect,
    request
)
from form import MusicSearchForm
import mysqlapi
import re, os


PATH = os.getcwd()

app = Flask(__name__, static_folder=rf'{PATH}')
app.secret_key = 'super_secret_key_123'
mysql = mysqlapi.MySqlAPI()

@app.route('/')
@app.route('/index')
def home():
    if 'loggedin' in session:
        return render_template('index.html', username=session['username'])
    return redirect(url_for('login'))

@app.route('/homepage', methods=["POST", "GET"])   
def homepage():
    search = MusicSearchForm(request.form)
    if request.method == 'POST':
        return search_results(search)

    return render_template('home.html', form=search)

@app.route('/login', methods=["POST", "GET"])
def login():
    msg = ''
    if request.method == 'POST' and 'username' in request.form and 'password' in request.form:
        user_ = request.form.get('username')
        pass_ = request.form.get('password')
        account = mysql.get_account(user_, pass_)
        if account:
            session['loggedin'] = True
            session['id'] = account[0]
            session['username'] = account[1]
            msg = 'Login successful.'
            return redirect('homepage')
        else:
            msg = 'Incorrect username or password.'
    return render_template('login.html', msg=msg)

@app.route('/logout')
def logout():
    session.pop('loggedin', None)
    session.pop('id', None)
    session.pop('username', None)
    return redirect(url_for('login'))

@app.route('/database_view')
def database_view():
    raise NotImplementedError

@app.route('/register', methods=["POST", "GET"])
def register():
    msg = ''
    if request.method == 'POST' and 'username' in request.form and 'password' in request.form:
        user_ = request.form.get('username')
        pass_ = request.form.get('password')
        # we don't accept new accounts having an already-
        # used username
        account = mysql.find_user(user_)
        if account:
            msg = 'Username already exists!'
        elif re.match(r'^[^\s]+$', pass_)[0] != pass_ or re.match(r'^[^\s]+$', user_)[0] != user_:
            msg = 'Username must only contain English characters, numers, and special characters.'
        else:
            mysql.create_account(user_, pass_)
            msg = 'Registration successful.'
            return redirect(url_for('login'))
    elif request.method == 'POST':
        msg = 'Invalid username or password. Both values must be provided.'
    return render_template('register.html', msg=msg)

@app.route('/album', methods=["POST", "GET"])
def albums():
    if 'loggedin' in session:
        search = MusicSearchForm(request.form)
        if request.method == 'POST':
            return search_results(search)
        cursor_result = mysql.fetch_albums()
        return render_template('album.html', album_data = cursor_result, form=search)
    return redirect(url_for('login'))

@app.route('/results', methods=["POST", "GET"])
def search_results(search):
    results = []
    search_string = search.data['search']
    if search_string:
        if search.data['select'] == 'Artist':
            results = mysql.search_artist(search_string)
            return render_template('resultsArtists.html', data=results, form=search, search=search_string)
        elif search.data['select'] == 'Album':
            results = mysql.search_album(search_string)
            return render_template('resultsAlbums.html', data=results, form=search, search=search_string)
        elif search.data['select'] == 'Song':
            results = mysql.search_song(search_string)
            return render_template('resultsSongs.html', data=results, form=search, search=search_string)
    if not results:
        flash('No results found!')
        return redirect('/homepage')

@app.route('/albumview/<string:album_name>/<string:id>', methods=["POST", "GET"])
def albumview(album_name, id):
    search = MusicSearchForm(request.form)
    if request.method == 'POST':
        return search_results(search)

    cursor_result = mysql.fetch_single_album(id)
    return render_template('albumview.html', data=cursor_result, form=search, the_album_name=album_name)


@app.route('/artists', methods=["POST", "GET"])
def artists():
    if 'loggedin' in session:
        search = MusicSearchForm(request.form)
        if request.method == 'POST':
            return search_results(search)
        cursor_result = mysql.fetch_artists()
        return render_template('artists.html', artists_data = cursor_result, form=search)
    return redirect(url_for('login'))


@app.route('/songs', methods=["POST", "GET"])
def songs():
    if 'loggedin' in session:
        search = MusicSearchForm(request.form)
        if request.method == 'POST':
            return search_results(search)
        cursor_result = mysql.fetch_songs()
        return render_template('songs.html', songs_data=cursor_result, form=search)
    return redirect(url_for('login'))

@app.route('/artistview/<string:artist_name>/<string:id>', methods=["POST", "GET"])
def singlealbumview(artist_name, id):
    search = MusicSearchForm(request.form)
    if request.method == 'POST':
        return search_results(search)

    cursor_result = mysql.fetch_single_artist(id)
    return render_template('artistview.html', data=cursor_result, form=search, the_artist_name=artist_name)


@app.route('/add songs', methods=["POST", "GET"])
def addSongs():
    if 'loggedin' in session:
        search = MusicSearchForm(request.form)
        if 'song' in request.args:
            song = request.args.get('song')
            artist = request.args.get('artist')
            album = request.args.get('album')
            mysql.add_song(song, artist, album)
            
            return render_template('addsongs.html', form=search)
        return render_template('addsongs.html', form=search)
    return redirect(url_for('login'))


if __name__ == '__main__':
    app.run(debug=True)

