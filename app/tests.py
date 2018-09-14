import sqlite3



def find_parent(person_id):
        with sqlite3.connect("static/user.db") as db:
            cursor = db.cursor()
            person_id = int(person_id)
            cursor.execute('SELECT * FROM dzieci WHERE person_id = ?', (person_id,))
            print(cursor.fetchall())
            return


find_parent(85011118272)