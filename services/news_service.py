from dataclasses import dataclass
from datetime import datetime
import sys
import os

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from services.cache_service import cache_get, cache_set
from utils.config import Config

@dataclass
class NewsItem:
    headline: str
    source: str
    category: str
    region: str
    published_at: str
    severity_hint: str

def _get_stub_news() -> list[NewsItem]:
    return [
        NewsItem("Port of Los Angeles workers threaten strike", "Logistics Weekly", "logistics", "us-west-coast", datetime.utcnow().isoformat(), "HIGH"),
        NewsItem("Suez canal partially blocked due to high winds", "Global News", "logistics", "middle-east", datetime.utcnow().isoformat(), "CRITICAL"),
        NewsItem("Category 4 hurricane forming in the Atlantic", "Weather Network", "weather", "us-east-coast", datetime.utcnow().isoformat(), "CRITICAL"),
        NewsItem("Ransomware attack targets major shipping firm", "CyberTech News", "cyber", "global", datetime.utcnow().isoformat(), "HIGH"),
        NewsItem("Tensions rise in South China Sea", "World Politics", "geopolitical", "east-asia", datetime.utcnow().isoformat(), "HIGH"),
        NewsItem("Microchip supplier halts production", "Tech Daily", "supplier", "east-asia", datetime.utcnow().isoformat(), "CRITICAL"),
        NewsItem("New tariffs imposed on EU imports", "Trade Times", "customs", "europe", datetime.utcnow().isoformat(), "MEDIUM"),
        NewsItem("Truck driver shortage worsens in UK", "Transport News", "logistics", "europe", datetime.utcnow().isoformat(), "MEDIUM")
    ] * 5

def fetch_headlines(query: str = "", max_results: int = 10) -> list[NewsItem]:
    """
    # TO SWAP FOR REAL API (e.g. NewsAPI.org):
    # import requests
    # API_KEY = os.getenv("NEWS_API_KEY")
    # url = f"https://newsapi.org/v2/everything?q={query}&apiKey={API_KEY}"
    # response = requests.get(url)
    # data = response.json()
    # return [NewsItem(headline=a['title'], ...) for a in data['articles'][:max_results]]
    """
    try:
        results = _get_stub_news()
        if query:
            results = [r for r in results if query.lower() in r.headline.lower()]
        return results[:max_results]
    except Exception as e:
        return []

def fetch_by_category(category: str) -> list[NewsItem]:
    try:
        return [r for r in _get_stub_news() if r.category == category]
    except Exception:
        return []

def fetch_by_region(region: str) -> list[NewsItem]:
    try:
        if region == "global":
            return _get_stub_news()[:10]
        return [r for r in _get_stub_news() if r.region == region]
    except Exception:
        return []