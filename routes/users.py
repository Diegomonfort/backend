from flask import Blueprint, jsonify
from db import get_db_connection 

users_bp = Blueprint('users', __name__)

# Endpoint to get the entire users list
@users_bp.route('/users', methods=['GET'])
def list_users():

    try:
        conn = get_db_connection()
        cursor = conn.cursor()

        # Get all users
        cursor.execute("SELECT id, name FROM users;")
        users = cursor.fetchall()
        
        cursor.close()
        conn.close()
        
        # Make the response json
        users_list = [{"id": row[0], "name": row[1]} for row in users]

        return jsonify(users_list)
    except Exception as e:
        return jsonify({"error": str(e)}), 500



