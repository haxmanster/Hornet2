import sqlite3
#with sqlite3.connect("static/user.db") as db:
#        cursor = db.cursor()
#        t = '85011118272'
#        cursor.execute('SELECT * FROM dzieci  WHERE person_id = ?', t,)
#        data = cursor.fetchall()
#        for item in data:
#            person_id = item[0]
#            name = item[1]
#            surname = item[2]
#            birth = item[3]
#            group = item[4]
#            result = person_id,name,surname,birth,group
#            print(result)


def find_child(pesel):
    with sqlite3.connect("app/static/user.db") as db:
        cursor = db.cursor()
        pesel = int(pesel)
        cursor.execute ('SELECT * FROM dzieci WHERE person_id = ?', (pesel,))
        data = cursor.fetchall()
        return data


print(find_child('85011118272'))


