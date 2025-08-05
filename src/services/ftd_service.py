import os
import requests
import pandas as pd
import logging
from datetime import datetime, timedelta
from io import StringIO
from ..models import db, Security, FTDData, ApiProvider, ApiKey, ApiEndpoint, ApiCallLog, DataSyncLog

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class FTDService:
    """Service for fetching and processing Failure-to-Deliver (FTD) data from SEC EDGAR"""
    
    def __init__(self):
        """Initialize the FTD service"""
        self.base_url = "https://www.sec.gov/data/foiadocsfailsdatahtm"
        self._provider_registered = False
    
    def _ensure_registered(self):
        """Ensure the API provider is registered before making API calls"""
        if not self._provider_registered:
            try:
                # Only register if we're in a Flask app context
                from flask import current_app
                if current_app:
                    self._register_api_provider()
                    self._provider_registered = True
            except Exception as e:
                # Log but don't fail - API calls can still work without registration
                logger.warning(f"Could not register API provider: {str(e)}")
    
    def _register_api_provider(self):
        """Register SEC EDGAR as an API provider in the database"""
        try:
            provider = ApiProvider.query.filter_by(name='SEC EDGAR').first()
            if not provider:
                provider = ApiProvider(
                    name='SEC EDGAR',
                    base_url='https://www.sec.gov',
                    description='SEC EDGAR database providing regulatory filings and FTD data.',
                    is_active=True
                )
                db.session.add(provider)
                db.session.commit()
                logger.info("Registered SEC EDGAR as API provider")
            
            # Register common endpoints
            self._register_endpoints(provider.id)
            
        except Exception as e:
            logger.error(f"Error registering SEC EDGAR API provider: {str(e)}")
            db.session.rollback()
    
    def _register_endpoints(self, provider_id):
        """Register common SEC EDGAR API endpoints"""
        endpoints = [
            {
                'name': 'ftd_data',
                'path': '/data/foiadocsfailsdatahtm',
                'method': 'GET',
                'description': 'Get Failure-to-Deliver data from SEC EDGAR.'
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
        logger.info("Registered SEC EDGAR API endpoints")
    
    def _log_api_call(self, endpoint_name, url, method, params, response=None, error=None):
        """Log an API call to the database"""
        try:
            provider = ApiProvider.query.filter_by(name='SEC EDGAR').first()
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
    
    def _get_ftd_file_urls(self, year=None, half=None):
        """Get URLs for FTD data files based on year and half"""
        current_year = datetime.now().year
        current_month = datetime.now().month
        
        # Default to current year and half if not specified
        if not year:
            year = current_year
        if not half:
            half = 1 if current_month <= 6 else 2
        
        # Ensure year and half are valid
        if year < 2009 or year > current_year:
            raise ValueError(f"Year must be between 2009 and {current_year}")
        if half not in [1, 2]:
            raise ValueError("Half must be 1 or 2")
        
        # Check if requesting future data
        if year == current_year and half == 2 and current_month <= 6:
            raise ValueError("Data for second half of current year is not yet available")
        
        # Format URLs based on year and half
        if year >= 2010:
            if half == 1:
                return [f"https://www.sec.gov/files/data/fails-deliver-data/cnsfails{year}a.zip"]
            else:
                return [f"https://www.sec.gov/files/data/fails-deliver-data/cnsfails{year}b.zip"]
        else:
            # 2009 has a different format
            urls = []
            if half == 1:
                for month in range(1, 7):
                    urls.append(f"https://www.sec.gov/files/data/fails-deliver-data/cnsfails{year}0{month}.zip")
            else:
                for month in range(7, 13):
                    urls.append(f"https://www.sec.gov/files/data/fails-deliver-data/cnsfails{year}{month}.zip")
            return urls
    
    def fetch_ftd_data(self, ticker, year=None, half=None):
        """Fetch FTD data for a specific ticker"""
        try:
            # Get security from database
            security = Security.query.filter_by(symbol=ticker).first()
            if not security:
                logger.error(f"Security {ticker} not found in database")
                return None
            
            # Get FTD file URLs
            urls = self._get_ftd_file_urls(year, half)
            
            # Create data sync log
            sync_log = DataSyncLog(
                data_type='ftd_data',
                security_id=security.id,
                start_date=datetime(year, 1 if half == 1 else 7, 1).date(),
                end_date=datetime(year, 6 if half == 1 else 12, 31).date()
            )
            
            records_processed = 0
            records_added = 0
            records_updated = 0
            records_failed = 0
            
            for url in urls:
                try:
                    # Download and process the file
                    headers = {
                        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
                    }
                    response = requests.get(url, headers=headers)
                    self._log_api_call('ftd_data', url, 'GET', None, response)
                    
                    if response.status_code != 200:
                        logger.error(f"Error downloading FTD data from {url}: {response.status_code}")
                        records_failed += 1
                        continue
                    
                    # Save the zip file temporarily - use /tmp for Render.com compatibility
                    import tempfile
                    zip_path = os.path.join(tempfile.gettempdir(), f"ftd_data_{year}_{half}.zip")
                    with open(zip_path, 'wb') as f:
                        f.write(response.content)
                    
                    # Read the CSV file from the zip
                    df = pd.read_csv(zip_path, compression='zip', sep='|')
                    
                    # Filter for the specific ticker
                    df = df[df['SYMBOL'] == ticker]
                    records_processed += len(df)
                    
                    # Process each row
                    for _, row in df.iterrows():
                        try:
                            # Parse date
                            date = datetime.strptime(row['SETTLEMENT DATE'], '%Y%m%d').date()
                            
                            # Check if FTD data already exists for this date
                            ftd_data = FTDData.query.filter_by(
                                security_id=security.id,
                                date=date
                            ).first()
                            
                            # Calculate value
                            quantity = int(row['QUANTITY (FAILS)'])
                            price = float(row['PRICE'])
                            value = quantity * price
                            
                            if ftd_data:
                                # Update existing record
                                ftd_data.quantity = quantity
                                ftd_data.price = price
                                ftd_data.value = value
                                records_updated += 1
                            else:
                                # Create new record
                                ftd_data = FTDData(
                                    security_id=security.id,
                                    date=date,
                                    quantity=quantity,
                                    price=price,
                                    value=value
                                )
                                db.session.add(ftd_data)
                                records_added += 1
                                
                        except Exception as e:
                            logger.error(f"Error processing FTD data for {ticker} on {row['SETTLEMENT DATE']}: {str(e)}")
                            records_failed += 1
                    
                    # Clean up
                    os.remove(zip_path)
                    
                except Exception as e:
                    logger.error(f"Error processing FTD data file {url}: {str(e)}")
                    records_failed += 1
            
            # Update sync log
            sync_log.records_processed = records_processed
            sync_log.records_added = records_added
            sync_log.records_updated = records_updated
            sync_log.records_failed = records_failed
            sync_log.is_success = records_failed == 0
            
            db.session.add(sync_log)
            db.session.commit()
            
            return {
                'security': security,
                'ftd_data': FTDData.query.filter_by(security_id=security.id).all(),
                'sync_log': sync_log
            }
            
        except Exception as e:
            logger.error(f"Error fetching FTD data for {ticker}: {str(e)}")
            db.session.rollback()
            return None
    
    def get_ftd_data(self, ticker, start_date=None, end_date=None):
        """Get FTD data for a ticker from the database"""
        try:
            # Get security from database
            security = Security.query.filter_by(symbol=ticker).first()
            if not security:
                logger.error(f"Security {ticker} not found in database")
                return None
            
            # Query FTD data
            query = FTDData.query.filter_by(security_id=security.id)
            
            if start_date:
                query = query.filter(FTDData.date >= start_date)
            if end_date:
                query = query.filter(FTDData.date <= end_date)
            
            # Order by date
            query = query.order_by(FTDData.date)
            
            return query.all()
            
        except Exception as e:
            logger.error(f"Error getting FTD data for {ticker}: {str(e)}")
            return None

