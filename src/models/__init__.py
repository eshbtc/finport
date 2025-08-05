from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

# Import all models to ensure they are registered with SQLAlchemy
from .security import Security, PriceData, FTDData, InstitutionalOwnership, OptionData, ETFHolding
from .user import User, Watchlist, WatchlistItem, UserSetting, Alert
from .analytics import SwapCycle, VolatilityCycle, MarketCorrelation, TechnicalIndicator
from .api_integration import ApiProvider, ApiKey, ApiEndpoint, ApiCallLog, DataSyncLog

def init_app(app):
    """Initialize the SQLAlchemy app"""
    db.init_app(app)
    
    # Create tables if they don't exist
    with app.app_context():
        db.create_all()
        
    return db

