# -*- coding: utf-8 -*- 

from flask import Flask
app = Flask(__name__)
from werkzeug.utils import secure_filename
from flask import render_template, request, redirect, url_for, flash, session
import sqlite3
import os
from function import *
from datetime import timedelta
app.secret_key = os.urandom(24)

app.permanent_session_lifetime = timedelta(minutes=10)


@app.route('/')
def index():
    if 'username' in session:
        username = session['username']
        data = show_posted()
        return render_template('show_posts.html', the_title="BAZA PRZEDSZKOLAKA", info=username,
                               grupa=check_grupa(username), data=data)
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
    return redirect(url_for('login'))


@app.route('/login', methods=['GET', 'POST'])
def login():
    error = None
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        completion = validate(username, password)
        if completion is False:
            error = 'Niepoprawny login lub haslo'
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
    return redirect(url_for('login'))


@app.route('/register', methods=['GET', 'POST'])
def register():
    if 'username' in session:
        username = session['username']
        if check_grupa(username) == check_grupa('admin'):
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

@app.route('/admin/')
def admin():
    if 'username' in session:
        username = session['username']
        if check_grupa(username) == 'admin':
            return render_template('admin.html', grupa=check_grupa(username), info=username)

    return redirect(url_for('login')), flash('Nie jestes zalogowany!!  Prosze sie wczesniej zalogować')


@app.route('/search_db/', methods=['POST', 'GET'])
def search_db():
    if 'username' in session:
        username = session['username']
        if check_grupa(username) == 'admin':
            if request.method == 'POST':
                pesel = request.form['person_id']
                data = find_child(pesel)
                return render_template('search_db.html', grupa=check_grupa(username), info=username, data=data[::])
        return render_template('search_db.html', grupa=check_grupa(username), info=username)
    return redirect(url_for('login')), flash('Nie jestes zalogowany!!  Prosze sie wczesniej zalogować')



@app.route('/upload', methods=['GET', 'POST'])
def upload_file():
    if 'username' in session:
        username = session['username']
        if check_grupa(username) == 'admin':
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
        session.pop('username', None)
        session.clear()
        return redirect(url_for('login')), flash('Nie jestes zalogowany!!  Prosze sie wczesniej zalogować')
    return redirect(url_for('login')), flash('Nie jestes zalogowany!!  Prosze sie wczesniej zalogować')


@app.route('/check_users', methods=['POST', 'GET'])
def check_user():
    if 'username' in session:
        username = session['username']
        if check_grupa(username) == check_grupa('admin'):
            data = check_username()
            return render_template('check_users.html', grupa=check_grupa(username), info=username, data=data)
        session.pop('username', None)
        session.clear()
        return redirect(url_for('login')), flash('Nie jestes zalogowany!!  Prosze sie wczesniej zalogować')
    return redirect(url_for('login')), flash('Nie jestes zalogowany!!  Prosze sie wczesniej zalogować')


@app.route('/add_post', methods=['POST', 'GET'])
def add_post():
    if 'username' in session:
        username = session['username']
        if check_grupa(username) == 'nauczyciel' or check_grupa(username) == 'admin':
            if request.method == 'POST':
                with sqlite3.connect("static/user.db") as db:
                    cursor = db.cursor()
                cursor.execute(
                    'INSERT INTO posts (email, title, contents) VALUES (?, ?, ?)',
                    (
                        request.form.get('email', type=str),
                        request.form.get('title', type=str),
                        request.form.get('contents', type=str)
                    )
                )
                db.commit()
                flash('Dodano ogloszenie pomyslnie.')
            return render_template('/add_post.html', grupa=check_grupa(username), info=username)
        session.pop('username', None)
        session.clear()
        return redirect(url_for('login')), flash('Nie jestes zalogowany!!  Prosze sie wczesniej zalogować')
    return redirect(url_for('login'))

@app.route('/show_posts')
def show_posts():
        data = show_posted()
        return render_template('show_posts.html', data=data)

