import hashlib
import sqlite3
from flask import sessions,session



ALLOWED_EXTENSIONS = {'txt', 'pdf', 'jpg', 'png', 'jpeg', 'gif', 'doc', 'rar'}


def db_connect():
    with sqlite3.connect("static/user.db") as db:
        cursor = db.cursor()
        cursor.execute('SELECT * FROM users')
        data = cursor.fetchall()
        return data

def db_connect_post():
    with sqlite3.connect("static/user.db") as db:
        cursor = db.cursor()
        cursor.execute('SELECT * FROM posts ORDER BY time DESC')
        data = cursor.fetchall()
        return data

def check_username():
    find = db_connect()
    return find


def find_child(pesel):
    with sqlite3.connect("static/user.db") as db:
        cursor = db.cursor()
        cursor.execute('SELECT * FROM dzieci WHERE person_id = ?', (pesel,))
        data = cursor.fetchall()
        return data


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

def show_posted():
    find = db_connect_post()
    return find

def username_sesion():
    username = session['username']
    return username

