# Financial Analysis Dashboard

## Overview
Interactive Streamlit application for comprehensive stock analysis supporting both Indian (NSE/BSE) and US markets.
 https://finlyzer.streamlit.app/

## Features
- Real-time stock data from Yahoo Finance (no API keys required)
- Multi-source news scraping
- Interactive charts and correlation analysis  
- Downloadable markdown reports
- Support for Indian and US stocks

## Setup Instructions

1. **Install Python 3.11+**

2. **Install dependencies:**
   ```bash
   pip install streamlit yfinance plotly beautifulsoup4 requests pandas numpy curl-cffi trafilatura
   ```

   **OR**

   ```bash
   pip install -r requirements.txt
   ```


3. **Create .streamlit directory and config.toml:**
   ```bash
   mkdir .streamlit
   ```
   
   Add the config.toml file provided in the package.

4. **Run the application:**

   ```bash
   streamlit run app.py --server.port 5000
   ```

   **OR**

   ```bash
   streamlit run app.py --server.port 8501 --server.address localhost
   ```


## Usage Examples

### Indian Stocks
- RELIANCE.NS, TCS.NS, INFY.NS
- HDFCBANK.NS, ICICIBANK.NS, SBIN.NS
- Or without suffix: RELIANCE, TCS, INFY (auto-detected)

### US Stocks  
- AAPL, MSFT, GOOGL, NVDA, AMD
- TSLA, META, AMZN, NFLX

## File Structure
- `app.py` - Main Streamlit application
- `stock_analyzer.py` - Stock data retrieval and analysis
- `news_scraper.py` - Multi-source news headline scraping
- `report_generator.py` - Comprehensive report generation
- `.streamlit/config.toml` - Streamlit configuration
- `pyproject.toml` - Python dependencies

## Notes
- No API keys required - uses free data sources
- Supports automatic market detection for Indian stocks
- Rate limiting implemented to prevent blocking
- Comprehensive error handling and fallback mechanisms

## Author
Created by Vaibhav Rawat

