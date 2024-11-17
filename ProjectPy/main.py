from flask import Flask, render_template, request, redirect, url_for, flash, session
from models import db, User, Song
from sqlalchemy.exc import IntegrityError
from cryptography.fernet import Fernet
import os
from werkzeug.utils import secure_filename

app = Flask(__name__)
app.secret_key = "supersecretkey" # Flask needs secret key for session safety
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///database.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db.init_app(app)

with app.app_context():
    db.create_all()
UPLOAD_FOLDER = 'static/uploads/' # Upload folder 16
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER # Folder for songs that has been uploaded by user as artist

# Create the uploads directory if it does not exist
if not os.path.exists(UPLOAD_FOLDER): # If folder doesn't exist, program will create it himself
    os.makedirs(UPLOAD_FOLDER)

@app.route('/upload_song', methods=['POST']) # Function for upload song
def upload_song():
    if 'user_id' not in session:
        return redirect(url_for('login')) # If user was not logged in then he or she must log in

    user = User.query.get(session['user_id']) # Getting user id in db
    title = request.form['title'] # Getting a title of song from user to save in db
    genre = request.form['genre']  # Getting genre type
    audio_file = request.files['audio_file'] # Getting audio file

    if audio_file and title and genre:
        # Save the file to the uploads folder
        filename = secure_filename(audio_file.filename)
        file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        print('FILENAME:',filename,'//FILE_PATH:',file_path,'//UPDFOLDER:',app.config['UPLOAD_FOLDER'])
        audio_file.save(file_path)

        # Save song details in the database with genre
        song = Song(title=title, file_path=file_path, genre=genre, user_id=user.id)
        db.session.add(song)
        db.session.commit()

        flash('Song uploaded successfully!', 'success')
    else:
        flash('Failed to upload song. Please ensure all fields are filled.', 'danger')

    return redirect(url_for('artist_page'))
@app.route('/artists')
def artists():
    # Get all users who have registered as artists
    artists = User.query.filter(User.artist_name.isnot(None), User.artist_surname.isnot(None)).all()
    return render_template('artists.html', artists=artists)

@app.route('/artist_songs/<int:artist_id>')
def artist_songs(artist_id):
    # Get songs by the specified artist
    artist = User.query.get_or_404(artist_id) # Getting user's id to show his songs and 404 error if id doesn't exist
    songs = Song.query.filter_by(user_id=artist_id).all() # Filtering every song to their artists
    return render_template('artist_songs.html', artist=artist, songs=songs)


@app.route('/')
def main():
    return render_template('main.html')


@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        user = User.query.filter_by(username=username).first()
        if user and str(Fernet(user.key).decrypt(user.password).decode()) == password:
            session['user_id'] = user.id
            flash('Login successful!', 'info')
            return redirect(url_for('dashboard'))
        else:
            flash('Invalid credentials', 'danger')

    return render_template('login.html')


@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        skey=Fernet.generate_key()
        new_user = User(username=username, password=Fernet(skey).encrypt(password.encode("utf8")),key=skey)
        db.session.add(new_user)

        try:
            db.session.commit()
            session['user_id'] = new_user.id
            flash('Registration successful!', 'success')
            return redirect(url_for('dashboard'))
        except IntegrityError:
            db.session.rollback()
            flash('Username already exists. Please choose another one.', 'danger')

    return render_template('register.html')

@app.route('/logout')
def logout():
    session.pop('user_id', None)  # Remove user from session
    flash('You have been logged out.', 'info')
    return redirect(url_for('main'))

@app.route('/profile', methods=['GET', 'POST'])
def profile():
    if 'user_id' not in session:
        return redirect(url_for('login'))

    user = User.query.get(session['user_id'])

    if request.method == 'POST':
        new_username = request.form['username']
        new_password = request.form['password']
        user.username = new_username
        skey=Fernet.generate_key()
        sskey=Fernet(skey)
        user.key=skey
        user.password = sskey.encrypt(new_password.encode("utf8"))
        try:
            db.session.commit()
            flash('Profile updated successfully!', 'success')
        except IntegrityError:
            db.session.rollback()
            flash('Username already exists. Please choose another one.', 'danger')

    return render_template('profile.html', user=user)


# Route to delete the user account
@app.route('/delete_account', methods=['POST'])
def delete_account():
    if 'user_id' in session:
        user = User.query.get(session['user_id'])

        # Удаление всех песен, загруженных пользователем
        songs = Song.query.filter_by(user_id=user.id).all()
        for song in songs:
            # Удаление файла с сервера
            if os.path.exists(song.file_path):
                os.remove(song.file_path)
            # Удаление записи о песне из базы данных
            db.session.delete(song)

        # Удаление аккаунта пользователя
        db.session.delete(user)
        db.session.commit()

        # Очистка сессии
        session.pop('user_id', None)
        flash('Your account and all uploaded songs have been deleted.', 'success')
        return redirect(url_for('main'))
    else:
        flash('You need to log in first.', 'danger')
        return redirect(url_for('login'))


@app.route('/genres')
def genres():
    if 'user_id' not in session:
        return redirect(url_for('login'))
    return render_template('genres.html')

@app.route('/hip_hop')
def hip_hop():
    # Get all songs with the genre "Hip hop"
    songs = Song.query.filter_by(genre="Hip hop").all()
    return render_template('genre_page.html', genre="Hip hop", songs=songs)

@app.route('/heavy_metal')
def heavy_metal():
    # Get all songs with the genre "Heavy metal"
    songs = Song.query.filter_by(genre="Heavy metal").all()
    return render_template('genre_page.html', genre="Heavy metal", songs=songs)

@app.route('/rock_n_roll')
def rock_n_roll():
    # Get all songs with the genre "Rock n roll"
    songs = Song.query.filter_by(genre="Rock n roll").all()
    return render_template('genre_page.html', genre="Rock n roll", songs=songs)

@app.route('/jazz')
def jazz():
    # Get all songs with the genre "Jazz"
    songs = Song.query.filter_by(genre="Jazz").all()
    return render_template('genre_page.html', genre="Jazz", songs=songs)

@app.route('/rap')
def rap():
    # Get all songs with the genre "Rap"
    songs = Song.query.filter_by(genre="Rap").all()
    return render_template('genre_page.html', genre="Rap", songs=songs)

@app.route('/pop')
def pop():
    # Get all songs with the genre "Pop"
    songs = Song.query.filter_by(genre="Pop").all()
    return render_template('genre_page.html', genre="Pop", songs=songs)

@app.route('/classic')
def classic():
    # Get all songs with the genre "Classic"
    songs = Song.query.filter_by(genre="Classic").all()
    return render_template('genre_page.html', genre="Classic", songs=songs)

@app.route('/remix')
def remix():
    # Get all songs with the genre "Remix"
    songs = Song.query.filter_by(genre="Remix").all()
    return render_template('genre_page.html', genre="Remix", songs=songs)


@app.route('/dashboard')
def dashboard():
    if 'user_id' not in session:
        return redirect(url_for('login'))

    user = User.query.get(session['user_id'])
    songs = Song.query.all()  # Displaying all songs that in db to all users

    return render_template('dashboard.html', user=user, songs=songs)


@app.route('/delete_song/<int:song_id>')
def delete_song(song_id):
    if 'user_id' not in session:
        return redirect(url_for('login'))

    song = Song.query.get(song_id)
    user = User.query.get(session['user_id'])

    # Only the user that uploaded the song can delete it
    if song and song.user_id == user.id:
        file_path = song.file_path
        db.session.delete(song)
        db.session.commit()

        # Remove the file from the filesystem
        if os.path.exists(file_path):
            os.remove(file_path)

        flash('Song deleted successfully!', 'success')
    else:
        flash('You do not have permission to delete this song.', 'danger')

    return redirect(url_for('artist_page'))


@app.route('/register_artist', methods=['GET', 'POST'])
def register_artist():
    if 'user_id' in session:
        user = User.query.get(session['user_id'])

        # Если метод POST, обрабатываем отправку формы
        if request.method == 'POST':
            artist_name = request.form.get('artist_name') # Получаем данные об имени и фамилии пользователя
            artist_surname = request.form.get('artist_surname')

            user.artist_name = artist_name
            user.artist_surname = artist_surname
            user.is_artist = True  # Помечаем юзера как исполнителя
            db.session.commit()

            return redirect(url_for('artist_page'))

        # Если метод ГЕТ, просто отобразим страницу регистрации артиста
        return render_template('register_artist.html')

    return redirect(url_for('login'))

@app.route('/artist_page')
def artist_page():
    if 'user_id' not in session:
        return redirect(url_for('login'))

    user = User.query.get(session['user_id'])

    # Check if the user is an artist
    if not user.is_artist:
        return redirect(url_for('register_artist'))

    songs = Song.query.filter_by(user_id=user.id).all() # Getting all songs of current user
    return render_template('artist_page.html', user=user, songs=songs)

@app.route('/check_artist_status')
def check_artist_status():
    if 'user_id' not in session:
        return redirect(url_for('login'))

    user = User.query.get(session['user_id'])
    if user.is_artist:
        # Redirect to artist page if already registered as artist
        return redirect(url_for('artist_page'))
    else:
        # Redirect to artist registration page if not registered
        return redirect(url_for('register_artist'))

@app.route('/edit_song_title/<int:song_id>', methods=['POST'])
def edit_song_title(song_id):
    if 'user_id' not in session:
        return redirect(url_for('login'))

    # Получаем новую информацию
    new_title = request.form.get('new_title')

    # Ищем песню в базе данных
    song = Song.query.get(song_id)

    if song and song.user_id == session['user_id']:  # Проверяем, что песня принадлежит текущему пользователю
        song.title = new_title  # Обновляем название
        db.session.commit()
        flash('Song title updated successfully!', 'success')
    else:
        flash('You do not have permission to edit this song.', 'danger')

    return redirect(url_for('artist_page'))


if __name__ == '__main__':
    app.run(debug=True)
