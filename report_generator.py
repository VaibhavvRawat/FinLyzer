from datetime import datetime
import pandas as pd

class ReportGenerator:
    def __init__(self):
        self.current_date = datetime.now().strftime("%Y-%m-%d")
    
    def generate_report(self, stocks, stock_data, news_data, correlation_data):
        """Generate a comprehensive financial report in markdown format"""
        
        report = f"""# Financial Analysis Report
**Generated on:** {self.current_date}

## Executive Summary

This report provides a comprehensive analysis of the following stocks: {', '.join(stocks)}. 
The analysis includes current stock prices, 6-month performance, fundamental ratios, 
correlation analysis, and recent news headlines.

## Stock Overview

{self._generate_stock_overview_section(stocks, stock_data)}

## Performance Analysis

{self._generate_performance_section(stocks, stock_data)}

## Fundamental Ratios Comparison

{self._generate_fundamentals_table(stocks, stock_data)}

### Ratio Descriptions

{self._generate_ratio_descriptions()}

## Correlation Analysis

{self._generate_correlation_section(correlation_data)}

## News Analysis

{self._generate_news_section(stocks, news_data, stock_data)}

## Risk Assessment and Future Scenarios

{self._generate_risk_assessment(stocks, stock_data, correlation_data)}

## Conclusion

{self._generate_conclusion(stocks, stock_data)}

---
*This report was generated using real-time data from Yahoo Finance and news sources. 
Data accuracy is subject to market conditions and source reliability.*
"""
        return report
    
    def _generate_stock_overview_section(self, stocks, stock_data):
        """Generate stock overview section"""
        overview = ""
        
        for stock in stocks:
            data = stock_data.get(stock, {})
            if not data:
                continue
                
            company_name = data.get('company_name', stock)
            current_price = data.get('current_price', 0)
            six_month_change = data.get('six_month_change', 0)
            
            currency_symbol = "₹" if data.get('currency') == 'INR' else "$"
            exchange_info = f" ({data.get('exchange', 'Unknown')})" if data.get('exchange') != 'Unknown' else ""
            
            overview += f"""
### {stock} - {company_name}{exchange_info}

- **Current Price:** {currency_symbol}{current_price:.2f}
- **6-Month Performance:** {six_month_change:.2f}%
- **Market Cap:** {self._format_large_number(data.get('market_cap', 'N/A'))}
- **Trading Volume:** {self._format_large_number(data.get('volume', 'N/A'))}
"""
        
        return overview
    
    def _generate_performance_section(self, stocks, stock_data):
        """Generate performance analysis section"""
        performance_data = []
        
        for stock in stocks:
            data = stock_data.get(stock, {})
            if data:
                performance_data.append({
                    'Stock': stock,
                    'Company': data.get('company_name', stock),
                    '6M Change (%)': f"{data.get('six_month_change', 0):.2f}%"
                })
        
        if not performance_data:
            return "Performance data not available."
        
        # Find best and worst performers
        best_performer = max(performance_data, key=lambda x: float(x['6M Change (%)'].rstrip('%')))
        worst_performer = min(performance_data, key=lambda x: float(x['6M Change (%)'].rstrip('%')))
        
        section = f"""
Over the past 6 months, the analyzed stocks have shown varying performance:

- **Best Performer:** {best_performer['Stock']} ({best_performer['Company']}) with {best_performer['6M Change (%)']} change
- **Worst Performer:** {worst_performer['Stock']} ({worst_performer['Company']}) with {worst_performer['6M Change (%)']} change

### Performance Summary
"""
        
        for data in performance_data:
            change_val = float(data['6M Change (%)'].rstrip('%'))
            trend = "📈" if change_val > 0 else "📉" if change_val < 0 else "➡️"
            section += f"- {trend} **{data['Stock']}:** {data['6M Change (%)']}\n"
        
        return section
    
    def _generate_fundamentals_table(self, stocks, stock_data):
        """Generate fundamentals comparison table"""
        table = "| Stock | P/E Ratio | Forward P/E | Dividend Yield | Price-to-Book | Debt/Equity | ROE |\n"
        table += "|-------|-----------|-------------|----------------|---------------|-------------|-----|\n"
        
        for stock in stocks:
            data = stock_data.get(stock, {})
            if not data:
                continue
            
            pe_ratio = self._format_metric(data.get('pe_ratio'))
            forward_pe = self._format_metric(data.get('forward_pe'))
            dividend_yield = f"{data.get('dividend_yield', 0):.2f}%" if data.get('dividend_yield') else 'N/A'
            price_to_book = self._format_metric(data.get('price_to_book'))
            debt_to_equity = self._format_metric(data.get('debt_to_equity'))
            roe = f"{data.get('roe', 0):.2f}%" if data.get('roe') else 'N/A'
            
            table += f"| {stock} | {pe_ratio} | {forward_pe} | {dividend_yield} | {price_to_book} | {debt_to_equity} | {roe} |\n"
        
        return table
    
    def _generate_ratio_descriptions(self):
        """Generate descriptions of financial ratios"""
        return """
- **P/E Ratio (Price-to-Earnings):** Measures how much investors are willing to pay per dollar of earnings. Higher ratios may indicate growth expectations or overvaluation.

- **Forward P/E:** Similar to P/E ratio but uses projected earnings for the next 12 months.

- **Dividend Yield:** The percentage of a company's current stock price paid out as dividends annually.

- **Price-to-Book Ratio:** Compares a stock's market value to its book value. Values below 1.0 may indicate undervaluation.

- **Debt-to-Equity Ratio:** Measures a company's financial leverage by comparing total debt to shareholders' equity.

- **Return on Equity (ROE):** Indicates how effectively a company uses shareholders' equity to generate profits.
"""
    
    def _generate_correlation_section(self, correlation_data):
        """Generate correlation analysis section"""
        if correlation_data is None or correlation_data.empty:
            return "Correlation analysis not available due to insufficient data."
        
        section = """
The correlation analysis shows how the stock prices move in relation to each other:

"""
        
        # Generate correlation insights
        for i, stock1 in enumerate(correlation_data.columns):
            for j, stock2 in enumerate(correlation_data.columns):
                if i < j:  # Avoid duplicate pairs
                    corr_value = correlation_data.loc[stock1, stock2]
                    
                    if corr_value > 0.7:
                        relationship = "strong positive correlation"
                    elif corr_value > 0.3:
                        relationship = "moderate positive correlation"
                    elif corr_value > -0.3:
                        relationship = "weak correlation"
                    elif corr_value > -0.7:
                        relationship = "moderate negative correlation"
                    else:
                        relationship = "strong negative correlation"
                    
                    section += f"- **{stock1} vs {stock2}:** {corr_value:.3f} ({relationship})\n"
        
        return section
    
    def _generate_news_section(self, stocks, news_data, stock_data):
        """Generate news analysis section"""
        section = "Recent news headlines provide insights into market sentiment and company developments:\n\n"
        
        for stock in stocks:
            headlines = news_data.get(stock, [])
            company_name = stock_data.get(stock, {}).get('company_name', stock)
            
            section += f"### {stock} - {company_name}\n\n"
            
            if headlines:
                section += f"**Recent Headlines ({len(headlines)} found):**\n\n"
                for i, headline in enumerate(headlines[:8], 1):  # Show top 8 headlines
                    section += f"{i}. {headline}\n"
                
                # Basic sentiment analysis based on keywords
                positive_keywords = ['growth', 'profit', 'revenue', 'beat', 'strong', 'positive', 'gain', 'rise', 'up']
                negative_keywords = ['loss', 'down', 'fall', 'weak', 'decline', 'drop', 'negative', 'concern']
                
                positive_count = sum(1 for headline in headlines for keyword in positive_keywords if keyword in headline.lower())
                negative_count = sum(1 for headline in headlines for keyword in negative_keywords if keyword in headline.lower())
                
                if positive_count > negative_count:
                    sentiment = "predominantly positive"
                elif negative_count > positive_count:
                    sentiment = "predominantly negative"
                else:
                    sentiment = "mixed"
                
                section += f"\n**News Sentiment:** The recent news coverage appears {sentiment}.\n\n"
            else:
                section += "No recent news headlines were found for this stock.\n\n"
        
        return section
    
    def _generate_risk_assessment(self, stocks, stock_data, correlation_data):
        """Generate risk assessment and future scenarios"""
        section = """
### Risk Factors:

"""
        
        # Analyze volatility based on 6-month performance
        high_volatility_stocks = []
        for stock in stocks:
            data = stock_data.get(stock, {})
            six_month_change = abs(data.get('six_month_change', 0))
            if six_month_change > 20:  # Consider >20% change as high volatility
                high_volatility_stocks.append((stock, six_month_change))
        
        if high_volatility_stocks:
            section += "- **High Volatility Stocks:** "
            for stock, change in high_volatility_stocks:
                section += f"{stock} ({change:.1f}% change), "
            section = section.rstrip(', ') + "\n"
        
        # Correlation-based risk
        if correlation_data is not None and not correlation_data.empty:
            high_corr_pairs = []
            for i, stock1 in enumerate(correlation_data.columns):
                for j, stock2 in enumerate(correlation_data.columns):
                    if i < j and abs(correlation_data.loc[stock1, stock2]) > 0.7:
                        high_corr_pairs.append((stock1, stock2, correlation_data.loc[stock1, stock2]))
            
            if high_corr_pairs:
                section += "- **High Correlation Risk:** Strong correlations between "
                for stock1, stock2, corr in high_corr_pairs:
                    section += f"{stock1}-{stock2} ({corr:.2f}), "
                section = section.rstrip(', ') + " may lead to similar price movements.\n"
        
        section += """
### Future Scenarios:

**Bull Market Scenario:**
- Stocks with strong fundamentals and positive news sentiment may outperform
- High-growth stocks could see accelerated gains
- Dividend-paying stocks may attract income-focused investors

**Bear Market Scenario:**  
- High P/E ratio stocks may face pressure
- Highly correlated stocks may decline together
- Defensive stocks with strong balance sheets may be more resilient

**Neutral Market Scenario:**
- Stock selection based on individual company fundamentals becomes more important
- Dividend yields become more attractive relative to other investments
- Market correlation effects may be reduced
"""
        
        return section
    
    def _generate_conclusion(self, stocks, stock_data):
        """Generate conclusion section"""
        conclusion = f"""
Based on the comprehensive analysis of {', '.join(stocks)}, several key insights emerge:

"""
        
        # Find stocks with best fundamentals
        strong_stocks = []
        for stock in stocks:
            data = stock_data.get(stock, {})
            pe_ratio = data.get('pe_ratio', float('inf'))
            roe = data.get('roe', 0)
            
            # Simple scoring based on available metrics
            score = 0
            if isinstance(pe_ratio, (int, float)) and pe_ratio < 25:
                score += 1
            if isinstance(roe, (int, float)) and roe > 10:
                score += 1
            if data.get('six_month_change', 0) > 0:
                score += 1
            
            if score >= 2:
                strong_stocks.append(stock)
        
        if strong_stocks:
            conclusion += f"- **Fundamentally Strong Stocks:** {', '.join(strong_stocks)} show favorable metrics\n"
        
        conclusion += """
- Diversification across the analyzed stocks may help mitigate individual company risks
- Regular monitoring of news and fundamental changes is recommended
- Consider correlation effects when building a portfolio with these stocks

**Disclaimer:** This analysis is for informational purposes only and should not be considered as investment advice. 
Always consult with a qualified financial advisor before making investment decisions.
"""
        
        return conclusion
    
    def _format_metric(self, value):
        """Format metric values for display"""
        if value is None or value == 'N/A':
            return 'N/A'
        
        try:
            if isinstance(value, (int, float)):
                return f"{value:.2f}"
            else:
                return str(value)
        except:
            return 'N/A'
    
    def _format_large_number(self, value):
        """Format large numbers (market cap, volume) for readability"""
        if value is None or value == 'N/A':
            return 'N/A'
        
        try:
            if isinstance(value, (int, float)):
                if value >= 1e12:
                    return f"${value/1e12:.2f}T"
                elif value >= 1e9:
                    return f"${value/1e9:.2f}B"
                elif value >= 1e6:
                    return f"${value/1e6:.2f}M"
                else:
                    return f"${value:,.0f}"
            else:
                return str(value)
        except:
            return 'N/A'
