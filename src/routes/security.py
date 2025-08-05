from flask import Blueprint, jsonify, request
from datetime import datetime, timedelta
from ..models import db, Security, PriceData, FTDData
from ..services.polygon_service import PolygonService
from ..services.ftd_service import FTDService
from ..services.analytics_service import AnalyticsService
import os

security_bp = Blueprint('security', __name__, url_prefix='/api/securities')

# Initialize services with default API key if not in environment
polygon_service = PolygonService(api_key=os.environ.get('POLYGON_API_KEY', 'QqvHewfNYcDiPQUPVFblxK6SczJmcblY'))
ftd_service = FTDService()
analytics_service = AnalyticsService()

@security_bp.route('/', methods=['GET'])
def get_securities():
    """Get all securities"""
    try:
        securities = Security.query.all()
        return jsonify({
            'success': True,
            'data': [s.__dict__ for s in securities]
        }), 200
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@security_bp.route('/search', methods=['GET'])
def search_securities():
    """Search for securities by name or symbol"""
    try:
        query = request.args.get('q', '')
        if not query or len(query) < 2:
            return jsonify({
                'success': False,
                'error': 'Search query must be at least 2 characters'
            }), 400
        
        # Search in database first
        securities = Security.query.filter(
            (Security.symbol.ilike(f'%{query}%')) | 
            (Security.name.ilike(f'%{query}%'))
        ).all()
        
        # If not found in database, search via Polygon API
        if not securities:
            securities = polygon_service.search_tickers(query)
        
        return jsonify({
            'success': True,
            'data': [s.__dict__ for s in securities]
        }), 200
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@security_bp.route('/<string:ticker>', methods=['GET'])
def get_security(ticker):
    """Get security details by ticker symbol"""
    try:
        # Check if security exists in database
        security = Security.query.filter_by(symbol=ticker.upper()).first()
        
        # If not found, fetch from Polygon API
        if not security:
            security = polygon_service.get_ticker_details(ticker.upper())
            if not security:
                return jsonify({
                    'success': False,
                    'error': f'Security {ticker} not found'
                }), 404
        
        return jsonify({
            'success': True,
            'data': security.__dict__
        }), 200
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@security_bp.route('/<string:ticker>/price', methods=['GET'])
def get_security_price(ticker):
    """Get price data for a security"""
    try:
        # Parse query parameters
        from_date = request.args.get('from')
        to_date = request.args.get('to')
        timespan = request.args.get('timespan', 'day')
        
        # Get security from database
        security = Security.query.filter_by(symbol=ticker.upper()).first()
        
        # If not found, fetch from Polygon API
        if not security:
            security = polygon_service.get_ticker_details(ticker.upper())
            if not security:
                return jsonify({
                    'success': False,
                    'error': f'Security {ticker} not found'
                }), 404
        
        # Check if we have price data in the database
        price_data = PriceData.query.filter_by(security_id=security.id).all()
        
        # If no price data or requesting specific date range, fetch from Polygon API
        if not price_data or from_date or to_date:
            result = polygon_service.get_price_data(
                ticker.upper(),
                timespan=timespan,
                from_date=from_date,
                to_date=to_date
            )
            if not result:
                return jsonify({
                    'success': False,
                    'error': f'Failed to fetch price data for {ticker}'
                }), 500
            
            price_data = result['price_data']
        
        # Format response
        formatted_data = []
        for p in price_data:
            formatted_data.append({
                'date': p.date.isoformat(),
                'open': p.open,
                'high': p.high,
                'low': p.low,
                'close': p.close,
                'volume': p.volume,
                'vwap': p.vwap
            })
        
        return jsonify({
            'success': True,
            'data': {
                'security': security.__dict__,
                'price_data': formatted_data
            }
        }), 200
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@security_bp.route('/<string:ticker>/ftd', methods=['GET'])
def get_security_ftd(ticker):
    """Get FTD data for a security"""
    try:
        # Parse query parameters
        year = request.args.get('year')
        half = request.args.get('half')
        
        if year:
            year = int(year)
        if half:
            half = int(half)
        
        # Get security from database
        security = Security.query.filter_by(symbol=ticker.upper()).first()
        
        # If not found, fetch from Polygon API
        if not security:
            security = polygon_service.get_ticker_details(ticker.upper())
            if not security:
                return jsonify({
                    'success': False,
                    'error': f'Security {ticker} not found'
                }), 404
        
        # Check if we have FTD data in the database
        ftd_data = FTDData.query.filter_by(security_id=security.id).all()
        
        # If no FTD data or requesting specific year/half, fetch from SEC EDGAR
        if not ftd_data or (year and half):
            result = ftd_service.fetch_ftd_data(ticker.upper(), year, half)
            if not result:
                return jsonify({
                    'success': False,
                    'error': f'Failed to fetch FTD data for {ticker}'
                }), 500
            
            ftd_data = result['ftd_data']
        
        # Format response
        formatted_data = []
        for f in ftd_data:
            formatted_data.append({
                'date': f.date.isoformat(),
                'quantity': f.quantity,
                'price': f.price,
                'value': f.value
            })
        
        return jsonify({
            'success': True,
            'data': {
                'security': security.__dict__,
                'ftd_data': formatted_data
            }
        }), 200
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@security_bp.route('/<string:ticker>/indicators', methods=['GET'])
def get_security_indicators(ticker):
    """Get technical indicators for a security"""
    try:
        # Parse query parameters
        from_date = request.args.get('from')
        to_date = request.args.get('to')
        
        if from_date:
            from_date = datetime.strptime(from_date, '%Y-%m-%d').date()
        if to_date:
            to_date = datetime.strptime(to_date, '%Y-%m-%d').date()
        
        # Calculate technical indicators
        result = analytics_service.calculate_technical_indicators(ticker.upper(), from_date, to_date)
        if not result:
            return jsonify({
                'success': False,
                'error': f'Failed to calculate indicators for {ticker}'
            }), 500
        
        return jsonify({
            'success': True,
            'data': {
                'security': result['security'].__dict__,
                'indicators': result['indicators']
            }
        }), 200
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@security_bp.route('/<string:ticker>/swap-cycles', methods=['GET'])
def get_security_swap_cycles(ticker):
    """Get swap cycle analysis for a security"""
    try:
        # Parse query parameters
        lookback_days = request.args.get('lookback', 365)
        lookback_days = int(lookback_days)
        
        # Analyze swap cycles
        result = analytics_service.analyze_swap_cycles(ticker.upper(), lookback_days)
        if not result:
            return jsonify({
                'success': False,
                'error': f'Failed to analyze swap cycles for {ticker}'
            }), 500
        
        return jsonify({
            'success': True,
            'data': {
                'security': result['security'].__dict__,
                'cycles': result['cycles'],
                'price_data': result['price_data']
            }
        }), 200
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@security_bp.route('/<string:ticker>/volatility-cycles', methods=['GET'])
def get_security_volatility_cycles(ticker):
    """Get volatility cycle analysis for a security"""
    try:
        # Parse query parameters
        lookback_days = request.args.get('lookback', 365)
        lookback_days = int(lookback_days)
        
        # Analyze volatility cycles
        result = analytics_service.analyze_volatility_cycles(ticker.upper(), lookback_days)
        if not result:
            return jsonify({
                'success': False,
                'error': f'Failed to analyze volatility cycles for {ticker}'
            }), 500
        
        return jsonify({
            'success': True,
            'data': {
                'security': result['security'].__dict__,
                'volatility_data': result['volatility_data']
            }
        }), 200
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@security_bp.route('/<string:ticker>/correlations', methods=['GET'])
def get_security_correlations(ticker):
    """Get market correlations for a security"""
    try:
        # Parse query parameters
        comparison = request.args.get('comparison', 'SPY,QQQ,IWM')
        lookback_days = request.args.get('lookback', 90)
        lookback_days = int(lookback_days)
        
        comparison_tickers = comparison.split(',')
        
        # Calculate correlations
        result = analytics_service.calculate_market_correlations(ticker.upper(), comparison_tickers, lookback_days)
        if not result:
            return jsonify({
                'success': False,
                'error': f'Failed to calculate correlations for {ticker}'
            }), 500
        
        return jsonify({
            'success': True,
            'data': {
                'security': result['security'].__dict__,
                'correlations': result['correlations']
            }
        }), 200
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

