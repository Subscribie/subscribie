import sqlite3

from datetime import datetime

date_format = "%Y-%m-%d %H:%M:%S.%f"
# Connect to the SQLite database
conn = sqlite3.connect("data.db")

# Create a cursor object using the cursor() method
cursor = conn.cursor()

# Selecting the 'stripe_invoice_raw_json' column from the 'stripe_invoice' table
query = "SELECT id, created_at, stripe_invoice_raw_json FROM stripe_invoice"

# Executing the query
cursor.execute(query)

# Fetch all rows from the executed query
rows = cursor.fetchall()

count = 0
errors = 0
# Looping over each row and printing the 'stripe_invoice_raw_json' column
for row in rows:
    count += 1
    print(row[1])
    datetime.strptime(row[1], date_format)
    try:
        if row[0] == "example":
            update_query = "UPDATE table_name SET column_name = ? WHERE id = ?"
            cursor.execute(
                update_query,
                ("foo", "bar"),
            )
            conn.commit()
    except ValueError as e:
        print(e)
        errors += 1

# Close the connection
conn.close()

print(f"Total rows: {count}")
print(f"Total errors: {errors}")
