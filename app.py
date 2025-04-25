from flask import Flask, request, jsonify
from flask_cors import CORS
import pyodbc
from datetime import date

app = Flask(__name__)
CORS(app)

# Replace with your actual connection string
conn_str = (
    "Driver={ODBC Driver 17 for SQL Server};"
    "Server=localhost;"
    "Database=ShoppingDB;"
    "Trusted_Connection=yes;"
)

def get_connection():
    return pyodbc.connect(conn_str)


# 🔹 GET all items
@app.route('/items', methods=['GET'])
def get_items():
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM ShoppingItems")
    items = [dict(zip([column[0] for column in cursor.description], row)) for row in cursor.fetchall()]
    conn.close()
    return jsonify(items)


# 🔹 POST create a new item
@app.route('/items', methods=['POST'])
def add_item():
    data = request.json
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("""
        INSERT INTO ShoppingItems (name, quantity, unit, price, boughtDate)
        VALUES (?, ?, ?, ?, ?)
    """, data['name'], data['quantity'], data['unit'], data['price'], None)
    conn.commit()
    conn.close()
    return jsonify({"message": "Item added"}), 201


# 🔹 PUT update item (by id)
@app.route('/items/<int:item_id>', methods=['PUT'])
def update_item(item_id):
    data = request.json
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("""
        UPDATE ShoppingItems 
        SET name = ?, quantity = ?, unit = ?, price = ?
        WHERE id = ?
    """, data['name'], data['quantity'], data['unit'], data['price'], item_id)
    conn.commit()
    conn.close()
    return jsonify({"message": "Item updated"})


# 🔹 PUT mark as bought (current date)
@app.route('/items/<int:item_id>/bought', methods=['PUT'])
def mark_bought(item_id):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("UPDATE ShoppingItems SET boughtDate = ? WHERE id = ?", date.today(), item_id)
    conn.commit()
    conn.close()
    return jsonify({"message": "Marked as bought"})


# 🔹 DELETE an item
@app.route('/items/<int:item_id>', methods=['DELETE'])
def delete_item(item_id):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM ShoppingItems WHERE id = ?", item_id)
    conn.commit()
    conn.close()
    return jsonify({"message": "Item deleted"})


if __name__ == '__main__':
    app.run(debug=True)
