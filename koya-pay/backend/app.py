from flask import Flask
from flask_cors import CORS
from routes import auth, database, recognition
from config import Config

app = Flask(__name__)
app.config.from_object(Config)
CORS(app)

app.register_blueprint(auth.bp)
app.register_blueprint(database.bp)
app.register_blueprint(recognition.bp)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)