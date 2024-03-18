import sqlite3

def connect():
    conn = sqlite3.connect('db.db')
    cursor = conn.cursor()
    return conn, cursor

def create_table():
    conn, cursor = connect()
    cursor.execute('''CREATE TABLE IF NOT EXISTS email (
                      id INTEGER PRIMARY KEY,
                      user_id TEXT NOT NULL,
                      email TEXT NOT NULL,
                      phone TEXT)''')  # Added phone column
    conn.commit()
    conn.close()

def insert_email(user_id, email):
    conn, cursor = connect()
    cursor.execute('INSERT INTO email (user_id, email) VALUES (?, ?)', (user_id, email))
    conn.commit()
    conn.close()

def insert_phone(user_id, phone):
    conn, cursor = connect()
    cursor.execute('UPDATE email SET phone = ? WHERE user_id = ?', (phone, user_id))
    conn.commit()
    conn.close()

def view_emails():
    conn, cursor = connect()
    cursor.execute('SELECT * FROM email')
    rows = cursor.fetchall()
    conn.close()
    return rows

def view_username_with_email(email):
    conn, cursor = connect()
    cursor.execute('SELECT user_id FROM email where email = ?', (email,))
    rows = cursor.fetchall()
    conn.close()
    return rows


def view_emails_with_username(user_id):
    conn, cursor = connect()
    cursor.execute('SELECT email FROM email where user_id = ?', (str(user_id),))
    rows = cursor.fetchall()
    conn.close()
    return rows

# Uncomment the line below to create the table when this script is executed.
create_table()
