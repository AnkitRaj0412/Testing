import feedparser
import requests
from bs4 import BeautifulSoup
from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer
from jinja2 import Template
import re
from datetime import datetime

# Define RSS feeds for each source
rss_feeds = {
    "Investing.com": "https://www.investing.com/rss/news_1.rss",
    "FXStreet News": "https://www.fxstreet.com/rss/news",
    "FXStreet Analysis": "https://www.fxstreet.com/rss/analysis",
    "DailyFX": "https://rss.app/feed/dailyfx",  # Replace with real feed if available
    "Reuters Markets": "https://www.reuters.com/rssFeed/marketsNews",
    "Reuters Currencies": "https://www.reuters.com/rssFeed/currenciesNews"
}

major_currencies = ["USD", "EUR", "GBP", "JPY", "AUD", "CAD", "CHF", "NZD", "CNY"]
sentiment_threshold = {"positive": 0.05, "negative": -0.05}
analyzer = SentimentIntensityAnalyzer()

def extract_image(link):
    try:
        headers = {'User-Agent': 'Mozilla/5.0'}
        response = requests.get(link, headers=headers, timeout=10)
        soup = BeautifulSoup(response.content, 'html.parser')
        img = soup.find('img')
        return img['src'] if img and 'src' in img.attrs else None
    except:
        return None

def analyze_sentiment(text):
    score = analyzer.polarity_scores(text)['compound']
    if score >= sentiment_threshold['positive']:
        return 'Positive'
    elif score <= sentiment_threshold['negative']:
        return 'Negative'
    return 'Neutral'

def determine_impact(text):
    impact_keywords = ['interest rate', 'inflation', 'gdp', 'jobless', 'unemployment', 'central bank']
    return 'High' if any(k in text.lower() for k in impact_keywords) else 'Low'

def fetch_news():
    articles = []
    for source, url in rss_feeds.items():
        feed = feedparser.parse(url)
        for entry in feed.entries:
            content = entry.get('summary', '') + ' ' + entry.get('title', '')
            if not any(currency in content.upper() for currency in major_currencies):
                continue
            
            article = {
                'source': source,
                'title': entry.get('title', 'No Title'),
                'summary': BeautifulSoup(entry.get('summary', ''), 'html.parser').text,
                'link': entry.get('link', '#'),
                'published': entry.get('published', 'Unknown'),
                'image': extract_image(entry.get('link', '')),
                'sentiment': analyze_sentiment(content),
                'impact': determine_impact(content)
            }
            articles.append(article)
    return articles

def generate_html(articles):
    html_template = """
    <html>
    <head>
        <title>Forex Market News</title>
        <style>
            body { font-family: Arial, sans-serif; background: #f4f4f4; padding: 20px; }
            .article { background: white; margin-bottom: 20px; padding: 15px; border-radius: 8px; box-shadow: 0 0 5px rgba(0,0,0,0.1); }
            .article img { max-width: 100%; height: auto; }
            .meta { font-size: 0.9em; color: gray; }
            .sentiment { font-weight: bold; }
        </style>
    </head>
    <body>
        <h1>Forex Market News</h1>
        {% for article in articles %}
        <div class="article">
            <h2>{{ article.title }}</h2>
            <p class="meta">Source: {{ article.source }} | Published: {{ article.published }}</p>
            {% if article.image %}<img src="{{ article.image }}">{% endif %}
            <p>{{ article.summary }}</p>
            <p class="sentiment">Sentiment: {{ article.sentiment }} | Impact: {{ article.impact }}</p>
            <a href="{{ article.link }}" target="_blank">Read more</a>
        </div>
        {% endfor %}
    </body>
    </html>
    """
    template = Template(html_template)
    return template.render(articles=articles)

if __name__ == "__main__":
    news = fetch_news()
    html_output = generate_html(news)
    with open("forex_news_report.html", "w", encoding="utf-8") as f:
        f.write(html_output)
    print("Report generated: forex_news_report.html")
