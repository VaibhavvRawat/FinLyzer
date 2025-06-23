import requests
from bs4 import BeautifulSoup
import urllib.parse
import time
import random

class NewsScraper:
    def __init__(self):
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        }
    
    def get_stock_news(self, company_name, stock_symbol, max_headlines=10):
        """Get news headlines for a stock using web scraping"""
        headlines = []
        
        try:
            # Try multiple sources
            sources = [
                self._get_google_news_headlines,
                self._get_yahoo_news_headlines,
                self._get_bing_news_headlines
            ]
            
            for source_func in sources:
                try:
                    source_headlines = source_func(company_name, stock_symbol)
                    headlines.extend(source_headlines)
                    if len(headlines) >= max_headlines:
                        break
                    time.sleep(random.uniform(1, 2))  # Rate limiting
                except Exception as e:
                    print(f"Error with news source: {str(e)}")
                    continue
            
            # Remove duplicates and limit to max_headlines
            unique_headlines = list(dict.fromkeys(headlines))  # Preserves order
            return unique_headlines[:max_headlines]
            
        except Exception as e:
            print(f"Error getting news for {stock_symbol}: {str(e)}")
            return []
    
    def _get_google_news_headlines(self, company_name, stock_symbol):
        """Scrape Google News for headlines"""
        headlines = []
        
        try:
            # Search for news about the company
            query = f"{company_name} stock news"
            encoded_query = urllib.parse.quote(query)
            url = f"https://news.google.com/rss/search?q={encoded_query}&hl=en-US&gl=US&ceid=US:en"
            
            response = requests.get(url, headers=self.headers, timeout=10)
            response.raise_for_status()
            
            soup = BeautifulSoup(response.content, 'xml')
            items = soup.find_all('item')
            
            for item in items[:5]:  # Limit to 5 headlines per source
                title = item.find('title')
                if title:
                    headline = title.text.strip()
                    if headline and len(headline) > 10:  # Filter out very short headlines
                        headlines.append(headline)
            
        except Exception as e:
            print(f"Error scraping Google News: {str(e)}")
        
        return headlines
    
    def _get_yahoo_news_headlines(self, company_name, stock_symbol):
        """Scrape Yahoo Finance for headlines"""
        headlines = []
        
        try:
            # Yahoo Finance news URL
            url = f"https://finance.yahoo.com/quote/{stock_symbol}/news"
            
            response = requests.get(url, headers=self.headers, timeout=10)
            response.raise_for_status()
            
            soup = BeautifulSoup(response.content, 'html.parser')
            
            # Look for news headlines in Yahoo Finance
            news_elements = soup.find_all(['h3', 'h4'], class_=lambda x: x and 'headline' in x.lower() if x else False)
            
            for element in news_elements[:5]:
                headline = element.get_text().strip()
                if headline and len(headline) > 10:
                    headlines.append(headline)
            
            # Fallback: look for any news-like headlines
            if not headlines:
                all_headlines = soup.find_all(['h3', 'h4'])
                for element in all_headlines[:10]:
                    text = element.get_text().strip()
                    if text and len(text) > 20 and any(keyword in text.lower() for keyword in ['stock', 'shares', 'earnings', 'revenue', 'profit', 'loss']):
                        headlines.append(text)
                        if len(headlines) >= 5:
                            break
            
        except Exception as e:
            print(f"Error scraping Yahoo Finance: {str(e)}")
        
        return headlines
    
    def _get_bing_news_headlines(self, company_name, stock_symbol):
        """Scrape Bing News for headlines"""
        headlines = []
        
        try:
            # Bing News search
            query = f"{company_name} {stock_symbol} news"
            encoded_query = urllib.parse.quote(query)
            url = f"https://www.bing.com/news/search?q={encoded_query}"
            
            response = requests.get(url, headers=self.headers, timeout=10)
            response.raise_for_status()
            
            soup = BeautifulSoup(response.content, 'html.parser')
            
            # Look for news headlines
            news_cards = soup.find_all('div', class_=lambda x: x and 'news' in x.lower() if x else False)
            
            for card in news_cards[:5]:
                title_elements = card.find_all(['a', 'h2', 'h3', 'h4'])
                for element in title_elements:
                    headline = element.get_text().strip()
                    if headline and len(headline) > 15:
                        headlines.append(headline)
                        break
                if len(headlines) >= 5:
                    break
            
        except Exception as e:
            print(f"Error scraping Bing News: {str(e)}")
        
        return headlines
    
    def _clean_headline(self, headline):
        """Clean and format headline text"""
        if not headline:
            return ""
        
        # Remove extra whitespace
        headline = " ".join(headline.split())
        
        # Remove common prefixes/suffixes
        prefixes_to_remove = ['Breaking:', 'BREAKING:', 'News:', 'NEWS:']
        for prefix in prefixes_to_remove:
            if headline.startswith(prefix):
                headline = headline[len(prefix):].strip()
        
        return headline
    
    def get_news_summary(self, news_data):
        """Generate a summary of news data"""
        summary = {}
        
        for stock, headlines in news_data.items():
            if headlines:
                summary[stock] = {
                    'count': len(headlines),
                    'sample_headlines': headlines[:3]  # First 3 headlines as samples
                }
            else:
                summary[stock] = {
                    'count': 0,
                    'sample_headlines': []
                }
        
        return summary
