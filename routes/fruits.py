from flask import Blueprint, jsonify
from db import get_db_connection

fruits_bp = Blueprint('fruits', __name__)




@fruits_bp.route('/fruits', methods=['GET'])
def get_fruits():

    """Endpoint to get all the fruits"""

    try:
        conn = get_db_connection()
        cursor = conn.cursor()

        cursor.execute("SELECT id, name, family, \"order\", genus, nutritions FROM fruits;")
        fruits = cursor.fetchall()

        # Format the json list
        fruits_list = []
        for fruit in fruits:
            fruit_dict = {
                "id": fruit[0],
                "name": fruit[1],
                "family": fruit[2],
                "order": fruit[3],
                "genus": fruit[4],
                "nutritions": fruit[5]
            }
            fruits_list.append(fruit_dict)

        cursor.close()
        conn.close()

        return jsonify(fruits_list), 200 

    except Exception as e:
        return jsonify({"error": str(e)}), 500
