from flask import Flask, render_template, request, redirect, url_for
import sqlite3
from werkzeug.security import generate_password_hash, check_password_hash

app = Flask(__name__)

# Create SQLite database and tables
conn = sqlite3.connect('social_media.db')
cursor = conn.cursor()

# Create 'users' table
cursor.execute('''
    CREATE TABLE IF NOT EXISTS users (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        username TEXT UNIQUE NOT NULL,
        password TEXT NOT NULL
    )
''')

# Create 'posts' table
cursor.execute('''
    CREATE TABLE IF NOT EXISTS posts (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER NOT NULL,
        content TEXT NOT NULL,
        timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (user_id) REFERENCES users (id)
    )
''')

conn.commit()
conn.close()

# Route for home page
@app.route('/')
def home():
    conn = sqlite3.connect('social_media.db')
    cursor = conn.cursor()

    # Fetch all posts with username
    cursor.execute('''
        SELECT posts.id, content, username, timestamp
        FROM posts
        JOIN users ON posts.user_id = users.id
        ORDER BY timestamp DESC
    ''')
    posts = cursor.fetchall()

    conn.close()
    return render_template('home.html', posts=posts)

# Route for creating a new post
@app.route('/create_post', methods=['POST'])
def create_post():
    if 'username' in request.cookies:
        content = request.form['content']
        username = request.cookies['username']

        conn = sqlite3.connect('social_media.db')
        cursor = conn.cursor()

        # Get user_id based on the username
        cursor.execute('SELECT id FROM users WHERE username = ?', (username,))
        user_id = cursor.fetchone()[0]

        # Insert the new post
        cursor.execute('INSERT INTO posts (user_id, content) VALUES (?, ?)', (user_id, content))
        conn.commit()
        conn.close()

    return redirect(url_for('home'))

# Route for user registration
@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        conn = sqlite3.connect('social_media.db')
        cursor = conn.cursor()

        # Hash the password before storing
        hashed_password = generate_password_hash(password, method='sha256')

        # Insert new user into 'users' table
        cursor.execute('INSERT INTO users (username, password) VALUES (?, ?)', (username, hashed_password))
        conn.commit()
        conn.close()

        return redirect(url_for('login'))

    return render_template('register.html')

# Route for user login
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        conn = sqlite3.connect('social_media.db')
        cursor = conn.cursor()

        # Get user details based on the username
        cursor.execute('SELECT id, username, password FROM users WHERE username = ?', (username,))
        user = cursor.fetchone()

        conn.close()

        if user and check_password_hash(user[2], password):
            response = redirect(url_for('home'))
            response.set_cookie('username', user[1])
            return response

    return render_template('login.html')

# Route for user logout
@app.route('/logout')
def logout():
    response = redirect(url_for('home'))
    response.delete_cookie('username')
    return response

if __name__ == '__main__':
    app.run(debug=True)
