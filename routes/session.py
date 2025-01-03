from flask import Flask, jsonify, request, Blueprint
import uuid
from db import get_db_connection

app = Flask(__name__)

session_bp = Blueprint('start-game', __name__)

# Endpoint to create new session game
@session_bp.route('/start-game', methods=['POST'])
def start_game():
    try:

        user_id = request.json.get('user_id')

        if not user_id:
            return jsonify({'error': 'The user_id is necessary'}), 400

        # Create the uuid for the sessions
        session_id = str(uuid.uuid4())

        conn = get_db_connection()
        cursor = conn.cursor()

        # Insert new session on  the DB
        cursor.execute("""
            INSERT INTO sessions (id, user_id) 
            VALUES (%s, %s) 
            RETURNING id
        """, (session_id, user_id))

        session_id = cursor.fetchone()[0]
        conn.commit()

        return jsonify({'session_id': session_id}), 201

    except Exception as e:
        print(f"Error: {e}")
        return jsonify({'error': 'Error al iniciar el juego'}), 500

    finally:
        cursor.close()
        conn.close()





# Endpoint to get all the sessions from a selected user
@session_bp.route('/sessions', methods=['GET'])
def get_sessions():
    try:

        user_id = request.args.get('user_id')

        if not user_id:
            return jsonify({'error': 'El user_id es necesario'}), 400

        conn = get_db_connection()
        cursor = conn.cursor()

        # Get all the sessions of the user from the sessions Table
        cursor.execute("""
            SELECT id, user_id, started_at, score FROM sessions WHERE user_id = %s
        """, (user_id,))

        sessions = cursor.fetchall()

        if not sessions:
            return jsonify({'message': 'There are no sessions for this user'}), 404

        # make the json response whith the sessions
        session_list = [{'session_id': session[0], 'user_id': session[1], 'created_at': session[2], 'score': session[3]} for session in sessions]

        return jsonify({'sessions': session_list}), 200

    except Exception as e:
        print(f"Error: {e}")
        return jsonify({'error': 'Error al obtener las sesiones'}), 500

    finally:
        cursor.close()
        conn.close()





# Esdpoint to DELETE a session
@session_bp.route('/sessions/<session_id>', methods=['DELETE'])
def delete_session(session_id):
    try:

        conn = get_db_connection()
        cursor = conn.cursor()

        # Verify if the session exist
        cursor.execute("SELECT id FROM sessions WHERE id = %s", (session_id,))
        session = cursor.fetchone()

        if not session:
            return jsonify({'error': 'La sesión no existe'}), 404

        # Delete the session
        cursor.execute("DELETE FROM sessions WHERE id = %s", (session_id,))
        conn.commit()

        return jsonify({'message': f'Session {session_id} deleted succesfuly'}), 200

    except Exception as e:
        print(f"Error: {e}")
        return jsonify({'error': 'Error deleting the session'}), 500

    finally:
        cursor.close()
        conn.close()





# Endpoint to save the score of the current session
@session_bp.route('/save_score', methods=['POST'])
def save_score():
    try:

        data = request.json
        session_id = data.get('session_id') # session id
        score = data.get('score') # Score of the session played

        if not session_id or score is None:
            return jsonify({'error': 'session_id and score are necessary'}), 400

        conn = get_db_connection()
        cursor = conn.cursor()

        # UPDATE the score on the session Table
        cursor.execute("""
            UPDATE sessions
            SET score = %s
            WHERE id = %s
        """, (score, session_id))

        conn.commit()
        return jsonify({'message': 'Score updated succesfuly'}), 200

    except Exception as e:
        print(f"Error: {e}")
        return jsonify({'error': 'Error saving the score'}), 500

    finally:
        cursor.close()
        conn.close()






# Endpoint to get the top session socre of a user
@session_bp.route('/session-top', methods=['GET'])
def session_top():
    try:
 
        user_id = request.args.get('user_id')

        if not user_id:
            return jsonify({'error': 'user_id necessary'}), 400

        conn = get_db_connection()
        cursor = conn.cursor()

        # Get the higest score from a selected user
        cursor.execute("""
            SELECT MAX(score) AS highest_score
            FROM sessions
            WHERE user_id = %s
        """, (user_id,))
        result = cursor.fetchone()

        highest_score = result[0] if result[0] is not None else 0

        return jsonify({'highest_score': highest_score}), 200

    except Exception as e:
        print(f"Error: {e}")
        return jsonify({'error': 'Error geting the highest score'}), 500

    finally:
        cursor.close()
        conn.close()

if __name__ == '__main__':
    app.run(debug=True)