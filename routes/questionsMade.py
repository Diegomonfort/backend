from flask import Flask, jsonify, Blueprint
from db import get_db_connection

app = Flask(__name__)

fruit_comparisons_bp = Blueprint('fruit_comparisons', __name__)

# Endpoint to get all the questions from a session using the sesion id
@fruit_comparisons_bp.route('/get-questions/<session_id>', methods=['GET'])
def get_questions(session_id):
    try:
        conn = get_db_connection()
        cursor = conn.cursor()

        # From DB, get the questions using the session_id property
        cursor.execute("""
            SELECT id, fruit1_id, fruit2_id, attribute, result, question_id, session_id
            FROM fruit_comparisons
            WHERE session_id = %s
        """, (session_id,))

        questions = cursor.fetchall()

        # Make the list for the response
        formatted_questions = [
            {
                'id': row[0],
                'fruit1_id': row[1],
                'fruit2_id': row[2],
                'attribute': row[3],
                'result': row[4],
                'question_id': row[5],
                'session_id': row[6]
            }
            for row in questions
        ]

        return jsonify({'questions': formatted_questions}), 200

    except Exception as e:
        print(f"Error: {e}")
        return jsonify({'error': 'Error al obtener las preguntas'}), 500

    finally:
        cursor.close()
        conn.close()

