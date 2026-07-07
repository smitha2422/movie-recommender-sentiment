# import pickle
# import sqlite3
# import pandas as pd

# print("1. Reading your local movies_df.pkl dataset...")
# try:
#    movies_df = pickle.load(open("models/movies_df.pkl", "rb"))
# except FileNotFoundError:
#     print("❌ Error: Could not find movies_df.pkl in this folder. Make sure it's here!")
#     exit()

# print("2. Connecting to your empty movies.db file...")
# conn = sqlite3.connect("movies.db")

# print("3. Injecting movie rows into a new 'movies' table...")
# # This reads your dataframe properties and populates the sql rows dynamically
# movies_df.to_sql("movies", conn, if_exists="replace", index=False)

# print("4. Appending the users security authentication table...")
# cursor = conn.cursor()
# cursor.execute("""
# CREATE TABLE IF NOT EXISTS users (
#     id INTEGER PRIMARY KEY AUTOINCREMENT,
#     username TEXT UNIQUE NOT NULL,
#     password_hash TEXT NOT NULL
# );
# """)

# conn.commit()
# conn.close()
# print("🎉 Success! Your movies.db is no longer empty. It is fully loaded with movie entries and auth tables!")

import sqlite3
import os

db_path = 'movies.db'

# Optional: Safe fallback to delete the bad file programmatically if it still exists
if os.path.exists(db_path) and os.path.getsize(db_path) == 0:
    os.remove(db_path)

# This automatically creates a fresh, valid movies.db file
conn = sqlite3.connect(db_path)
cursor = conn.cursor()

print("Creating tables...")

# 1. Create users table
cursor.execute('''
    CREATE TABLE IF NOT EXISTS users (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        username TEXT UNIQUE NOT NULL,
        password TEXT NOT NULL
    )
''')

# 2. Create movies table (so your recommender has its table ready too!)
cursor.execute('''
    CREATE TABLE IF NOT EXISTS movies (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        title TEXT NOT NULL,
        genres TEXT
    )
''')

conn.commit()
conn.close()
print("Database initialized successfully!")