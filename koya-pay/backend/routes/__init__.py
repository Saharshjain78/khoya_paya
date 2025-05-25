from flask import Blueprint

# Initialize the routes blueprint
routes_bp = Blueprint('routes', __name__)

from . import auth, database, recognition  # Import routes to register them with the blueprint