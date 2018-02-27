import sqlite3
import datetime

con = sqlite3.connect('data.db')
cur = con.cursor()
cur.execute('''CREATE TABLE lookups (sid text, ts timestamp , buildingnumber text, streetname text, locality text, administrative_area_level_1 text, country text, PostCode text)''')
cur.execute('''CREATE TABLE person (sid text , ts timestamp, given_name text, family_name text, address_line1 text, city text, postal_code text, email text, mobile text, wants text, phoneline_installed text, phoneline_CLI text, hasInstantPaid boolean)''')
cur.execute('''CREATE TABLE mandates(sid text, ts timestamp , mandate text, customer text, flow text)''')
cur.execute('''CREATE TABLE instantPayments(sid text, ts timestamp , description text, amount int)''')
con.commit()
