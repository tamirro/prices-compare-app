from flask import Flask, jsonify
import sqlite3
import pandas as pd

app = Flask(__name__)

@app.route('/data/<table_name>')
def get_data(table_name):
    conn = sqlite3.connect('prices.db')
    df = pd.read_sql_query(f"SELECT ItemCode, [Product Name], Price, Unit FROM {table_name}", conn)
    conn.close()
    return jsonify(df.to_dict(orient='records'))

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)