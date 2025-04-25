from flask import Flask, request, jsonify
from flask_cors import CORS
import pyodbc
from datetime import date, datetime

app = Flask(__name__)

# CORS setup to allow cross-origin requests
CORS(app)

# Database connection string (update as per your environment)
conn_str = (
    "Driver={ODBC Driver 17 for SQL Server};"
    "Server=DESKTOP-VF137E5;"  # Update the server name as needed
    "Database=ShoppingDB;"
    "Trusted_Connection=yes;"
)

# Function to establish database connection
def get_connection():
    return pyodbc.connect(conn_str)

# Home route
@app.route('/')
def home():
    return "Welcome to the Enhanced Shopping List App!"

# 🔹 GET all items from the database
@app.route('/items', methods=['GET'])
def get_items():
    try:
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM ShoppingItems")
        items = [dict(zip([column[0] for column in cursor.description], row)) for row in cursor.fetchall()]
        conn.close()
        return jsonify(items)
    except pyodbc.Error as e:
        return jsonify({"error": "Database error", "message": str(e)}), 500

# 🔹 POST create a new item in the database
@app.route('/items', methods=['POST'])
def add_item():
    data = request.json
    try:
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute("""
            INSERT INTO ShoppingItems (name, quantity, unit, price, boughtDate)
            VALUES (?, ?, ?, ?, ?)
        """, data['name'], data['quantity'], data['unit'], data['price'], None)
        conn.commit()
        conn.close()
        return jsonify({"message": "Item added"}), 201
    except pyodbc.Error as e:
        return jsonify({"error": "Database error", "message": str(e)}), 500

# 🔹 PUT update item by id
@app.route('/items/<int:item_id>', methods=['PUT'])
def update_item(item_id):
    data = request.json
    try:
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
    except pyodbc.Error as e:
        return jsonify({"error": "Database error", "message": str(e)}), 500

# 🔹 PUT mark an item as bought (by item_id)
@app.route('/items/<int:item_id>/bought', methods=['PUT'])
def mark_bought(item_id):
    try:
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute("UPDATE ShoppingItems SET boughtDate = ? WHERE id = ?", date.today(), item_id)
        conn.commit()
        conn.close()
        return jsonify({"message": "Marked as bought"})
    except pyodbc.Error as e:
        return jsonify({"error": "Database error", "message": str(e)}), 500

# 🔹 DELETE an item by id
@app.route('/items/<int:item_id>', methods=['DELETE'])
def delete_item(item_id):
    try:
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute("DELETE FROM ShoppingItems WHERE id = ?", item_id)
        conn.commit()
        conn.close()
        return jsonify({"message": "Item deleted"})
    except pyodbc.Error as e:
        return jsonify({"error": "Database error", "message": str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True)
