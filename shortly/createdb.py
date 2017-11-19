import sqlite3
import datetime

con = sqlite3.connect('karma.db')
cur = con.cursor()
cur.execute('''CREATE TABLE lookups (sid text, ts timestamp , buildingnumber text, PostCode text)''')
cur.execute('''CREATE TABLE person (sid text , ts timestamp, given_name text, family_name text, address_line1 text, city text, postal_code text, email text, mobile text)''')
con.commit()
