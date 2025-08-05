import os
import requests
import logging
from datetime import datetime, timedelta
from polygon import RESTClient
from ..models import db, Security, PriceData, ApiProvider, ApiKey, ApiEndpoint, ApiCallLog, DataSyncLog

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class PolygonService:
    """Service for interacting with the Polygon.io API"""
    
    def __init__(self, api_key=None):
        """Initialize the Polygon service with API key"""
        self.api_key = api_key or os.environ.get('POLYGON_API_KEY')
        if not self.api_key:
            raise ValueError("Polygon API key is required")
        
        self.client = RESTClient(self.api_key)
        self.base_url = "https://api.polygon.io"
        
        # Register the API provider in the database
        self._register_api_provider()
    
    def _register_api_provider(self):
        """Register Polygon.io as an API provider in the database"""
        try:
            provider = ApiProvider.query.filter_by(name='Polygon.io').first()
            if not provider:
                provider = ApiProvider(
                    name='Polygon.io',
                    base_url=self.base_url,
                    description='Financial market data API providing real-time and historical data for stocks, options, and more.',
                    is_active=True
                )
                db.session.add(provider)
                db.session.commit()
                logger.info("Registered Polygon.io as API provider")
            
            # Register API key
            api_key = ApiKey.query.filter_by(provider_id=provider.id, key_name='default').first()
            if not api_key:
                api_key = ApiKey(
                    provider_id=provider.id,
                    key_name='default',
                    key_value=self.api_key,
                    is_active=True,
                    daily_limit=50000,  # Adjust based on your subscription
                    minute_limit=200    # Adjust based on your subscription
                )
                db.session.add(api_key)
                db.session.commit()
                logger.info("Registered Polygon.io API key")
                
            # Register common endpoints
            self._register_endpoints(provider.id)
            
        except Exception as e:
            logger.error(f"Error registering Polygon.io API provider: {str(e)}")
            db.session.rollback()
    
    def _register_endpoints(self, provider_id):
        """Register common Polygon.io API endpoints"""
        endpoints = [
            {
                'name': 'ticker_details',
                'path': '/v3/reference/tickers/{ticker}',
                'method': 'GET',
                'description': 'Get detailed information for a ticker symbol.'
            },
            {
                'name': 'aggregates',
                'path': '/v2/aggs/ticker/{ticker}/range/{multiplier}/{timespan}/{from}/{to}',
                'method': 'GET',
                'description': 'Get aggregate bars for a ticker over a given date range in custom time window sizes.'
            },
            {
                'name': 'previous_close',
                'path': '/v2/aggs/ticker/{ticker}/prev',
                'method': 'GET',
                'description': 'Get the previous day close for a ticker symbol.'
            },
            {
                'name': 'ticker_news',
                'path': '/v2/reference/news',
                'method': 'GET',
                'description': 'Get news articles for a ticker symbol.'
            }
        ]
        
        for endpoint_data in endpoints:
            endpoint = ApiEndpoint.query.filter_by(
                provider_id=provider_id, 
                name=endpoint_data['name']
            ).first()
            
            if not endpoint:
                endpoint = ApiEndpoint(
                    provider_id=provider_id,
                    name=endpoint_data['name'],
                    path=endpoint_data['path'],
                    method=endpoint_data['method'],
                    description=endpoint_data['description']
                )
                db.session.add(endpoint)
        
        db.session.commit()
        logger.info("Registered Polygon.io API endpoints")
    
    def _log_api_call(self, endpoint_name, url, method, params, response=None, error=None):
        """Log an API call to the database"""
        try:
            provider = ApiProvider.query.filter_by(name='Polygon.io').first()
            if not provider:
                return
            
            endpoint = ApiEndpoint.query.filter_by(provider_id=provider.id, name=endpoint_name).first()
            
            log = ApiCallLog(
                provider_id=provider.id,
                endpoint_id=endpoint.id if endpoint else None,
                request_url=url,
                request_method=method,
                request_params=str(params) if params else None,
                response_code=response.status_code if response else None,
                response_size=len(response.content) if response and hasattr(response, 'content') else None,
                is_success=response.ok if response else False,
                error_message=str(error) if error else None
            )
            
            db.session.add(log)
            db.session.commit()
            
        except Exception as e:
            logger.error(f"Error logging API call: {str(e)}")
            db.session.rollback()
    
    def get_ticker_details(self, ticker):
        """Get detailed information for a ticker symbol"""
        try:
            ticker_details = self.client.get_ticker_details(ticker)
            
            # Create or update security in database
            security = Security.query.filter_by(symbol=ticker).first()
            if not security:
                security = Security(
                    symbol=ticker,
                    name=ticker_details.name,
                    security_type=ticker_details.type.lower(),
                    exchange=ticker_details.primary_exchange,
                    sector=ticker_details.sic_description,
                    market_cap=ticker_details.market_cap
                )
                db.session.add(security)
            else:
                security.name = ticker_details.name
                security.security_type = ticker_details.type.lower()
                security.exchange = ticker_details.primary_exchange
                security.sector = ticker_details.sic_description
                security.market_cap = ticker_details.market_cap
                security.updated_at = datetime.utcnow()
            
            db.session.commit()
            return security
            
        except Exception as e:
            logger.error(f"Error getting ticker details for {ticker}: {str(e)}")
            url = f"{self.base_url}/v3/reference/tickers/{ticker}"
            self._log_api_call('ticker_details', url, 'GET', None, None, e)
            return None
    
    def get_price_data(self, ticker, timespan='day', from_date=None, to_date=None, limit=1000):
        """Get price data for a ticker symbol"""
        try:
            # Default to last 30 days if no dates provided
            if not from_date:
                from_date = (datetime.now() - timedelta(days=30)).strftime('%Y-%m-%d')
            if not to_date:
                to_date = datetime.now().strftime('%Y-%m-%d')
            
            # Get security from database or create if it doesn't exist
            security = Security.query.filter_by(symbol=ticker).first()
            if not security:
                security = self.get_ticker_details(ticker)
                if not security:
                    return None
            
            # Get aggregates from Polygon
            aggs = self.client.get_aggs(
                ticker=ticker,
                multiplier=1,
                timespan=timespan,
                from_=from_date,
                to=to_date,
                limit=limit
            )
            
            # Create data sync log
            sync_log = DataSyncLog(
                data_type='price_data',
                security_id=security.id,
                start_date=datetime.strptime(from_date, '%Y-%m-%d').date(),
                end_date=datetime.strptime(to_date, '%Y-%m-%d').date(),
                records_processed=len(aggs) if aggs else 0
            )
            
            records_added = 0
            records_updated = 0
            records_failed = 0
            
            # Process and store price data
            for agg in aggs:
                try:
                    # Convert timestamp to date
                    date = datetime.fromtimestamp(agg.timestamp / 1000).date()
                    
                    # Check if price data already exists for this date
                    price_data = PriceData.query.filter_by(
                        security_id=security.id,
                        date=date
                    ).first()
                    
                    if price_data:
                        # Update existing record
                        price_data.open = agg.open
                        price_data.high = agg.high
                        price_data.low = agg.low
                        price_data.close = agg.close
                        price_data.volume = agg.volume
                        price_data.vwap = agg.vwap
                        records_updated += 1
                    else:
                        # Create new record
                        price_data = PriceData(
                            security_id=security.id,
                            date=date,
                            open=agg.open,
                            high=agg.high,
                            low=agg.low,
                            close=agg.close,
                            volume=agg.volume,
                            vwap=agg.vwap
                        )
                        db.session.add(price_data)
                        records_added += 1
                        
                except Exception as e:
                    logger.error(f"Error processing price data for {ticker} on {date}: {str(e)}")
                    records_failed += 1
            
            # Update sync log
            sync_log.records_added = records_added
            sync_log.records_updated = records_updated
            sync_log.records_failed = records_failed
            sync_log.is_success = records_failed == 0
            
            db.session.add(sync_log)
            db.session.commit()
            
            return {
                'security': security,
                'price_data': PriceData.query.filter_by(security_id=security.id).all(),
                'sync_log': sync_log
            }
            
        except Exception as e:
            logger.error(f"Error getting price data for {ticker}: {str(e)}")
            url = f"{self.base_url}/v2/aggs/ticker/{ticker}/range/1/{timespan}/{from_date}/{to_date}"
            self._log_api_call('aggregates', url, 'GET', {'limit': limit}, None, e)
            db.session.rollback()
            return None
    
    def search_tickers(self, query, limit=10):
        """Search for tickers by name or symbol"""
        try:
            results = self.client.get_tickers(search=query, limit=limit)
            
            securities = []
            for result in results:
                # Check if security already exists
                security = Security.query.filter_by(symbol=result.ticker).first()
                if not security:
                    # Create new security
                    security = Security(
                        symbol=result.ticker,
                        name=result.name,
                        security_type=result.type.lower() if hasattr(result, 'type') else 'unknown',
                        exchange=result.primary_exchange if hasattr(result, 'primary_exchange') else None,
                        is_active=True
                    )
                    db.session.add(security)
                
                securities.append(security)
            
            db.session.commit()
            return securities
            
        except Exception as e:
            logger.error(f"Error searching tickers for '{query}': {str(e)}")
            url = f"{self.base_url}/v3/reference/tickers"
            self._log_api_call('search_tickers', url, 'GET', {'search': query, 'limit': limit}, None, e)
            return []
    
    def get_market_status(self):
        """Get current market status"""
        try:
            status = self.client.get_market_status()
            return status
        except Exception as e:
            logger.error(f"Error getting market status: {str(e)}")
            url = f"{self.base_url}/v1/marketstatus/now"
            self._log_api_call('market_status', url, 'GET', None, None, e)
            return None

