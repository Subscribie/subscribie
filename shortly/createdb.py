import sqlite3

con = sqlite3.connect('karma.db')
cur = con.cursor()
cur.execute('''CREATE TABLE lookups (sid text, buildingnumber text, PostCode text)''')
cur.execute('''CREATE TABLE person (sid text , given_name text, family_name text, address_line1 text, city text, postal_code text, email text, mobile text)''')
con.commit()
