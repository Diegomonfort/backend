from flask import Blueprint, request, jsonify
from werkzeug.security import generate_password_hash, check_password_hash
from db import get_db_connection

auth_bp = Blueprint('auth', __name__)




@auth_bp.route('/register', methods=['POST'])
def register():
    try:

        data = request.get_json()
        if not data:
            return jsonify({"error": "Invalid or empty request body"}), 400

        name = data.get('name')
        password = data.get('password')


        if not name or not password:
            return jsonify({"error": "Name and password are required"}), 400

        conn = get_db_connection()
        cursor = conn.cursor()

        # Check if the user already exists
        cursor.execute("SELECT id FROM users WHERE name = %s;", (name,))
        existing_user = cursor.fetchone()

        if existing_user:
            return jsonify({"error": "Username already in use"}), 400

        # Hash the password and insert the new user
        hashed_password = generate_password_hash(password)
        cursor.execute(
            "INSERT INTO users (name, password) VALUES (%s, %s) RETURNING id;",
            (name, hashed_password)
        )
        user_id = cursor.fetchone()[0]

        conn.commit()
        cursor.close()
        conn.close()

        return jsonify({"id": user_id, "name": name}), 201

    except Exception as e:
        return jsonify({"error": str(e)}), 500
    




@auth_bp.route('/login', methods=['POST'])
def login():
    data = request.json
    name = data.get('name')
    password = data.get('password')

    if not name or not password:
        return jsonify({"error": "Name and password are required"}), 400

    try:
        conn = get_db_connection()
        cursor = conn.cursor()

        # Retrieve the user by name and check credentials
        cursor.execute("SELECT id, password FROM users WHERE name = %s;", (name,))
        user = cursor.fetchone()

        if not user or not check_password_hash(user[1], password):
            return jsonify({"error": "Invalid credentials"}), 401

        return jsonify({"message": f"Welcome {name}!", "id": user[0]}), 200
    
    except Exception as e:
        return jsonify({"error": str(e)}), 500
    finally:
        cursor.close()
        conn.close()
