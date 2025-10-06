import mysql.connector

config = {
    "host": "localhost",
    "user": "root",
    "password": "BYR@qjn517120",
    "database": "youtime_test",
}

conn = mysql.connector.connect(**config)

cursor = conn.cursor()
cursor.execute("SELECT username, email FROM users")
for row in cursor.fetchall():
    print(row)

cursor.close()
conn.close()
