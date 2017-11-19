import sqlite3

con = sqlite3.connect('karma.db')
cur = con.cursor()
cur.execute('''CREATE TABLE lookups (buildingnumber text, PostCode text, sid text)''')
con.commit()
