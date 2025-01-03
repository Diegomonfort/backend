from flask import Flask, jsonify, request, Blueprint
import random
from db import get_db_connection

app = Flask(__name__)
game_question_bp = Blueprint('question', __name__)



# Endpoint to retrieve a new question
@game_question_bp.route('/question', methods=['GET'])
def get_game_question():
    session_id = request.args.get('session_id')

    try:
        conn = get_db_connection()
        cursor = conn.cursor()

        # Get a random question from questions Table
        cursor.execute('SELECT * FROM questions ORDER BY RANDOM() LIMIT 1')
        question = cursor.fetchone()

        if not question:
            return jsonify({'error': 'No questions available'}), 404

        question_id, question_text, question_type = question

        # Get two random fruits from fruits Table
        cursor.execute('SELECT * FROM fruits ORDER BY RANDOM() LIMIT 2')
        fruits = cursor.fetchall()

        if len(fruits) < 2:
            return jsonify({'error': 'Not enough fruits in the database'}), 404

        # Fruit data
        fruit1_id, fruit1_name, fruit1_family, fruit1_order, fruit1_genus, fruit1_nutritions = fruits[0]
        fruit2_id, fruit2_name, fruit2_family, fruit2_order, fruit2_genus, fruit2_nutritions = fruits[1]

        # Check if the fruits have been compared previously on the actual session
        cursor.execute(""" 
            SELECT * FROM fruit_comparisons 
            WHERE session_id = %s AND 
            ((fruit1_id = %s AND fruit2_id = %s) OR 
            (fruit1_id = %s AND fruit2_id = %s))
        """, (session_id, fruit1_id, fruit2_id, fruit1_id, fruit2_id))

        previous_comparisons = cursor.fetchall()

        if previous_comparisons:
            # Check if a comparison with the same attribute exists
            same_attribute_comparison = any(
                comparison['attribute'] != 'family' for comparison in previous_comparisons
            )

            if same_attribute_comparison:
                # If compared select new fruits
                return get_game_question()

        # Select the question type (Equal for atributes - Different for family)
        correct_fruit_id = None
        comparison_attribute = None

        if question_type == 'equal':
            # Get a random nutritional attribute
            attributes = ['calories', 'carbohydrates', 'fat', 'protein', 'sugar']
            comparison_attribute = random.choice(attributes)

            # Retrieve values of the selected attribute
            fruit1_value = fruit1_nutritions.get(comparison_attribute, 0)
            fruit2_value = fruit2_nutritions.get(comparison_attribute, 0)

            # Select the correct fruit depend on the higher value
            if fruit1_value > fruit2_value:
                correct_fruit_id = fruit1_id
            else:
                correct_fruit_id = fruit2_id

            # Male the question
            question_text = f"Which fruit has more {comparison_attribute}?"

        elif question_type == 'different':

            comparison_attribute = 'family'

            if fruit1_family == fruit2_family:
                # If fruits have the same family, select another combination
                return get_game_question()

            # Make the question
            question_text = f"Which fruit belongs to the family {fruit1_family}?"

            # Select random winner question (i made this step because the correct answer was always the first option)
            fruits = [
                {'id': fruit1_id, 'name': fruit1_name, 'family': fruit1_family},
                {'id': fruit2_id, 'name': fruit2_name, 'family': fruit2_family}
            ]

            random.shuffle(fruits)

            # After random, select the correct fruit
            correct_fruit_id = fruits[0]['id'] if fruits[0]['family'] == fruit1_family else fruits[1]['id']

            # Update the fruit order
            fruit1_id, fruit1_name, fruit1_family = fruits[0]['id'], fruits[0]['name'], fruits[0]['family']
            fruit2_id, fruit2_name, fruit2_family = fruits[1]['id'], fruits[1]['name'], fruits[1]['family']


        # Save the question to fruit_comparisons Table to avoid repetition
        cursor.execute(""" 
            INSERT INTO fruit_comparisons (session_id, question_id, fruit1_id, fruit2_id, attribute, result)
            VALUES (%s, %s, %s, %s, %s, %s)
        """, (session_id, question_id, fruit1_id, fruit2_id, comparison_attribute, correct_fruit_id))

        conn.commit()

        # Return the question, fruits, and correct fruit for the response json
        response = {
            'question': question_text,
            'fruits': [
                {
                    'id': fruit1_id,
                    'name': fruit1_name,
                    'family': fruit1_family,
                    'value': fruit1_nutritions.get(comparison_attribute) if comparison_attribute != 'family' else None # If the comparison atribute is nutriotions, then put null because is not going to be used this
                },
                {
                    'id': fruit2_id,
                    'name': fruit2_name,
                    'family': fruit2_family,
                    'value': fruit2_nutritions.get(comparison_attribute) if comparison_attribute != 'family' else None
                }
            ],
            'correct_fruit_id': correct_fruit_id,
            'comparison_attribute': comparison_attribute
        }

        return jsonify(response)

    except Exception as e:
        print(f"Error: {e}")
        return jsonify({'error': 'An error occurred while retrieving the question'}), 500

    finally:
        cursor.close()
        conn.close()

if __name__ == '__main__':
    app.run(debug=True)
