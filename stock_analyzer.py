import yfinance as yf
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import warnings
import time
warnings.filterwarnings('ignore')

class StockAnalyzer:
    def __init__(self):
        self.six_months_ago = datetime.now() - timedelta(days=180)
        # Indian stock suffix mapping
        self.indian_suffixes = {
            'NSE': '.NS',  # National Stock Exchange
            'BSE': '.BO'   # Bombay Stock Exchange
        }
    
    def _normalize_symbol(self, symbol):
        """Normalize stock symbol for different markets"""
        symbol = symbol.upper().strip()
        
        # If symbol already has a suffix, return as is
        if '.' in symbol:
            return symbol
            
        # Check if it's likely an Indian stock (common Indian stock patterns)
        indian_patterns = ['RELIANCE', 'TCS', 'INFY', 'HDFCBANK', 'ICICIBANK', 'SBIN', 'ITC', 'HINDUNILVR', 'BHARTIARTL', 'KOTAKBANK', 'LT', 'ASIANPAINT', 'MARUTI', 'TITAN', 'NESTLEIND', 'ULTRACEMCO', 'POWERGRID', 'NTPC', 'ONGC', 'COALINDIA', 'WIPRO', 'TECHM', 'HCLTECH', 'DRREDDY', 'SUNPHARMA', 'CIPLA', 'DIVISLAB', 'BAJFINANCE', 'BAJAJFINSV', 'AXISBANK', 'INDUSINDBK', 'TATAMOTORS', 'TATASTEEL', 'JSWSTEEL', 'HINDALCO', 'ADANIPORTS', 'ADANIENT', 'GRASIM', 'BRITANNIA', 'HEROMOTOCO', 'BAJAJ-AUTO', 'EICHERMOT', 'BPCL', 'IOC', 'SHREECEM', 'AMBUJACEM', 'ACC', 'VEDL', 'SAIL', 'NMDC', 'JINDALSTEL', 'TATACHEM', 'UPL', 'PIDILITIND', 'DMART', 'GODREJCP', 'MARICO', 'DABUR', 'COLPAL', 'PGHH', 'MCDOWELL-N', 'UBL', 'APOLLOHOSP', 'FORTIS', 'LUPIN', 'BIOCON', 'CADILAHC', 'AUROPHARMA', 'TORNTPHARM', 'ALKEM', 'CONCOR', 'SIEMENS', 'ABB', 'BHEL', 'CROMPTON', 'HAVELLS', 'VOLTAS', 'BLUESTAR', 'CUMMINSIND', 'BOSCHLTD', 'MOTHERSUMI', 'AMARAJABAT', 'EXIDEIND', 'MFSL', 'SRTRANSFIN', 'CHOLAFIN', 'PFC', 'RECLTD', 'IRCTC', 'CONCOR', 'FINOPB', 'INOXGREEN']
        
        # Try to detect Indian stocks by pattern matching
        if any(pattern in symbol for pattern in indian_patterns) or len(symbol) > 6:
            # Try NSE first, then BSE as fallback
            return symbol + '.NS'
        
        # Default to US market (no suffix needed)
        return symbol

    def get_stock_info(self, symbol):
        """Get comprehensive stock information"""
        try:
            # Normalize symbol for different markets
            normalized_symbol = self._normalize_symbol(symbol)
            
            # Try with normalized symbol first
            ticker = yf.Ticker(normalized_symbol)
            info = ticker.info
            
            # Get historical data for 6 months
            hist_data = ticker.history(start=self.six_months_ago, end=datetime.now())
            
            # If no data found and it's an Indian stock, try BSE
            if hist_data.empty and normalized_symbol.endswith('.NS'):
                time.sleep(1)  # Rate limiting
                bse_symbol = symbol + '.BO'
                ticker = yf.Ticker(bse_symbol)
                info = ticker.info
                hist_data = ticker.history(start=self.six_months_ago, end=datetime.now())
                normalized_symbol = bse_symbol
            
            # If still no data and no suffix, try adding common Indian suffixes
            if hist_data.empty and '.' not in normalized_symbol:
                for suffix in ['.NS', '.BO']:
                    time.sleep(1)  # Rate limiting
                    try_symbol = symbol + suffix
                    ticker = yf.Ticker(try_symbol)
                    info = ticker.info
                    hist_data = ticker.history(start=self.six_months_ago, end=datetime.now())
                    if not hist_data.empty:
                        normalized_symbol = try_symbol
                        break
            
            if hist_data.empty:
                print(f"No historical data found for {symbol}")
                return None
            
            # Calculate 6-month performance
            if len(hist_data) > 1:
                six_month_change = ((hist_data['Close'].iloc[-1] - hist_data['Close'].iloc[0]) / hist_data['Close'].iloc[0]) * 100
            else:
                six_month_change = 0
            
            # Extract key metrics with better error handling
            current_price = info.get('currentPrice')
            if current_price is None or current_price == 0:
                current_price = hist_data['Close'].iloc[-1] if not hist_data.empty else 0
            
            # Get company name with fallbacks
            company_name = info.get('longName') or info.get('shortName') or symbol
            
            # Extract financial metrics with proper handling
            stock_data = {
                'symbol': symbol,
                'normalized_symbol': normalized_symbol,
                'company_name': company_name,
                'current_price': float(current_price) if current_price else 0,
                'six_month_change': six_month_change,
                'pe_ratio': info.get('trailingPE', 'N/A'),
                'forward_pe': info.get('forwardPE', 'N/A'),
                'dividend_yield': info.get('dividendYield', 0) * 100 if info.get('dividendYield') else None,
                'price_to_book': info.get('priceToBook', 'N/A'),
                'debt_to_equity': info.get('debtToEquity', 'N/A'),
                'roe': info.get('returnOnEquity', 0) * 100 if info.get('returnOnEquity') else None,
                'market_cap': info.get('marketCap', 'N/A'),
                'volume': info.get('volume', hist_data['Volume'].iloc[-1] if not hist_data.empty else 'N/A'),
                'price_history': hist_data['Close'],
                'currency': info.get('currency', 'USD'),
                'exchange': info.get('exchange', 'Unknown')
            }
            
            return stock_data
            
        except Exception as e:
            print(f"Error fetching data for {symbol}: {str(e)}")
            return None
    
    def analyze_stocks(self, symbols):
        """Analyze multiple stocks"""
        results = {}
        
        for symbol in symbols:
            print(f"Analyzing {symbol}...")
            stock_data = self.get_stock_info(symbol)
            if stock_data:
                results[symbol] = stock_data
            else:
                print(f"Failed to get data for {symbol}")
        
        return results
    
    def calculate_correlations(self, stock_data):
        """Calculate correlation matrix between stocks"""
        try:
            # Create DataFrame with price histories
            price_data = {}
            
            for symbol, data in stock_data.items():
                if 'price_history' in data and not data['price_history'].empty:
                    price_data[symbol] = data['price_history']
            
            if len(price_data) < 2:
                return None
            
            # Align all price series to same dates
            df_prices = pd.DataFrame(price_data)
            df_prices = df_prices.dropna()
            
            if df_prices.empty:
                return None
            
            # Calculate correlation matrix
            correlation_matrix = df_prices.corr()
            
            return correlation_matrix
            
        except Exception as e:
            print(f"Error calculating correlations: {str(e)}")
            return None
    
    def format_metric(self, value, is_percentage=False, decimal_places=2):
        """Format metric values for display"""
        if value is None or value == 'N/A':
            return 'N/A'
        
        try:
            if isinstance(value, (int, float)):
                if is_percentage:
                    return f"{value:.{decimal_places}f}%"
                else:
                    return f"{value:.{decimal_places}f}"
            else:
                return str(value)
        except:
            return 'N/A'
    
    def get_performance_summary(self, stock_data):
        """Generate a performance summary"""
        summary = {}
        
        for symbol, data in stock_data.items():
            summary[symbol] = {
                'company': data.get('company_name', symbol),
                'price': data.get('current_price', 0),
                'change': data.get('six_month_change', 0),
                'pe_ratio': data.get('pe_ratio', 'N/A')
            }
        
        return summary
