from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

db = SQLAlchemy()

class User(db.Model):
    """Model for users"""
    __tablename__ = 'users'
    
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(255), nullable=False)
    is_active = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    watchlists = db.relationship('Watchlist', backref='user', lazy=True)
    settings = db.relationship('UserSetting', backref='user', uselist=False, lazy=True)
    
    def __repr__(self):
        return f'<User {self.username}>'

    def to_dict(self):
        return {
            'id': self.id,
            'username': self.username,
            'email': self.email,
            'is_active': self.is_active,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }


class Watchlist(db.Model):
    """Model for user watchlists"""
    __tablename__ = 'watchlists'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    name = db.Column(db.String(100), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    items = db.relationship('WatchlistItem', backref='watchlist', lazy=True)
    
    __table_args__ = (
        db.UniqueConstraint('user_id', 'name', name='uix_watchlist_user_name'),
    )
    
    def __repr__(self):
        return f'<Watchlist {self.name} (User: {self.user.username})>'

    def to_dict(self):
        return {
            'id': self.id,
            'user_id': self.user_id,
            'name': self.name,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None,
            'items': [item.to_dict() for item in self.items]
        }


class WatchlistItem(db.Model):
    """Model for items in a watchlist"""
    __tablename__ = 'watchlist_items'
    
    id = db.Column(db.Integer, primary_key=True)
    watchlist_id = db.Column(db.Integer, db.ForeignKey('watchlists.id'), nullable=False)
    security_id = db.Column(db.Integer, db.ForeignKey('securities.id'), nullable=False)
    added_at = db.Column(db.DateTime, default=datetime.utcnow)
    notes = db.Column(db.Text)
    
    # Relationship to Security
    security = db.relationship('Security')
    
    __table_args__ = (
        db.UniqueConstraint('watchlist_id', 'security_id', name='uix_watchlist_item_watchlist_security'),
    )
    
    def __repr__(self):
        return f'<WatchlistItem {self.security.symbol} in {self.watchlist.name}>'

    def to_dict(self):
        return {
            'id': self.id,
            'watchlist_id': self.watchlist_id,
            'security_id': self.security_id,
            'security_symbol': self.security.symbol if self.security else None,
            'added_at': self.added_at.isoformat() if self.added_at else None,
            'notes': self.notes
        }


class UserSetting(db.Model):
    """Model for user settings"""
    __tablename__ = 'user_settings'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False, unique=True)
    theme = db.Column(db.String(20), default='dark')  # dark, light
    default_chart_type = db.Column(db.String(20), default='candlestick')  # candlestick, line, ohlc
    default_timeframe = db.Column(db.String(10), default='1d')  # 1d, 1w, 1m, etc.
    show_volume = db.Column(db.Boolean, default=True)
    show_extended_hours = db.Column(db.Boolean, default=False)
    default_indicators = db.Column(db.Text)  # JSON string of default indicators
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    def __repr__(self):
        return f'<UserSetting for {self.user.username}>'

    def to_dict(self):
        return {
            'id': self.id,
            'user_id': self.user_id,
            'theme': self.theme,
            'default_chart_type': self.default_chart_type,
            'default_timeframe': self.default_timeframe,
            'show_volume': self.show_volume,
            'show_extended_hours': self.show_extended_hours,
            'default_indicators': self.default_indicators,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }


class Alert(db.Model):
    """Model for price alerts"""
    __tablename__ = 'alerts'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    security_id = db.Column(db.Integer, db.ForeignKey('securities.id'), nullable=False)
    alert_type = db.Column(db.String(20), nullable=False)  # price_above, price_below, percent_change, etc.
    value = db.Column(db.Float, nullable=False)  # The price or percentage threshold
    is_active = db.Column(db.Boolean, default=True)
    is_triggered = db.Column(db.Boolean, default=False)
    triggered_at = db.Column(db.DateTime)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relationships
    user = db.relationship('User', backref='alerts')
    security = db.relationship('Security')
    
    def __repr__(self):
        return f'<Alert {self.alert_type} {self.value} for {self.security.symbol}>'

    def to_dict(self):
        return {
            'id': self.id,
            'user_id': self.user_id,
            'security_id': self.security_id,
            'security_symbol': self.security.symbol if self.security else None,
            'alert_type': self.alert_type,
            'value': self.value,
            'is_active': self.is_active,
            'is_triggered': self.is_triggered,
            'triggered_at': self.triggered_at.isoformat() if self.triggered_at else None,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }
