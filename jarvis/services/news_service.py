import requests
import xml.etree.ElementTree as ET
from typing import List, Optional
from jarvis.utils.logger import logger
from jarvis.config.settings import NEWS_COUNTRY

class NewsService:
    @staticmethod
    def get_news_headlines(country: Optional[str] = None, limit: int = 5) -> str:
        """Fetch latest news headlines from Google News RSS feed."""
        if not country or not country.strip():
            country = NEWS_COUNTRY

        logger.info(f"Fetching news headlines for country: {country}")
        url = f"https://news.google.com/rss?hl=en-{country.upper()}&gl={country.upper()}&ceid={country.upper()}:en"
        
        try:
            response = requests.get(url, timeout=5)
            if response.status_code == 200:
                root = ET.fromstring(response.content)
                items = root.findall('.//item')
                
                headlines = []
                for idx, item in enumerate(items[:limit]):
                    title = item.find('title').text
                    # Clean up source from title, e.g. "Title - Source" -> "Title"
                    if " - " in title:
                        title = title.rsplit(" - ", 1)[0]
                    headlines.append(f"{idx + 1}. {title}")
                
                if headlines:
                    report = f"Here are the top news headlines for today: " + ", ".join(headlines)
                    logger.info("News headlines fetched successfully.")
                    return report
                else:
                    logger.warning("No news articles found in Google News RSS.")
            else:
                logger.warning(f"Google News RSS returned status code {response.status_code}")
        except Exception as e:
            logger.error(f"Error fetching news from RSS: {e}")
            
        return "I'm sorry, I was unable to fetch the news updates at this time."
