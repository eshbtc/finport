from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

db = SQLAlchemy()

class Security(db.Model):
    """Model for securities (stocks, ETFs, etc.)"""
    __tablename__ = 'securities'
    
    id = db.Column(db.Integer, primary_key=True)
    symbol = db.Column(db.String(20), unique=True, nullable=False, index=True)
    name = db.Column(db.String(255), nullable=False)
    security_type = db.Column(db.String(20), nullable=False)  # stock, etf, etc.
    exchange = db.Column(db.String(20))
    is_active = db.Column(db.Boolean, default=True)
    sector = db.Column(db.String(100))
    industry = db.Column(db.String(100))
    market_cap = db.Column(db.Float)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    price_data = db.relationship('PriceData', backref='security', lazy=True)
    ftd_data = db.relationship('FTDData', backref='security', lazy=True)
    
    def __repr__(self):
        return f'<Security {self.symbol}>'


class PriceData(db.Model):
    """Model for price data"""
    __tablename__ = 'price_data'
    
    id = db.Column(db.Integer, primary_key=True)
    security_id = db.Column(db.Integer, db.ForeignKey('securities.id'), nullable=False)
    date = db.Column(db.Date, nullable=False)
    open = db.Column(db.Float)
    high = db.Column(db.Float)
    low = db.Column(db.Float)
    close = db.Column(db.Float, nullable=False)
    volume = db.Column(db.BigInteger)
    vwap = db.Column(db.Float)  # Volume-weighted average price
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    __table_args__ = (
        db.UniqueConstraint('security_id', 'date', name='uix_price_data_security_date'),
    )
    
    def __repr__(self):
        return f'<PriceData {self.security.symbol} {self.date}>'


class FTDData(db.Model):
    """Model for Failure-to-Deliver data"""
    __tablename__ = 'ftd_data'
    
    id = db.Column(db.Integer, primary_key=True)
    security_id = db.Column(db.Integer, db.ForeignKey('securities.id'), nullable=False)
    date = db.Column(db.Date, nullable=False)
    quantity = db.Column(db.Integer, nullable=False)
    price = db.Column(db.Float, nullable=False)
    value = db.Column(db.Float, nullable=False)  # quantity * price
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    __table_args__ = (
        db.UniqueConstraint('security_id', 'date', name='uix_ftd_data_security_date'),
    )
    
    def __repr__(self):
        return f'<FTDData {self.security.symbol} {self.date}>'


class InstitutionalOwnership(db.Model):
    """Model for institutional ownership data"""
    __tablename__ = 'institutional_ownership'
    
    id = db.Column(db.Integer, primary_key=True)
    security_id = db.Column(db.Integer, db.ForeignKey('securities.id'), nullable=False)
    institution_name = db.Column(db.String(255), nullable=False)
    date = db.Column(db.Date, nullable=False)
    shares = db.Column(db.BigInteger, nullable=False)
    value = db.Column(db.Float)
    percentage = db.Column(db.Float)  # Percentage of outstanding shares
    change = db.Column(db.Float)  # Change from previous filing
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    __table_args__ = (
        db.UniqueConstraint('security_id', 'institution_name', 'date', 
                           name='uix_inst_ownership_security_inst_date'),
    )
    
    def __repr__(self):
        return f'<InstitutionalOwnership {self.security.symbol} {self.institution_name} {self.date}>'


class OptionData(db.Model):
    """Model for options data"""
    __tablename__ = 'option_data'
    
    id = db.Column(db.Integer, primary_key=True)
    security_id = db.Column(db.Integer, db.ForeignKey('securities.id'), nullable=False)
    option_type = db.Column(db.String(4), nullable=False)  # call or put
    expiration_date = db.Column(db.Date, nullable=False)
    strike_price = db.Column(db.Float, nullable=False)
    date = db.Column(db.Date, nullable=False)  # Trading date
    open = db.Column(db.Float)
    high = db.Column(db.Float)
    low = db.Column(db.Float)
    close = db.Column(db.Float)
    volume = db.Column(db.Integer)
    open_interest = db.Column(db.Integer)
    implied_volatility = db.Column(db.Float)
    delta = db.Column(db.Float)
    gamma = db.Column(db.Float)
    theta = db.Column(db.Float)
    vega = db.Column(db.Float)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    __table_args__ = (
        db.UniqueConstraint('security_id', 'option_type', 'expiration_date', 
                           'strike_price', 'date', 
                           name='uix_option_data_security_type_exp_strike_date'),
    )
    
    def __repr__(self):
        return f'<OptionData {self.security.symbol} {self.option_type} {self.strike_price} {self.expiration_date}>'


class ETFHolding(db.Model):
    """Model for ETF holdings"""
    __tablename__ = 'etf_holdings'
    
    id = db.Column(db.Integer, primary_key=True)
    etf_id = db.Column(db.Integer, db.ForeignKey('securities.id'), nullable=False)
    holding_id = db.Column(db.Integer, db.ForeignKey('securities.id'), nullable=False)
    date = db.Column(db.Date, nullable=False)
    shares = db.Column(db.BigInteger)
    weight = db.Column(db.Float)  # Percentage weight in ETF
    value = db.Column(db.Float)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Define relationships with aliases to distinguish between ETF and holding
    etf = db.relationship('Security', foreign_keys=[etf_id], backref='holdings')
    holding = db.relationship('Security', foreign_keys=[holding_id], backref='in_etfs')
    
    __table_args__ = (
        db.UniqueConstraint('etf_id', 'holding_id', 'date', name='uix_etf_holding_etf_holding_date'),
    )
    
    def __repr__(self):
        return f'<ETFHolding {self.etf.symbol} holds {self.holding.symbol} {self.date}>'

