from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
from .security import db

class SwapCycle(db.Model):
    """Model for swap theory cycle data"""
    __tablename__ = 'swap_cycles'
    
    id = db.Column(db.Integer, primary_key=True)
    security_id = db.Column(db.Integer, db.ForeignKey('securities.id'), nullable=False)
    cycle_type = db.Column(db.String(20), nullable=False)  # quarterly, monthly, etc.
    cycle_number = db.Column(db.Integer, nullable=False)
    start_date = db.Column(db.Date, nullable=False)
    end_date = db.Column(db.Date, nullable=False)
    predicted_end_date = db.Column(db.Date)
    peak_price = db.Column(db.Float)
    trough_price = db.Column(db.Float)
    volatility_score = db.Column(db.Float)
    confidence_score = db.Column(db.Float)  # 0-1 confidence in cycle prediction
    is_active = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationship
    security = db.relationship('Security', backref='swap_cycles')
    
    def __repr__(self):
        return f'<SwapCycle {self.security.symbol} {self.cycle_type} #{self.cycle_number}>'

    def to_dict(self):
        return {
            'id': self.id,
            'security_id': self.security_id,
            'security_symbol': self.security.symbol if self.security else None,
            'cycle_type': self.cycle_type,
            'cycle_number': self.cycle_number,
            'start_date': self.start_date.isoformat() if self.start_date else None,
            'end_date': self.end_date.isoformat() if self.end_date else None,
            'predicted_end_date': self.predicted_end_date.isoformat() if self.predicted_end_date else None,
            'peak_price': self.peak_price,
            'trough_price': self.trough_price,
            'volatility_score': self.volatility_score,
            'confidence_score': self.confidence_score,
            'is_active': self.is_active,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }


class VolatilityCycle(db.Model):
    """Model for volatility cycle analysis"""
    __tablename__ = 'volatility_cycles'
    
    id = db.Column(db.Integer, primary_key=True)
    security_id = db.Column(db.Integer, db.ForeignKey('securities.id'), nullable=False)
    date = db.Column(db.Date, nullable=False)
    cycle_phase = db.Column(db.String(20), nullable=False)  # accumulation, markup, distribution, markdown
    volatility_regime = db.Column(db.String(20), nullable=False)  # low, medium, high
    implied_volatility = db.Column(db.Float)
    realized_volatility = db.Column(db.Float)
    volatility_rank = db.Column(db.Float)  # Percentile rank of current volatility
    volatility_percentile = db.Column(db.Float)  # Historical percentile
    vix_correlation = db.Column(db.Float)  # Correlation with VIX
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relationship
    security = db.relationship('Security', backref='volatility_cycles')
    
    __table_args__ = (
        db.UniqueConstraint('security_id', 'date', name='uix_volatility_cycle_security_date'),
    )
    
    def __repr__(self):
        return f'<VolatilityCycle {self.security.symbol} {self.date} {self.cycle_phase}>'

    def to_dict(self):
        return {
            'id': self.id,
            'security_id': self.security_id,
            'security_symbol': self.security.symbol if self.security else None,
            'date': self.date.isoformat() if self.date else None,
            'cycle_phase': self.cycle_phase,
            'volatility_regime': self.volatility_regime,
            'implied_volatility': self.implied_volatility,
            'realized_volatility': self.realized_volatility,
            'volatility_rank': self.volatility_rank,
            'volatility_percentile': self.volatility_percentile,
            'vix_correlation': self.vix_correlation,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }


class MarketCorrelation(db.Model):
    """Model for market correlation data"""
    __tablename__ = 'market_correlations'
    
    id = db.Column(db.Integer, primary_key=True)
    security_id = db.Column(db.Integer, db.ForeignKey('securities.id'), nullable=False)
    correlated_security_id = db.Column(db.Integer, db.ForeignKey('securities.id'), nullable=False)
    date = db.Column(db.Date, nullable=False)
    correlation_period = db.Column(db.Integer, nullable=False)  # Days used for correlation calculation
    correlation_coefficient = db.Column(db.Float, nullable=False)  # -1 to 1
    beta = db.Column(db.Float)  # Beta coefficient
    r_squared = db.Column(db.Float)  # R-squared value
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relationships
    security = db.relationship('Security', foreign_keys=[security_id], backref='correlations_as_primary')
    correlated_security = db.relationship('Security', foreign_keys=[correlated_security_id], backref='correlations_as_secondary')
    
    __table_args__ = (
        db.UniqueConstraint('security_id', 'correlated_security_id', 'date', 'correlation_period',
                           name='uix_market_correlation_securities_date_period'),
    )
    
    def __repr__(self):
        return f'<MarketCorrelation {self.security.symbol} vs {self.correlated_security.symbol} {self.date}>'

    def to_dict(self):
        return {
            'id': self.id,
            'security_id': self.security_id,
            'security_symbol': self.security.symbol if self.security else None,
            'correlated_security_id': self.correlated_security_id,
            'correlated_security_symbol': self.correlated_security.symbol if self.correlated_security else None,
            'date': self.date.isoformat() if self.date else None,
            'correlation_period': self.correlation_period,
            'correlation_coefficient': self.correlation_coefficient,
            'beta': self.beta,
            'r_squared': self.r_squared,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }


class TechnicalIndicator(db.Model):
    """Model for technical indicator values"""
    __tablename__ = 'technical_indicators'
    
    id = db.Column(db.Integer, primary_key=True)
    security_id = db.Column(db.Integer, db.ForeignKey('securities.id'), nullable=False)
    date = db.Column(db.Date, nullable=False)
    indicator_name = db.Column(db.String(50), nullable=False)  # RSI, MACD, SMA, etc.
    indicator_value = db.Column(db.Float, nullable=False)
    indicator_signal = db.Column(db.String(10))  # buy, sell, hold
    timeframe = db.Column(db.String(10), nullable=False)  # 1d, 1h, etc.
    parameters = db.Column(db.Text)  # JSON string of indicator parameters
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relationship
    security = db.relationship('Security', backref='technical_indicators')
    
    __table_args__ = (
        db.UniqueConstraint('security_id', 'date', 'indicator_name', 'timeframe',
                           name='uix_technical_indicator_security_date_name_timeframe'),
    )
    
    def __repr__(self):
        return f'<TechnicalIndicator {self.security.symbol} {self.indicator_name} {self.date}>'

    def to_dict(self):
        return {
            'id': self.id,
            'security_id': self.security_id,
            'security_symbol': self.security.symbol if self.security else None,
            'date': self.date.isoformat() if self.date else None,
            'indicator_name': self.indicator_name,
            'indicator_value': self.indicator_value,
            'indicator_signal': self.indicator_signal,
            'timeframe': self.timeframe,
            'parameters': self.parameters,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }

