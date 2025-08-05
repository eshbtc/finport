from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
from .security import db

class ApiProvider(db.Model):
    """Model for API providers"""
    __tablename__ = 'api_providers'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False, unique=True)
    base_url = db.Column(db.String(255))
    description = db.Column(db.Text)
    is_active = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    api_keys = db.relationship('ApiKey', backref='provider', lazy=True)
    endpoints = db.relationship('ApiEndpoint', backref='provider', lazy=True)
    
    def __repr__(self):
        return f'<ApiProvider {self.name}>'

    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'base_url': self.base_url,
            'description': self.description,
            'is_active': self.is_active,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }


class ApiKey(db.Model):
    """Model for API keys"""
    __tablename__ = 'api_keys'
    
    id = db.Column(db.Integer, primary_key=True)
    provider_id = db.Column(db.Integer, db.ForeignKey('api_providers.id'), nullable=False)
    key_name = db.Column(db.String(100), nullable=False)
    key_value = db.Column(db.String(255), nullable=False)
    is_active = db.Column(db.Boolean, default=True)
    daily_limit = db.Column(db.Integer)  # Daily API call limit
    minute_limit = db.Column(db.Integer)  # Per-minute API call limit
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    __table_args__ = (
        db.UniqueConstraint('provider_id', 'key_name', name='uix_api_key_provider_name'),
    )
    
    def __repr__(self):
        return f'<ApiKey {self.provider.name} {self.key_name}>'

    def to_dict(self):
        return {
            'id': self.id,
            'provider_id': self.provider_id,
            'provider_name': self.provider.name if self.provider else None,
            'key_name': self.key_name,
            'is_active': self.is_active,
            'daily_limit': self.daily_limit,
            'minute_limit': self.minute_limit,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }


class ApiEndpoint(db.Model):
    """Model for API endpoints"""
    __tablename__ = 'api_endpoints'
    
    id = db.Column(db.Integer, primary_key=True)
    provider_id = db.Column(db.Integer, db.ForeignKey('api_providers.id'), nullable=False)
    name = db.Column(db.String(100), nullable=False)
    path = db.Column(db.String(255), nullable=False)
    method = db.Column(db.String(10), nullable=False, default='GET')  # GET, POST, etc.
    description = db.Column(db.Text)
    parameters = db.Column(db.Text)  # JSON string of parameters
    response_format = db.Column(db.Text)  # JSON string of response format
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    __table_args__ = (
        db.UniqueConstraint('provider_id', 'name', name='uix_api_endpoint_provider_name'),
    )
    
    def __repr__(self):
        return f'<ApiEndpoint {self.provider.name} {self.name}>'

    def to_dict(self):
        return {
            'id': self.id,
            'provider_id': self.provider_id,
            'provider_name': self.provider.name if self.provider else None,
            'name': self.name,
            'path': self.path,
            'method': self.method,
            'description': self.description,
            'parameters': self.parameters,
            'response_format': self.response_format,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }


class ApiCallLog(db.Model):
    """Model for API call logs"""
    __tablename__ = 'api_call_logs'
    
    id = db.Column(db.Integer, primary_key=True)
    provider_id = db.Column(db.Integer, db.ForeignKey('api_providers.id'), nullable=False)
    endpoint_id = db.Column(db.Integer, db.ForeignKey('api_endpoints.id'))
    request_url = db.Column(db.String(255), nullable=False)
    request_method = db.Column(db.String(10), nullable=False)
    request_params = db.Column(db.Text)
    response_code = db.Column(db.Integer)
    response_size = db.Column(db.Integer)  # Size in bytes
    execution_time = db.Column(db.Float)  # Time in seconds
    is_success = db.Column(db.Boolean, default=True)
    error_message = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relationships
    provider = db.relationship('ApiProvider')
    endpoint = db.relationship('ApiEndpoint')
    
    def __repr__(self):
        return f'<ApiCallLog {self.provider.name} {self.request_method} {self.created_at}>'

    def to_dict(self):
        return {
            'id': self.id,
            'provider_id': self.provider_id,
            'provider_name': self.provider.name if self.provider else None,
            'endpoint_id': self.endpoint_id,
            'endpoint_name': self.endpoint.name if self.endpoint else None,
            'request_url': self.request_url,
            'request_method': self.request_method,
            'request_params': self.request_params,
            'response_code': self.response_code,
            'response_size': self.response_size,
            'execution_time': self.execution_time,
            'is_success': self.is_success,
            'error_message': self.error_message,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }


class DataSyncLog(db.Model):
    """Model for data synchronization logs"""
    __tablename__ = 'data_sync_logs'
    
    id = db.Column(db.Integer, primary_key=True)
    data_type = db.Column(db.String(50), nullable=False)  # price_data, ftd_data, etc.
    security_id = db.Column(db.Integer, db.ForeignKey('securities.id'))
    start_date = db.Column(db.Date)
    end_date = db.Column(db.Date)
    records_processed = db.Column(db.Integer, default=0)
    records_added = db.Column(db.Integer, default=0)
    records_updated = db.Column(db.Integer, default=0)
    records_failed = db.Column(db.Integer, default=0)
    is_success = db.Column(db.Boolean, default=True)
    error_message = db.Column(db.Text)
    execution_time = db.Column(db.Float)  # Time in seconds
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relationship
    security = db.relationship('Security')
    
    def __repr__(self):
        security_symbol = self.security.symbol if self.security else 'ALL'
        return f'<DataSyncLog {self.data_type} {security_symbol} {self.created_at}>'

    def to_dict(self):
        return {
            'id': self.id,
            'data_type': self.data_type,
            'security_id': self.security_id,
            'security_symbol': self.security.symbol if self.security else None,
            'start_date': self.start_date.isoformat() if self.start_date else None,
            'end_date': self.end_date.isoformat() if self.end_date else None,
            'records_processed': self.records_processed,
            'records_added': self.records_added,
            'records_updated': self.records_updated,
            'records_failed': self.records_failed,
            'is_success': self.is_success,
            'error_message': self.error_message,
            'execution_time': self.execution_time,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }

