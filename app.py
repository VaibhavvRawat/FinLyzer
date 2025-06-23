import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px
from datetime import datetime, timedelta
import numpy as np
from stock_analyzer import StockAnalyzer
from news_scraper import NewsScraper
from report_generator import ReportGenerator

st.set_page_config(
    page_title="Financial Analysis Dashboard",
    page_icon="📈",
    layout="wide"
)


if 'analysis_complete' not in st.session_state:
    st.session_state.analysis_complete = False
if 'stock_data' not in st.session_state:
    st.session_state.stock_data = {}
if 'news_data' not in st.session_state:
    st.session_state.news_data = {}

def main():
    st.title("📈 Interactive Financial Analysis Dashboard")
    st.markdown("---")
    
    
    with st.sidebar:
        st.header("Stock Selection")
        
    
        default_stocks = "RELIANCE.NS, TCS.NS, INFY.NS"
        stock_input = st.text_area(
            "Enter stock symbols (comma-separated):",
            value=default_stocks,
            help="Enter stock symbols separated by commas. Examples:\n• Indian: RELIANCE.NS, TCS.NS, INFY.NS\n• US: AAPL, MSFT, GOOGL\n• Or without suffix: RELIANCE, TCS, INFY"
        )
        
        stocks = [stock.strip().upper() for stock in stock_input.split(',') if stock.strip()]
        
        if st.button("Analyze Stocks", type="primary"):
            if stocks:
                analyze_stocks(stocks)
            else:
                st.error("Please enter at least one stock symbol")
    
    
    if st.session_state.analysis_complete:
        display_analysis_results()
    else:
        display_welcome_screen()

def analyze_stocks(stocks):
    """Analyze the selected stocks"""
    try:
      
        stock_analyzer = StockAnalyzer()
        news_scraper = NewsScraper()
        
      
        progress_bar = st.progress(0)
        status_text = st.empty()
        
      
        status_text.text("Fetching stock data and calculating metrics...")
        stock_data = stock_analyzer.analyze_stocks(stocks)
        progress_bar.progress(0.4)
        
        if not stock_data:
            st.error("Failed to fetch stock data. Please check the stock symbols and try again.")
            return
        
      
        status_text.text("Fetching news headlines...")
        news_data = {}
        for i, stock in enumerate(stocks):
            try:
                company_name = stock_data.get(stock, {}).get('company_name', stock)
                headlines = news_scraper.get_stock_news(company_name, stock)
                news_data[stock] = headlines
            except Exception as e:
                st.warning(f"Could not fetch news for {stock}: {str(e)}")
                news_data[stock] = []
            progress_bar.progress(0.4 + (0.4 * (i + 1) / len(stocks)))
        
    
        status_text.text("Calculating correlations...")
        correlation_data = stock_analyzer.calculate_correlations(stock_data)
        progress_bar.progress(0.9)
        
        st.session_state.stock_data = stock_data
        st.session_state.news_data = news_data
        st.session_state.correlation_data = correlation_data
        st.session_state.selected_stocks = stocks
        st.session_state.analysis_complete = True
        
        progress_bar.progress(1.0)
        status_text.text("Analysis complete!")
        
  
        import time
        time.sleep(1)
        progress_bar.empty()
        status_text.empty()
        
        st.rerun()
        
    except Exception as e:
        st.error(f"An error occurred during analysis: {str(e)}")
        st.exception(e)

def display_welcome_screen():
    """Display welcome screen with instructions"""
    st.markdown("""
    ## Welcome to the Financial Analysis Dashboard
    
    This interactive tool provides comprehensive stock analysis without requiring paid API keys:
    
    ### Features:
    - 📊 **Real-time Stock Data**: Current prices and 6-month performance
    - 📈 **Interactive Charts**: Normalized price comparisons and correlation analysis  
    - 📰 **News Headlines**: Latest news for each stock
    - 📋 **Fundamental Ratios**: P/E, Forward P/E, Dividends, Price-to-Book, Debt/Equity, ROE
    - 📄 **Downloadable Reports**: Generate comprehensive markdown reports
    
    ### Getting Started:
    1. Enter stock symbols in the sidebar (comma-separated)
    2. Click "Analyze Stocks" to begin analysis
    3. Explore the interactive charts and data
    4. Download your comprehensive report
    
    ### Example Stock Symbols:
    
    **Indian Stocks (NSE/BSE):**
    - **IT**: TCS.NS, INFY.NS, WIPRO.NS, HCLTECH.NS
    - **Banking**: HDFCBANK.NS, ICICIBANK.NS, SBIN.NS, AXISBANK.NS
    - **Consumer**: RELIANCE.NS, ITC.NS, HINDUNILVR.NS, BRITANNIA.NS
    - **Auto**: MARUTI.NS, TATAMOTORS.NS, BAJAJ-AUTO.NS
    
    **US Stocks:**
    - **Tech**: AAPL, MSFT, GOOGL, NVDA, AMD
    - **Finance**: JPM, BAC, WFC, GS
    - **Consumer**: AMZN, TSLA, META, NFLX
    
    **Note:** You can enter Indian stocks with or without .NS/.BO suffix - the system will automatically detect them.
    """)

def display_analysis_results():
    """Display the analysis results"""
    stocks = st.session_state.selected_stocks
    stock_data = st.session_state.stock_data
    news_data = st.session_state.news_data
    correlation_data = st.session_state.correlation_data
    
    
    tab1, tab2, tab3, tab4, tab5 = st.tabs([
        "📊 Overview", 
        "📈 Charts", 
        "📰 News", 
        "🔗 Correlation", 
        "📄 Report"
    ])
    
    with tab1:
        display_overview_tab(stocks, stock_data)
    
    with tab2:
        display_charts_tab(stocks, stock_data)
    
    with tab3:
        display_news_tab(stocks, news_data)
    
    with tab4:
        display_correlation_tab(correlation_data)
    
    with tab5:
        display_report_tab(stocks, stock_data, news_data, correlation_data)

def display_overview_tab(stocks, stock_data):
    """Display overview of all stocks"""
    st.header("Stock Overview")
    
    
    summary_data = []
    for stock in stocks:
        data = stock_data.get(stock, {})
        if data:
            summary_data.append({
                'Symbol': stock,
                'Company': data.get('company_name', 'N/A'),
                'Current Price': f"{data.get('currency', '₹') if data.get('currency') == 'INR' else '$'}{data.get('current_price', 0):.2f}",
                '6M Change (%)': f"{data.get('six_month_change', 0):.2f}%",
                'P/E Ratio': data.get('pe_ratio', 'N/A'),
                'Forward P/E': data.get('forward_pe', 'N/A'),
                'Dividend Yield': f"{data.get('dividend_yield', 0):.2f}%" if data.get('dividend_yield') else 'N/A'
            })
    
    if summary_data:
        df_summary = pd.DataFrame(summary_data)
        st.dataframe(df_summary, use_container_width=True)
        
    
        st.subheader("Detailed Stock Information")
        for stock in stocks:
            data = stock_data.get(stock, {})
            if data:
                with st.expander(f"{stock} - {data.get('company_name', 'Unknown Company')}"):
                    col1, col2, col3 = st.columns(3)
                    
                    with col1:
                        currency_symbol = "₹" if data.get('currency') == 'INR' else "$"
                        st.metric("Current Price", f"{currency_symbol}{data.get('current_price', 0):.2f}")
                        st.metric("P/E Ratio", data.get('pe_ratio', 'N/A'))
                        st.metric("Price to Book", data.get('price_to_book', 'N/A'))
                    
                    with col2:
                        st.metric("6M Change", f"{data.get('six_month_change', 0):.2f}%")
                        st.metric("Forward P/E", data.get('forward_pe', 'N/A'))
                        st.metric("Debt/Equity", data.get('debt_to_equity', 'N/A'))
                    
                    with col3:
                        st.metric("Dividend Yield", f"{data.get('dividend_yield', 0):.2f}%" if data.get('dividend_yield') else 'N/A')
                        st.metric("ROE", f"{data.get('roe', 0):.2f}%" if data.get('roe') else 'N/A')

def display_charts_tab(stocks, stock_data):
    """Display interactive charts"""
    st.header("Interactive Charts")
    
    
    st.subheader("Normalized Price Comparison (6 Months)")
    
    try:
        
        fig = go.Figure()
        
        for stock in stocks:
            data = stock_data.get(stock, {})
            if data and 'price_history' in data:
                prices = data['price_history']
                if len(prices) > 0:
                    normalized_prices = (prices / prices.iloc[0] * 100)
                    fig.add_trace(go.Scatter(
                        x=prices.index,
                        y=normalized_prices,
                        mode='lines',
                        name=f"{stock} ({data.get('company_name', stock)})",
                        line=dict(width=2)
                    ))
        
        fig.update_layout(
            title="Normalized Stock Price Performance (Starting at 100)",
            xaxis_title="Date",
            yaxis_title="Normalized Price",
            height=500,
            hovermode='x unified'
        )
        
        st.plotly_chart(fig, use_container_width=True)
        
    except Exception as e:
        st.error(f"Error creating price chart: {str(e)}")
    
    
    st.subheader("6-Month Performance Comparison")
    
    try:
        performance_data = []
        for stock in stocks:
            data = stock_data.get(stock, {})
            if data:
                performance_data.append({
                    'Stock': f"{stock}\n({data.get('company_name', stock)})",
                    'Performance (%)': data.get('six_month_change', 0)
                })
        
        if performance_data:
            df_perf = pd.DataFrame(performance_data)
            fig_bar = px.bar(
                df_perf, 
                x='Stock', 
                y='Performance (%)',
                title="6-Month Performance Comparison",
                color='Performance (%)',
                color_continuous_scale=['red', 'yellow', 'green']
            )
            fig_bar.update_layout(height=400)
            st.plotly_chart(fig_bar, use_container_width=True)
            
    except Exception as e:
        st.error(f"Error creating performance chart: {str(e)}")

def display_news_tab(stocks, news_data):
    """Display news headlines for each stock"""
    st.header("Latest News Headlines")
    
    for stock in stocks:
        headlines = news_data.get(stock, [])
        stock_info = st.session_state.stock_data.get(stock, {})
        company_name = stock_info.get('company_name', stock)
        
        st.subheader(f"{stock} - {company_name}")
        
        if headlines:
            for i, headline in enumerate(headlines[:10], 1):  
                st.write(f"{i}. {headline}")
        else:
            st.info(f"No news headlines found for {stock}")
        
        st.markdown("---")

def display_correlation_tab(correlation_data):
    """Display correlation analysis"""
    st.header("Stock Correlation Analysis")
    
    if correlation_data is not None and not correlation_data.empty:
    
        fig_corr = px.imshow(
            correlation_data,
            text_auto=True,
            aspect="auto",
            title="Stock Price Correlation Matrix",
            color_continuous_scale="RdBu_r"
        )
        fig_corr.update_layout(height=500)
        st.plotly_chart(fig_corr, use_container_width=True)
        
    
        st.subheader("Correlation Analysis")
        st.markdown("""
        **Correlation Interpretation:**
        - **1.0**: Perfect positive correlation
        - **0.7 to 0.9**: Strong positive correlation
        - **0.3 to 0.7**: Moderate positive correlation
        - **-0.3 to 0.3**: Weak correlation
        - **-0.7 to -0.3**: Moderate negative correlation
        - **-0.9 to -0.7**: Strong negative correlation
        - **-1.0**: Perfect negative correlation
        """)
        
    
        st.subheader("Correlation Values")
        st.dataframe(correlation_data, use_container_width=True)
        
    else:
        st.info("Correlation data not available. Please ensure stock data was fetched successfully.")

def display_report_tab(stocks, stock_data, news_data, correlation_data):
    """Display and generate downloadable report"""
    st.header("Financial Report")
    
    
    report_generator = ReportGenerator()
    report_content = report_generator.generate_report(stocks, stock_data, news_data, correlation_data)
    
    
    st.subheader("Report Preview")
    st.markdown(report_content)
    
  
    st.subheader("Download Report")
    current_date = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"financial_report_{current_date}.md"
    
    st.download_button(
        label="📄 Download Report as Markdown",
        data=report_content,
        file_name=filename,
        mime="text/markdown"
    )

if __name__ == "__main__":
    main()
