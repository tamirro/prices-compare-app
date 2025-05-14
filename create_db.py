import sqlite3
import pandas as pd

# Connect to SQLite database (creates prices.db if it doesn't exist)
conn = sqlite3.connect('prices.db')
cursor = conn.cursor()

# Create tables for your_store and competitor_store
cursor.execute('''
    CREATE TABLE IF NOT EXISTS your_store (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        product_name TEXT NOT NULL,
        price REAL NOT NULL,
        category TEXT
    )
''')

cursor.execute('''
    CREATE TABLE IF NOT EXISTS competitor_store (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        product_name TEXT NOT NULL,
        price REAL NOT NULL,
        category TEXT
    )
''')

# Load CSVs
your_store_df = pd.read_csv('your_store.csv')
competitor_store_df = pd.read_csv('competitor_store.csv')

# Insert data into tables
your_store_df.to_sql('your_store', conn, if_exists='replace', index=False)
competitor_store_df.to_sql('competitor_store', conn, if_exists='replace', index=False)

# Commit changes and close
conn.commit()
conn.close()

print("Database created successfully with your_store and competitor_store tables.")