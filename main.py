from flask import Flask, render_template, request, redirect, url_for, flash, session
from werkzeug.utils import secure_filename
from datetime import timedelta
import sqlite3
import os
import hashlib


ALLOWED_EXTENSIONS = {'txt', 'pdf', 'jpg', 'png', 'jpeg', 'gif', 'doc', 'rar'}

app = Flask(__name__)
app.secret_key = os.urandom(24)

app.permanent_session_lifetime = timedelta(minutes=10)


def db_connect():
    with sqlite3.connect("static/user.db") as db:
        cursor = db.cursor()
        cursor.execute('SELECT * FROM users, dzieci')
        data = cursor.fetchall()
        return data

def check_username():
    find = db_connect()
    return find


def find_child(pesel):
        data = db_connect()
        for rows in data[:]:
            pesel = rows[5]
            name = rows[6]
            surname = rows[7]
            date_of_birth = rows[8]
            group = rows[9]
            result = "PESEL :" + " " + pesel, "IMIĘ :" + " " + name, "NAZWISKO :" + " " + surname, \
                     "DATA URODZENIA :" + " " + date_of_birth, "GRUPA PRZEDSZKOLNA :" + " " + group
            return result


def check_grupa(username):
    with sqlite3.connect("static/user.db") as db:
        cur = db.cursor()
    cur.execute("SELECT * FROM users")
    rows = cur.fetchall()
    for row in rows:
        db_grupa = row[1]
        db_user = row[2]
        if db_grupa == db_grupa and db_user == username:
            return db_grupa


def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


def hash_passwd(hashed_password):
    hash_pass = hashlib.sha224(hashed_password.encode()).hexdigest()
    return hash_pass


def check_password(hashed_password, user_password):
    return hashed_password == hashlib.sha224(user_password.encode()).hexdigest()


def validate(username, password):
    con = sqlite3.connect('static/user.db')
    completion = False
    with con:
                cur = con.cursor()
                cur.execute("SELECT * FROM Users")
                rows = cur.fetchall()
                for row in rows:
                    db_user = row[2]
                    db_pass = row[3]
                    if db_user == username:
                        completion = check_password(db_pass, password)
    return completion


@app.route('/')
def index():
    if 'username' in session:
        username = session['username']
        return render_template('base.html', the_title="BAZA PRZEDSZKOLAKA", info=username, grupa=check_grupa(username))
    else:
        return render_template('base.html', the_title="BAZA PRZEDSZKOLAKA")


@app.route('/profil')
def profil():
    if 'username' in session:
        username = session['username']
        with sqlite3.connect("static/user.db") as db:
            cursor = db.cursor()
            cursor.execute('SELECT person_id, name, surname, birth, grupa FROM dzieci')
            data = cursor.fetchall()
        db.commit()

        return render_template("profil.html", data=data, the_title='BAZA PRZEDSZKOLAKA', info=username,
                               grupa=check_grupa(username))


@app.route('/login', methods=['GET', 'POST'])
def login():
    error = None
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        completion = validate(username, password)
        if completion is False:
            error = 'Niepoprawny login lub hasło'
        else:
            session['username'] = request.form['username']
            username = session['username']
            if check_grupa(username) == 'admin':
                info = "Witaj" + " " + check_grupa(username)+"ie"
                flash(info)
            if check_grupa(username) == 'nauczyciel':
                info = "Witaj" + " " + check_grupa(username) + "u"
                flash(info)
            if check_grupa(username) == 'rodzic':
                info = "Witaj" + " " + check_grupa(username) + "u"
                flash(info)
            return render_template('base.html', error=error, info=username, grupa=check_grupa(username))
    return render_template('login.html', error=error)


@app.route("/logout")
def logout():
    session.pop('username', None)
    session.clear()
    return redirect(url_for('index'))


@app.route('/child', methods=['GET', 'POST'])
def child():
    if 'username' in session:
        username = session['username']
        if request.method == 'POST':
            with sqlite3.connect("static/user.db") as db:
                cursor = db.cursor()

            cursor.execute(
                'INSERT INTO dzieci (person_id, name, surname, birth, grupa) VALUES (?, ?, ?, ?, ?)',
                (
                    request.form.get('person_id', type=str),
                    request.form.get('name', type=str),
                    request.form.get('surname', type=str),
                    request.form.get('birth', type=str),
                    request.form.get('grupa', type=str)
                )
            )
            db.commit()
            return redirect(url_for('child'))
        return render_template("child.html", the_title='BAZA PRZEDSZKOLAKA', info=username, grupa=check_grupa(username))


@app.route('/register', methods=['GET', 'POST'])
def register():
    if session['username'] == 'admin':
        username = session['username']
        if request.method == 'POST':
            with sqlite3.connect("static/user.db") as db:
                cursor = db.cursor()

            cursor.execute(
                'INSERT INTO users (grupa, username, password, email) VALUES (?, ?, ?, ?)',
                (
                    request.form.get('grupa', type=str),
                    request.form.get('username', type=str),
                    hash_passwd(request.form.get('password', type=str)),
                    request.form.get('email', type=str))
            )
            db.commit()
            return redirect(url_for('register'))
        return render_template("register.html", the_title='BAZA PRZEDSZKOLAKA', info=username,
                               grupa=check_grupa(username))


@app.route('/admin')
def admin():
    username = session['username']
    if check_grupa(username) == check_grupa('admin'):
        return render_template('admin.html', grupa=check_grupa(username), info=username)
    else:
        session.pop('username', None)
        session.clear()
        return redirect(url_for('login')), flash('Nie jestes zalogowany!!  Prosze sie wczesniej zalogować')


@app.route('/search_db', methods=['POST', 'GET'])
def search_db():
    username = session['username']
    if check_grupa(username) == check_grupa('admin'):
        if request.method == 'POST':
            pesel = request.form['person_id']
            data = find_child(pesel)
            return render_template('search_db.html', grupa=check_grupa(username), info=username, data=data[::])
        return render_template('search_db.html', grupa=check_grupa(username), info=username)
    else:
        session.pop('username', None)
        session.clear()
        return redirect(url_for('login')), flash('Nie jestes zalogowany!!  Prosze sie wczesniej zalogować')


@app.route('/upload', methods=['GET', 'POST'])
def upload_file():
    username = session['username']
    if check_grupa(username) == check_grupa('admin'):
        if request.method == 'POST':
            if 'file' not in request.files:
                flash('No file part')
                return redirect(request.url)
            file = request.files['file']
            if file.filename == '':
                flash('No selected file')
                return redirect(request.url)
            if file and allowed_file(file.filename):
                filename = secure_filename(file.filename)
                file.save(os.path.join('static/storage', filename))
                return redirect(url_for('index', filename=filename)), flash('Upload file successfull')
        return render_template('upload.html', info=username, grupa=check_grupa(username))


@app.route('/check_users', methods=['POST','GET'])
def check_user():
    if 'username' in session:
        username = session['username']
        data = check_username()
        return render_template('check_users.html', grupa=check_grupa(username), info=username, data=data)
    else:
        return render_template('check_users.html',)


if __name__ == "__main__":
    app.run(host='0.0.0.0', debug=True, port=8061)

#check_username()

print(check_username())
print(find_child(85011118272))