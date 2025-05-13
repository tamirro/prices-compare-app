import sqlite3
import pandas as pd

conn = sqlite3.connect('prices.db')
cursor = conn.cursor()

# Example: Update price for a product
cursor.execute("UPDATE your_store SET price = ? WHERE product_name = ?", (5.99, "Apple"))
conn.commit()

# Example: Load new CSV
new_data = pd.read_csv('new_your_store.csv')
new_data.to_sql('your_store', conn, if_exists='replace', index=False)

conn.close()
print("Database updated.")