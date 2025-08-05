from flask import Blueprint, jsonify, request
from datetime import datetime
from ..models import db, User, Watchlist, WatchlistItem, UserSetting, Alert, Security
import hashlib
import json

user_bp = Blueprint('user', __name__, url_prefix='/api/users')

def hash_password(password):
    """Hash a password for storing"""
    return hashlib.sha256(password.encode()).hexdigest()

@user_bp.route('/', methods=['GET'])
def get_users():
    """Get all users"""
    try:
        users = User.query.all()
        return jsonify({
            'success': True,
            'data': [u.to_dict() for u in users]
        }), 200
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@user_bp.route('/<int:user_id>', methods=['GET'])
def get_user(user_id):
    """Get user by ID"""
    try:
        user = User.query.get_or_404(user_id)
        return jsonify({
            'success': True,
            'data': user.to_dict()
        }), 200
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@user_bp.route('/', methods=['POST'])
def create_user():
    """Create a new user"""
    try:
        data = request.json
        
        # Validate required fields
        if not data.get('username') or not data.get('email') or not data.get('password'):
            return jsonify({
                'success': False,
                'error': 'Username, email, and password are required'
            }), 400
        
        # Check if username or email already exists
        existing_user = User.query.filter(
            (User.username == data['username']) | 
            (User.email == data['email'])
        ).first()
        
        if existing_user:
            return jsonify({
                'success': False,
                'error': 'Username or email already exists'
            }), 400
        
        # Create new user
        user = User(
            username=data['username'],
            email=data['email'],
            password_hash=hash_password(data['password'])
        )
        
        db.session.add(user)
        db.session.commit()
        
        # Create default settings
        settings = UserSetting(
            user_id=user.id,
            theme='dark',
            default_chart_type='candlestick',
            default_timeframe='1d',
            show_volume=True,
            show_extended_hours=False,
            default_indicators=json.dumps(['sma_20', 'sma_50', 'sma_200', 'rsi'])
        )
        
        db.session.add(settings)
        
        # Create default watchlist
        watchlist = Watchlist(
            user_id=user.id,
            name='Default'
        )
        
        db.session.add(watchlist)
        db.session.commit()
        
        return jsonify({
            'success': True,
            'data': user.to_dict()
        }), 201
    except Exception as e:
        db.session.rollback()
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@user_bp.route('/<int:user_id>', methods=['PUT'])
def update_user(user_id):
    """Update a user"""
    try:
        user = User.query.get_or_404(user_id)
        
        data = request.json
        
        # Update fields
        if 'username' in data:
            user.username = data['username']
        if 'email' in data:
            user.email = data['email']
        if 'password' in data:
            user.password_hash = hash_password(data['password'])
        if 'is_active' in data:
            user.is_active = data['is_active']
        
        user.updated_at = datetime.utcnow()
        
        db.session.commit()
        
        return jsonify({
            'success': True,
            'data': user.to_dict()
        }), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@user_bp.route('/<int:user_id>', methods=['DELETE'])
def delete_user(user_id):
    """Delete a user"""
    try:
        user = User.query.get_or_404(user_id)
        
        # Delete related data
        UserSetting.query.filter_by(user_id=user_id).delete()
        Alert.query.filter_by(user_id=user_id).delete()
        
        # Delete watchlists and items
        watchlists = Watchlist.query.filter_by(user_id=user_id).all()
        for watchlist in watchlists:
            WatchlistItem.query.filter_by(watchlist_id=watchlist.id).delete()
        
        Watchlist.query.filter_by(user_id=user_id).delete()
        
        # Delete the user
        db.session.delete(user)
        db.session.commit()
        
        return '', 204
    except Exception as e:
        db.session.rollback()
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@user_bp.route('/<int:user_id>/watchlists', methods=['GET'])
def get_user_watchlists(user_id):
    """Get all watchlists for a user"""
    try:
        user = User.query.get_or_404(user_id)
        
        watchlists = Watchlist.query.filter_by(user_id=user_id).all()
        
        return jsonify({
            'success': True,
            'data': [w.to_dict() for w in watchlists]
        }), 200
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@user_bp.route('/<int:user_id>/watchlists', methods=['POST'])
def create_watchlist(user_id):
    """Create a new watchlist for a user"""
    try:
        user = User.query.get_or_404(user_id)
        
        data = request.json
        
        # Validate required fields
        if not data.get('name'):
            return jsonify({
                'success': False,
                'error': 'Watchlist name is required'
            }), 400
        
        # Check if watchlist with same name already exists
        existing_watchlist = Watchlist.query.filter_by(
            user_id=user_id,
            name=data['name']
        ).first()
        
        if existing_watchlist:
            return jsonify({
                'success': False,
                'error': f'Watchlist with name "{data["name"]}" already exists'
            }), 400
        
        # Create new watchlist
        watchlist = Watchlist(
            user_id=user_id,
            name=data['name']
        )
        
        db.session.add(watchlist)
        db.session.commit()
        
        return jsonify({
            'success': True,
            'data': watchlist.to_dict()
        }), 201
    except Exception as e:
        db.session.rollback()
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@user_bp.route('/<int:user_id>/watchlists/<int:watchlist_id>', methods=['PUT'])
def update_watchlist(user_id, watchlist_id):
    """Update a watchlist"""
    try:
        user = User.query.get_or_404(user_id)
        
        watchlist = Watchlist.query.get(watchlist_id)
        if not watchlist or watchlist.user_id != user_id:
            return jsonify({
                'success': False,
                'error': f'Watchlist with ID {watchlist_id} not found for user {user_id}'
            }), 404
        
        data = request.json
        
        # Update fields
        if 'name' in data:
            # Check if watchlist with same name already exists
            existing_watchlist = Watchlist.query.filter_by(
                user_id=user_id,
                name=data['name']
            ).first()
            
            if existing_watchlist and existing_watchlist.id != watchlist_id:
                return jsonify({
                    'success': False,
                    'error': f'Watchlist with name "{data["name"]}" already exists'
                }), 400
            
            watchlist.name = data['name']
        
        watchlist.updated_at = datetime.utcnow()
        
        db.session.commit()
        
        return jsonify({
            'success': True,
            'data': watchlist.to_dict()
        }), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@user_bp.route('/<int:user_id>/watchlists/<int:watchlist_id>', methods=['DELETE'])
def delete_watchlist(user_id, watchlist_id):
    """Delete a watchlist"""
    try:
        user = User.query.get_or_404(user_id)
        
        watchlist = Watchlist.query.get(watchlist_id)
        if not watchlist or watchlist.user_id != user_id:
            return jsonify({
                'success': False,
                'error': f'Watchlist with ID {watchlist_id} not found for user {user_id}'
            }), 404
        
        # Delete all watchlist items first
        WatchlistItem.query.filter_by(watchlist_id=watchlist_id).delete()
        
        # Delete the watchlist
        db.session.delete(watchlist)
        db.session.commit()
        
        return jsonify({
            'success': True,
            'message': f'Watchlist with ID {watchlist_id} deleted successfully'
        }), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@user_bp.route('/<int:user_id>/watchlists/<int:watchlist_id>/items', methods=['POST'])
def add_watchlist_item(user_id, watchlist_id):
    """Add an item to a watchlist"""
    try:
        user = User.query.get_or_404(user_id)
        
        watchlist = Watchlist.query.get(watchlist_id)
        if not watchlist or watchlist.user_id != user_id:
            return jsonify({
                'success': False,
                'error': f'Watchlist with ID {watchlist_id} not found for user {user_id}'
            }), 404
        
        data = request.json
        
        # Validate required fields
        if not data.get('ticker'):
            return jsonify({
                'success': False,
                'error': 'Security ticker is required'
            }), 400
        
        # Get security from database
        security = Security.query.filter_by(symbol=data['ticker'].upper()).first()
        
        # If not found, return error
        if not security:
            return jsonify({
                'success': False,
                'error': f'Security with ticker {data["ticker"]} not found'
            }), 404
        
        # Check if item already exists in watchlist
        existing_item = WatchlistItem.query.filter_by(
            watchlist_id=watchlist_id,
            security_id=security.id
        ).first()
        
        if existing_item:
            return jsonify({
                'success': False,
                'error': f'Security {data["ticker"]} already exists in watchlist'
            }), 400
        
        # Create new watchlist item
        item = WatchlistItem(
            watchlist_id=watchlist_id,
            security_id=security.id,
            notes=data.get('notes')
        )
        
        db.session.add(item)
        db.session.commit()
        
        return jsonify({
            'success': True,
            'data': item.to_dict()
        }), 201
    except Exception as e:
        db.session.rollback()
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@user_bp.route('/<int:user_id>/watchlists/<int:watchlist_id>/items/<int:item_id>', methods=['DELETE'])
def remove_watchlist_item(user_id, watchlist_id, item_id):
    """Remove an item from a watchlist"""
    try:
        user = User.query.get_or_404(user_id)
        
        watchlist = Watchlist.query.get(watchlist_id)
        if not watchlist or watchlist.user_id != user_id:
            return jsonify({
                'success': False,
                'error': f'Watchlist with ID {watchlist_id} not found for user {user_id}'
            }), 404
        
        item = WatchlistItem.query.get(item_id)
        if not item or item.watchlist_id != watchlist_id:
            return jsonify({
                'success': False,
                'error': f'Item with ID {item_id} not found in watchlist {watchlist_id}'
            }), 404
        
        db.session.delete(item)
        db.session.commit()
        
        return jsonify({
            'success': True,
            'message': f'Item with ID {item_id} removed from watchlist {watchlist_id}'
        }), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@user_bp.route('/<int:user_id>/settings', methods=['GET'])
def get_user_settings(user_id):
    """Get user settings"""
    try:
        user = User.query.get_or_404(user_id)
        
        settings = UserSetting.query.filter_by(user_id=user_id).first()
        
        if not settings:
            # Create default settings if not found
            settings = UserSetting(
                user_id=user_id,
                theme='dark',
                default_chart_type='candlestick',
                default_timeframe='1d',
                show_volume=True,
                show_extended_hours=False,
                default_indicators=json.dumps(['sma_20', 'sma_50', 'sma_200', 'rsi'])
            )
            
            db.session.add(settings)
            db.session.commit()
        
        return jsonify({
            'success': True,
            'data': settings.to_dict()
        }), 200
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@user_bp.route('/<int:user_id>/settings', methods=['PUT'])
def update_user_settings(user_id):
    """Update user settings"""
    try:
        user = User.query.get_or_404(user_id)
        
        settings = UserSetting.query.filter_by(user_id=user_id).first()
        
        if not settings:
            # Create default settings if not found
            settings = UserSetting(
                user_id=user_id,
                theme='dark',
                default_chart_type='candlestick',
                default_timeframe='1d',
                show_volume=True,
                show_extended_hours=False,
                default_indicators=json.dumps(['sma_20', 'sma_50', 'sma_200', 'rsi'])
            )
            
            db.session.add(settings)
        
        data = request.json
        
        # Update fields
        if 'theme' in data:
            settings.theme = data['theme']
        if 'default_chart_type' in data:
            settings.default_chart_type = data['default_chart_type']
        if 'default_timeframe' in data:
            settings.default_timeframe = data['default_timeframe']
        if 'show_volume' in data:
            settings.show_volume = data['show_volume']
        if 'show_extended_hours' in data:
            settings.show_extended_hours = data['show_extended_hours']
        if 'default_indicators' in data:
            settings.default_indicators = json.dumps(data['default_indicators'])
        
        settings.updated_at = datetime.utcnow()
        
        db.session.commit()
        
        return jsonify({
            'success': True,
            'data': settings.to_dict()
        }), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@user_bp.route('/<int:user_id>/alerts', methods=['GET'])
def get_user_alerts(user_id):
    """Get all alerts for a user"""
    try:
        user = User.query.get_or_404(user_id)
        
        alerts = Alert.query.filter_by(user_id=user_id).all()
        
        return jsonify({
            'success': True,
            'data': [a.to_dict() for a in alerts]
        }), 200
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@user_bp.route('/<int:user_id>/alerts', methods=['POST'])
def create_alert(user_id):
    """Create a new alert for a user"""
    try:
        user = User.query.get_or_404(user_id)
        
        data = request.json
        
        # Validate required fields
        if not data.get('ticker') or not data.get('alert_type') or 'value' not in data:
            return jsonify({
                'success': False,
                'error': 'Security ticker, alert type, and value are required'
            }), 400
        
        # Get security from database
        security = Security.query.filter_by(symbol=data['ticker'].upper()).first()
        
        # If not found, return error
        if not security:
            return jsonify({
                'success': False,
                'error': f'Security with ticker {data["ticker"]} not found'
            }), 404
        
        # Create new alert
        alert = Alert(
            user_id=user_id,
            security_id=security.id,
            alert_type=data['alert_type'],
            value=float(data['value']),
            is_active=True
        )
        
        db.session.add(alert)
        db.session.commit()
        
        return jsonify({
            'success': True,
            'data': alert.to_dict()
        }), 201
    except Exception as e:
        db.session.rollback()
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@user_bp.route('/<int:user_id>/alerts/<int:alert_id>', methods=['DELETE'])
def delete_alert(user_id, alert_id):
    """Delete an alert"""
    try:
        user = User.query.get_or_404(user_id)
        
        alert = Alert.query.get(alert_id)
        if not alert or alert.user_id != user_id:
            return jsonify({
                'success': False,
                'error': f'Alert with ID {alert_id} not found for user {user_id}'
            }), 404
        
        db.session.delete(alert)
        db.session.commit()
        
        return jsonify({
            'success': True,
            'message': f'Alert with ID {alert_id} deleted successfully'
        }), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500
