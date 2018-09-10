import sqlite3
import hashlib

with sqlite3.connect("static/user.db") as db:
    cursor = db.cursor()

cursor.execute('''
    CREATE TABLE IF NOT EXISTS Users(
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    grupa TEXT NOT NULL,
    username TEXT NOT NULL,
    password TEXT NOT NULL,
    email TEXT NOT NULL)
''')

cursor.execute('''
                    CREATE TABLE IF NOT EXISTS dzieci(
                    person_id TEXT NOT NULL,
                    name TEXT NOT NULL,
                    surname TEXT NOT NULL,
                    birth TEXT NOT NULL ,
                    grupa TEXT NOT NULL)
                ''')

def hash_passwd(hashed_password):
    hash_pass = hashlib.sha3_512(hashed_password.encode()).hexdigest()
    return hash_pass

def create_admin():

    grupa = input('Dodaj grupe użytkowników (admin, nauczyciel, rodzic)" ')
    username = input('Dodaj Uzytkownika: ')
    password = hash_passwd(input('Podaj hasło: '))
    email = input('podaj email:')

    cursor.execute(
        'INSERT INTO users (grupa, username, password, email) VALUES (?, ?, ?, ?)',
        (
            grupa, username, password, email
        )
    )
    db.commit()

    cursor.execute("SELECT * FROM users")
    print(cursor.fetchall())
    return grupa, username,password,email

create_admin()