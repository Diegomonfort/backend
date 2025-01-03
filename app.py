from flask import Flask
from flask_cors import CORS

# Importing Blueprints
from routes.users import users_bp
from routes.auth import auth_bp
from routes.fruits import fruits_bp
from routes.gameQuestion import game_question_bp
from routes.session import session_bp
from routes.questionsMade import fruit_comparisons_bp
from routes.leadboard import leadboard_bp

app = Flask(__name__)
CORS(app) #Added this for some problems with cors on testing


# Registrar blueprints
app.register_blueprint(users_bp, url_prefix='/api')
app.register_blueprint(fruits_bp, url_prefix='/api')
app.register_blueprint(leadboard_bp, url_prefix='/api')

app.register_blueprint(game_question_bp, url_prefix='/api/game')
app.register_blueprint(session_bp, url_prefix='/api/game')
app.register_blueprint(fruit_comparisons_bp, url_prefix='/api/game')

app.register_blueprint(auth_bp, url_prefix='/api/auth')



if __name__ == '__main__':
    app.run(debug=True)
