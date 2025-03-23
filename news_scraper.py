import requests
from bs4 import BeautifulSoup
import csv
from datetime import datetime
import time
import logging
from typing import List, Dict

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)

class BBCNewsScraper:
    def __init__(self, base_url: str = "https://www.bbc.com/news"):
        self.base_url = base_url
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        }

    def fetch_page(self, url: str) -> BeautifulSoup:
        """Fetch and parse a webpage."""
        try:
            response = requests.get(url, headers=self.headers)
            response.raise_for_status()
            return BeautifulSoup(response.text, 'html.parser')
        except requests.RequestException as e:
            logging.error(f"Error fetching page: {e}")
            return None

    def extract_articles(self, soup: BeautifulSoup) -> List[Dict]:
        """Extract article information from the parsed page."""
        articles = []
        
        # Find all article elements
        article_elements = soup.find_all('div', {'data-component': 'article'})
        
        for article in article_elements:
            try:
                # Extract title and link
                title_element = article.find('a', {'class': 'gs-c-promo-heading'})
                if not title_element:
                    continue
                    
                title = title_element.text.strip()
                url = title_element.get('href')
                if not url.startswith('http'):
                    url = f"https://www.bbc.com{url}"
                
                # Extract timestamp if available
                time_element = article.find('time')
                publish_date = time_element.get('datetime') if time_element else ''
                
                articles.append({
                    'title': title,
                    'url': url,
                    'publish_date': publish_date
                })
                
            except Exception as e:
                logging.error(f"Error extracting article: {e}")
                continue
                
        return articles

    def save_to_csv(self, articles: List[Dict], filename: str = None):
        """Save the extracted articles to a CSV file."""
        if not filename:
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            filename = f'bbc_news_{timestamp}.csv'
        
        try:
            with open(filename, 'w', newline='', encoding='utf-8') as csvfile:
                fieldnames = ['title', 'url', 'publish_date']
                writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
                
                writer.writeheader()
                writer.writerows(articles)
                
            logging.info(f"Successfully saved {len(articles)} articles to {filename}")
            
        except IOError as e:
            logging.error(f"Error saving to CSV: {e}")

    def run(self):
        """Run the scraper."""
        logging.info("Starting BBC News scraper...")
        
        # Fetch and parse the main page
        soup = self.fetch_page(self.base_url)
        if not soup:
            return
        
        # Extract articles
        articles = self.extract_articles(soup)
        
        # Save results
        self.save_to_csv(articles)
        
        logging.info("Scraping completed!")

if __name__ == "__main__":
    # Create and run the scraper
    scraper = BBCNewsScraper()
    scraper.run() 