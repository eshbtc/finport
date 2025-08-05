# Import all route blueprints
from .user import user_bp
from .security import security_bp

def register_routes(app):
    """Register all route blueprints with the Flask app"""
    app.register_blueprint(user_bp)
    app.register_blueprint(security_bp)

