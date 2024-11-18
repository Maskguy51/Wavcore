Wavcore Flask Application Documentation
Overview
This document provides a detailed description of the backend functionality for the Wavcore application, built using the Flask framework. It includes routes for user management, song uploads, artist functionalities, and genre-specific features.

Configuration Settings
SECRET_KEY: "supersecretkey"
Used to manage Flask session security.
SQLALCHEMY_DATABASE_URI: 'sqlite:///database.db'
SQLite is used as the database backend for simplicity.
UPLOAD_FOLDER: 'static/uploads'
Directory where uploaded audio files are stored.
Database Initialization
python
Copy code
db.init_app(app)

with app.app_context():
    db.create_all()
Initializes the database schema within the application context.

Features and Routes
User Management
Login (/login):

Methods: GET, POST
Allows users to log in. Validates credentials and creates a session for the user.
Register (/register):

Methods: GET, POST
Handles new user registration and database entry creation.
Profile Management (/profile):

Methods: GET, POST
Enables users to update their profile details (username and password).
Logout (/logout):

Clears the session and redirects the user to the homepage.
Delete Account (/delete_account):

Methods: POST
Removes a user’s account and all associated data.
Song Management
Upload Song (/upload_song):

Methods: POST
Uploads an audio file with metadata (title, genre) and stores it in the database.
Delete Song (/delete_song/<int:song_id>):

Removes a song from both the database and the filesystem. Only accessible by the original uploader.
Artist Songs (/artist_songs/<int:artist_id>):

Displays all songs uploaded by a specific artist.
Add Song (/add_song):

Methods: POST
Adds a new song for the logged-in user.

Artist Management
Register Artist (/register_artist):

Methods: POST
Converts a user account to an artist account by collecting artist-specific details like name and surname.
Artist Page (/artist_page):

Displays the artist's personal dashboard, including their uploaded songs.
Check Artist Status (/check_artist_status):

Redirects users based on their artist registration status.
Genre-Specific Routes
Genres Overview (/genres):

Lists all available genres for users to explore.
Genre Pages:

/hip_hop, /heavy_metal, /rock_n_roll:
Displays songs filtered by their respective genres.

K. Aliakhmet
B. Arsen
A. Maxim

