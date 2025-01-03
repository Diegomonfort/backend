from flask import Flask, jsonify, Blueprint
from db import get_db_connection

app = Flask(__name__)
leadboard_bp = Blueprint('leadboard', __name__)

@leadboard_bp.route('/leadboard', methods=['GET'])
def get_leadboard():
    try:
        conn = get_db_connection()
        cursor = conn.cursor()

        # Get the max scores from all users by descendant order
        query = '''
            SELECT user_id, MAX(score) AS max_score 
            FROM sessions 
            GROUP BY user_id 
            ORDER BY max_score DESC
        '''
        cursor.execute(query)

        results = cursor.fetchall()

        # Make the list for the response
        leadboard = []
        for idx, (user_id, score) in enumerate(results, start=1):
            leadboard.append({
                'position': idx,
                'user_id': user_id,
                'score': score
            })

        return jsonify(leadboard)

    except Exception as e:
        print(f"Error: {e}")
        return jsonify({'error': 'An error occurred while retriving the leadboard'}), 500

    finally:
        cursor.close()
        conn.close()

if __name__ == '__main__':
    app.run(debug=True)
