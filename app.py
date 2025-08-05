import os
from src.main import app
from src.models import db

def init_db():
    """Initialize database within application context"""
    with app.app_context():
        # Import services here to ensure they're initialized within app context
        from src.services.polygon_service import PolygonService
        
        # Create database tables if they don't exist
        db.create_all()

# Initialize database when module is loaded (for gunicorn)
init_db()

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 10000))
    app.run(host="0.0.0.0", port=port)


