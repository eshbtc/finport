import numpy as np
import pandas as pd
import logging
from datetime import datetime, timedelta
from ..models import db, Security, PriceData, FTDData, SwapCycle, VolatilityCycle, MarketCorrelation, TechnicalIndicator

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class AnalyticsService:
    """Service for performing financial analytics"""
    
    def __init__(self):
        """Initialize the analytics service"""
        pass
    
    def _get_price_data_df(self, security_id, start_date=None, end_date=None):
        """Get price data as a pandas DataFrame"""
        try:
            # Query price data
            query = PriceData.query.filter_by(security_id=security_id)
            
            if start_date:
                query = query.filter(PriceData.date >= start_date)
            if end_date:
                query = query.filter(PriceData.date <= end_date)
            
            # Order by date
            query = query.order_by(PriceData.date)
            
            # Convert to DataFrame
            price_data = query.all()
            if not price_data:
                return None
            
            df = pd.DataFrame([{
                'date': p.date,
                'open': p.open,
                'high': p.high,
                'low': p.low,
                'close': p.close,
                'volume': p.volume,
                'vwap': p.vwap
            } for p in price_data])
            
            # Set date as index
            df['date'] = pd.to_datetime(df['date'])
            df.set_index('date', inplace=True)
            
            return df
            
        except Exception as e:
            logger.error(f"Error getting price data DataFrame: {str(e)}")
            return None
    
    def calculate_technical_indicators(self, ticker, start_date=None, end_date=None):
        """Calculate technical indicators for a security"""
        try:
            # Get security from database
            security = Security.query.filter_by(symbol=ticker).first()
            if not security:
                logger.error(f"Security {ticker} not found in database")
                return None
            
            # Get price data as DataFrame
            df = self._get_price_data_df(security.id, start_date, end_date)
            if df is None or df.empty:
                logger.error(f"No price data found for {ticker}")
                return None
            
            # Calculate indicators
            indicators = {}
            
            # Moving Averages
            for period in [20, 50, 200]:
                df[f'sma_{period}'] = df['close'].rolling(window=period).mean()
                indicators[f'sma_{period}'] = df[f'sma_{period}'].dropna().to_dict()
            
            # Exponential Moving Averages
            for period in [12, 26]:
                df[f'ema_{period}'] = df['close'].ewm(span=period, adjust=False).mean()
                indicators[f'ema_{period}'] = df[f'ema_{period}'].dropna().to_dict()
            
            # MACD
            df['macd'] = df['ema_12'] - df['ema_26']
            df['macd_signal'] = df['macd'].ewm(span=9, adjust=False).mean()
            df['macd_histogram'] = df['macd'] - df['macd_signal']
            indicators['macd'] = df['macd'].dropna().to_dict()
            indicators['macd_signal'] = df['macd_signal'].dropna().to_dict()
            indicators['macd_histogram'] = df['macd_histogram'].dropna().to_dict()
            
            # RSI
            delta = df['close'].diff()
            gain = delta.where(delta > 0, 0)
            loss = -delta.where(delta < 0, 0)
            avg_gain = gain.rolling(window=14).mean()
            avg_loss = loss.rolling(window=14).mean()
            rs = avg_gain / avg_loss
            df['rsi'] = 100 - (100 / (1 + rs))
            indicators['rsi'] = df['rsi'].dropna().to_dict()
            
            # Bollinger Bands
            df['bb_middle'] = df['close'].rolling(window=20).mean()
            df['bb_std'] = df['close'].rolling(window=20).std()
            df['bb_upper'] = df['bb_middle'] + (df['bb_std'] * 2)
            df['bb_lower'] = df['bb_middle'] - (df['bb_std'] * 2)
            indicators['bb_upper'] = df['bb_upper'].dropna().to_dict()
            indicators['bb_middle'] = df['bb_middle'].dropna().to_dict()
            indicators['bb_lower'] = df['bb_lower'].dropna().to_dict()
            
            # Store indicators in database
            self._store_technical_indicators(security.id, df)
            
            return {
                'security': security,
                'indicators': indicators
            }
            
        except Exception as e:
            logger.error(f"Error calculating technical indicators for {ticker}: {str(e)}")
            return None
    
    def _store_technical_indicators(self, security_id, df):
        """Store technical indicators in the database"""
        try:
            # Get list of dates
            dates = df.index.date
            
            # Indicators to store
            indicators = {
                'sma_20': df['sma_20'].values if 'sma_20' in df else None,
                'sma_50': df['sma_50'].values if 'sma_50' in df else None,
                'sma_200': df['sma_200'].values if 'sma_200' in df else None,
                'ema_12': df['ema_12'].values if 'ema_12' in df else None,
                'ema_26': df['ema_26'].values if 'ema_26' in df else None,
                'macd': df['macd'].values if 'macd' in df else None,
                'macd_signal': df['macd_signal'].values if 'macd_signal' in df else None,
                'macd_histogram': df['macd_histogram'].values if 'macd_histogram' in df else None,
                'rsi': df['rsi'].values if 'rsi' in df else None,
                'bb_upper': df['bb_upper'].values if 'bb_upper' in df else None,
                'bb_middle': df['bb_middle'].values if 'bb_middle' in df else None,
                'bb_lower': df['bb_lower'].values if 'bb_lower' in df else None
            }
            
            # Store each indicator for each date
            for i, date in enumerate(dates):
                for indicator_name, values in indicators.items():
                    if values is not None and i < len(values) and not np.isnan(values[i]):
                        # Check if indicator already exists
                        indicator = TechnicalIndicator.query.filter_by(
                            security_id=security_id,
                            date=date,
                            indicator_name=indicator_name,
                            timeframe='1d'
                        ).first()
                        
                        # Determine signal
                        signal = None
                        if indicator_name == 'rsi':
                            if values[i] > 70:
                                signal = 'sell'
                            elif values[i] < 30:
                                signal = 'buy'
                            else:
                                signal = 'hold'
                        elif indicator_name == 'macd_histogram':
                            if i > 0 and values[i-1] < 0 and values[i] > 0:
                                signal = 'buy'
                            elif i > 0 and values[i-1] > 0 and values[i] < 0:
                                signal = 'sell'
                            else:
                                signal = 'hold'
                        
                        if indicator:
                            # Update existing indicator
                            indicator.indicator_value = float(values[i])
                            indicator.indicator_signal = signal
                        else:
                            # Create new indicator
                            indicator = TechnicalIndicator(
                                security_id=security_id,
                                date=date,
                                indicator_name=indicator_name,
                                indicator_value=float(values[i]),
                                indicator_signal=signal,
                                timeframe='1d'
                            )
                            db.session.add(indicator)
            
            db.session.commit()
            
        except Exception as e:
            logger.error(f"Error storing technical indicators: {str(e)}")
            db.session.rollback()
    
    def analyze_swap_cycles(self, ticker, lookback_days=365):
        """Analyze swap cycles for a security"""
        try:
            # Get security from database
            security = Security.query.filter_by(symbol=ticker).first()
            if not security:
                logger.error(f"Security {ticker} not found in database")
                return None
            
            # Calculate start date
            end_date = datetime.now().date()
            start_date = end_date - timedelta(days=lookback_days)
            
            # Get price data as DataFrame
            df = self._get_price_data_df(security.id, start_date, end_date)
            if df is None or df.empty:
                logger.error(f"No price data found for {ticker}")
                return None
            
            # Get FTD data
            ftd_query = FTDData.query.filter_by(security_id=security.id)
            ftd_query = ftd_query.filter(FTDData.date >= start_date)
            ftd_query = ftd_query.filter(FTDData.date <= end_date)
            ftd_query = ftd_query.order_by(FTDData.date)
            ftd_data = ftd_query.all()
            
            # Create FTD DataFrame
            if ftd_data:
                ftd_df = pd.DataFrame([{
                    'date': f.date,
                    'quantity': f.quantity,
                    'price': f.price,
                    'value': f.value
                } for f in ftd_data])
                ftd_df['date'] = pd.to_datetime(ftd_df['date'])
                ftd_df.set_index('date', inplace=True)
                
                # Merge with price data
                df = df.join(ftd_df, how='left')
                df['quantity'] = df['quantity'].fillna(0)
                df['value'] = df['value'].fillna(0)
            else:
                df['quantity'] = 0
                df['value'] = 0
            
            # Calculate volatility
            df['returns'] = df['close'].pct_change()
            df['volatility'] = df['returns'].rolling(window=20).std() * np.sqrt(252)  # Annualized
            
            # Identify potential cycle peaks and troughs
            df['rolling_max'] = df['close'].rolling(window=20).max()
            df['rolling_min'] = df['close'].rolling(window=20).min()
            df['is_peak'] = (df['close'] == df['rolling_max']) & (df['close'].shift(1) < df['close']) & (df['close'].shift(-1) < df['close'])
            df['is_trough'] = (df['close'] == df['rolling_min']) & (df['close'].shift(1) > df['close']) & (df['close'].shift(-1) > df['close'])
            
            # Identify cycles
            cycles = []
            current_cycle = None
            
            for date, row in df.iterrows():
                if row['is_trough'] and current_cycle is None:
                    # Start of a new cycle
                    current_cycle = {
                        'start_date': date.date(),
                        'start_price': row['close'],
                        'ftd_start': row['quantity']
                    }
                elif row['is_peak'] and current_cycle is not None:
                    # Peak of the cycle
                    current_cycle['peak_date'] = date.date()
                    current_cycle['peak_price'] = row['close']
                    current_cycle['ftd_peak'] = row['quantity']
                elif row['is_trough'] and current_cycle is not None and 'peak_date' in current_cycle:
                    # End of the cycle
                    current_cycle['end_date'] = date.date()
                    current_cycle['end_price'] = row['close']
                    current_cycle['ftd_end'] = row['quantity']
                    current_cycle['duration'] = (current_cycle['end_date'] - current_cycle['start_date']).days
                    current_cycle['return'] = (current_cycle['peak_price'] / current_cycle['start_price']) - 1
                    current_cycle['drawdown'] = (current_cycle['end_price'] / current_cycle['peak_price']) - 1
                    
                    # Calculate volatility for the cycle
                    cycle_df = df.loc[(df.index >= pd.Timestamp(current_cycle['start_date'])) & 
                                     (df.index <= pd.Timestamp(current_cycle['end_date']))]
                    current_cycle['volatility'] = cycle_df['volatility'].mean()
                    
                    # Calculate FTD correlation
                    if 'quantity' in cycle_df.columns:
                        current_cycle['ftd_correlation'] = cycle_df['close'].corr(cycle_df['quantity'])
                    else:
                        current_cycle['ftd_correlation'] = None
                    
                    cycles.append(current_cycle)
                    current_cycle = {
                        'start_date': date.date(),
                        'start_price': row['close'],
                        'ftd_start': row['quantity']
                    }
            
            # Store cycles in database
            self._store_swap_cycles(security.id, cycles)
            
            return {
                'security': security,
                'cycles': cycles,
                'price_data': df.reset_index().to_dict('records')
            }
            
        except Exception as e:
            logger.error(f"Error analyzing swap cycles for {ticker}: {str(e)}")
            return None
    
    def _store_swap_cycles(self, security_id, cycles):
        """Store swap cycles in the database"""
        try:
            # Clear existing active cycles
            SwapCycle.query.filter_by(security_id=security_id, is_active=True).update({'is_active': False})
            
            # Store new cycles
            for i, cycle in enumerate(cycles):
                # Check if cycle already exists
                existing_cycle = SwapCycle.query.filter_by(
                    security_id=security_id,
                    start_date=cycle['start_date'],
                    end_date=cycle['end_date']
                ).first()
                
                if existing_cycle:
                    # Update existing cycle
                    existing_cycle.peak_price = cycle.get('peak_price')
                    existing_cycle.trough_price = cycle.get('end_price')
                    existing_cycle.volatility_score = cycle.get('volatility')
                    existing_cycle.is_active = True
                    existing_cycle.updated_at = datetime.utcnow()
                else:
                    # Create new cycle
                    new_cycle = SwapCycle(
                        security_id=security_id,
                        cycle_type='quarterly',
                        cycle_number=i + 1,
                        start_date=cycle['start_date'],
                        end_date=cycle['end_date'],
                        peak_price=cycle.get('peak_price'),
                        trough_price=cycle.get('end_price'),
                        volatility_score=cycle.get('volatility'),
                        confidence_score=0.7,  # Default confidence
                        is_active=True
                    )
                    db.session.add(new_cycle)
            
            db.session.commit()
            
        except Exception as e:
            logger.error(f"Error storing swap cycles: {str(e)}")
            db.session.rollback()
    
    def analyze_volatility_cycles(self, ticker, lookback_days=365):
        """Analyze volatility cycles for a security"""
        try:
            # Get security from database
            security = Security.query.filter_by(symbol=ticker).first()
            if not security:
                logger.error(f"Security {ticker} not found in database")
                return None
            
            # Calculate start date
            end_date = datetime.now().date()
            start_date = end_date - timedelta(days=lookback_days)
            
            # Get price data as DataFrame
            df = self._get_price_data_df(security.id, start_date, end_date)
            if df is None or df.empty:
                logger.error(f"No price data found for {ticker}")
                return None
            
            # Calculate returns and volatility
            df['returns'] = df['close'].pct_change()
            df['volatility'] = df['returns'].rolling(window=20).std() * np.sqrt(252)  # Annualized
            
            # Calculate historical volatility percentiles
            df['volatility_rank'] = df['volatility'].rank(pct=True)
            
            # Define volatility regimes
            df['volatility_regime'] = 'medium'
            df.loc[df['volatility_rank'] <= 0.25, 'volatility_regime'] = 'low'
            df.loc[df['volatility_rank'] >= 0.75, 'volatility_regime'] = 'high'
            
            # Identify cycle phases
            df['price_sma'] = df['close'].rolling(window=50).mean()
            df['price_above_sma'] = df['close'] > df['price_sma']
            
            # Define cycle phases
            df['cycle_phase'] = 'unknown'
            df.loc[(df['price_above_sma']) & (df['volatility_regime'] == 'low'), 'cycle_phase'] = 'accumulation'
            df.loc[(df['price_above_sma']) & (df['volatility_regime'] == 'medium'), 'cycle_phase'] = 'markup'
            df.loc[(df['price_above_sma']) & (df['volatility_regime'] == 'high'), 'cycle_phase'] = 'distribution'
            df.loc[(~df['price_above_sma']) & (df['volatility_regime'].isin(['medium', 'high'])), 'cycle_phase'] = 'markdown'
            
            # Get VIX data if available (placeholder for now)
            df['vix_correlation'] = 0.0
            
            # Store volatility cycles in database
            self._store_volatility_cycles(security.id, df)
            
            return {
                'security': security,
                'volatility_data': df.reset_index().to_dict('records')
            }
            
        except Exception as e:
            logger.error(f"Error analyzing volatility cycles for {ticker}: {str(e)}")
            return None
    
    def _store_volatility_cycles(self, security_id, df):
        """Store volatility cycles in the database"""
        try:
            # Process each date
            for date, row in df.iterrows():
                if pd.isna(row['volatility']) or pd.isna(row['cycle_phase']):
                    continue
                
                # Check if cycle already exists
                cycle = VolatilityCycle.query.filter_by(
                    security_id=security_id,
                    date=date.date()
                ).first()
                
                if cycle:
                    # Update existing cycle
                    cycle.cycle_phase = row['cycle_phase']
                    cycle.volatility_regime = row['volatility_regime']
                    cycle.realized_volatility = row['volatility']
                    cycle.volatility_rank = row['volatility_rank']
                    cycle.vix_correlation = row['vix_correlation']
                else:
                    # Create new cycle
                    cycle = VolatilityCycle(
                        security_id=security_id,
                        date=date.date(),
                        cycle_phase=row['cycle_phase'],
                        volatility_regime=row['volatility_regime'],
                        realized_volatility=row['volatility'],
                        volatility_rank=row['volatility_rank'],
                        volatility_percentile=row['volatility_rank'],
                        vix_correlation=row['vix_correlation']
                    )
                    db.session.add(cycle)
            
            db.session.commit()
            
        except Exception as e:
            logger.error(f"Error storing volatility cycles: {str(e)}")
            db.session.rollback()
    
    def calculate_market_correlations(self, ticker, comparison_tickers, lookback_days=90):
        """Calculate market correlations between a security and other securities"""
        try:
            # Get security from database
            security = Security.query.filter_by(symbol=ticker).first()
            if not security:
                logger.error(f"Security {ticker} not found in database")
                return None
            
            # Calculate start date
            end_date = datetime.now().date()
            start_date = end_date - timedelta(days=lookback_days)
            
            # Get price data for main security
            main_df = self._get_price_data_df(security.id, start_date, end_date)
            if main_df is None or main_df.empty:
                logger.error(f"No price data found for {ticker}")
                return None
            
            correlations = []
            
            for comp_ticker in comparison_tickers:
                # Get comparison security
                comp_security = Security.query.filter_by(symbol=comp_ticker).first()
                if not comp_security:
                    logger.warning(f"Comparison security {comp_ticker} not found in database")
                    continue
                
                # Get price data for comparison security
                comp_df = self._get_price_data_df(comp_security.id, start_date, end_date)
                if comp_df is None or comp_df.empty:
                    logger.warning(f"No price data found for {comp_ticker}")
                    continue
                
                # Merge dataframes
                merged_df = pd.DataFrame({
                    'main_close': main_df['close'],
                    'comp_close': comp_df['close']
                })
                
                # Calculate returns
                merged_df['main_returns'] = merged_df['main_close'].pct_change()
                merged_df['comp_returns'] = merged_df['comp_close'].pct_change()
                
                # Drop NaN values
                merged_df = merged_df.dropna()
                
                if len(merged_df) < 10:
                    logger.warning(f"Not enough data points for correlation between {ticker} and {comp_ticker}")
                    continue
                
                # Calculate correlation
                correlation = merged_df['main_returns'].corr(merged_df['comp_returns'])
                
                # Calculate beta
                cov = merged_df['main_returns'].cov(merged_df['comp_returns'])
                var = merged_df['comp_returns'].var()
                beta = cov / var if var != 0 else 0
                
                # Calculate R-squared
                r_squared = correlation ** 2
                
                # Store correlation in database
                self._store_market_correlation(security.id, comp_security.id, end_date, lookback_days, correlation, beta, r_squared)
                
                correlations.append({
                    'ticker': comp_ticker,
                    'correlation': correlation,
                    'beta': beta,
                    'r_squared': r_squared
                })
            
            return {
                'security': security,
                'correlations': correlations
            }
            
        except Exception as e:
            logger.error(f"Error calculating market correlations for {ticker}: {str(e)}")
            return None
    
    def _store_market_correlation(self, security_id, comp_security_id, date, period, correlation, beta, r_squared):
        """Store market correlation in the database"""
        try:
            # Check if correlation already exists
            corr = MarketCorrelation.query.filter_by(
                security_id=security_id,
                correlated_security_id=comp_security_id,
                date=date,
                correlation_period=period
            ).first()
            
            if corr:
                # Update existing correlation
                corr.correlation_coefficient = correlation
                corr.beta = beta
                corr.r_squared = r_squared
            else:
                # Create new correlation
                corr = MarketCorrelation(
                    security_id=security_id,
                    correlated_security_id=comp_security_id,
                    date=date,
                    correlation_period=period,
                    correlation_coefficient=correlation,
                    beta=beta,
                    r_squared=r_squared
                )
                db.session.add(corr)
            
            db.session.commit()
            
        except Exception as e:
            logger.error(f"Error storing market correlation: {str(e)}")
            db.session.rollback()

