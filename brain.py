import json
import feedparser
import requests
from datetime import datetime

# 100% English Keywords
RISK_KEYWORDS = [
    "war", "conflict", "crisis", "missile", "nuclear", "attack", 
    "dead", "kill", "threat", "tension", "military", "army", 
    "sanction", "collapse", "emergency", "danger", "strike", "blast"
]

# Multiple Sources to prevent empty data
RSS_FEEDS = [
    "http://feeds.bbci.co.uk/news/world/rss.xml",       # BBC World
    "http://rss.cnn.com/rss/edition_world.rss",         # CNN World
    "https://www.nytimes.com/services/xml/rss/nyt/World.xml" # NYT World
]

def analyze_risk_from_news():
    combined_entries = []
    
    # "I am a browser, not a bot" header
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
    }

    print("Fetching news feeds...")

    for url in RSS_FEEDS:
        try:
            # Download XML first using requests (to bypass blocks)
            response = requests.get(url, headers=headers, timeout=10)
            if response.status_code == 200:
                # Parse the downloaded string
                feed = feedparser.parse(response.content)
                combined_entries.extend(feed.entries)
                print(f"✅ Fetched {len(feed.entries)} articles from {url}")
            else:
                print(f"❌ Failed to fetch {url}: {response.status_code}")
        except Exception as e:
            print(f"⚠️ Error fetching {url}: {e}")

    # Analysis Logic
    risk_score = 30
    details = []
    keyword_count = 0

    # Analyze latest 20 articles
    for entry in combined_entries[:20]:
        title = entry.title
        # Check for keywords (Case insensitive)
        found_keywords = [word for word in RISK_KEYWORDS if word in title.lower()]
        
        if found_keywords:
            keyword_count += len(found_keywords)
            details.append(f"⚠️ {title}")
        
    # Calculate Score
    risk_score += (keyword_count * 3)
    risk_score = min(max(risk_score, 10), 98) # Min 10, Max 98

    # Fill details if empty
    if not details:
        details = [entry.title for entry in combined_entries[:5]]
        summary_text = "No immediate high-risk keywords detected in major headlines."
    else:
        summary_text = f"Detected {keyword_count} risk-related keywords across major global news outlets."

    # Final English Data Structure
    risk_data = {
        "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S UTC"),
        "risk_score": risk_score,
        "summary": summary_text,
        "details": details[:7] # Show top 7 items
    }
    
    return risk_data

if __name__ == "__main__":
    data = analyze_risk_from_news()
    
    with open("data.json", "w", encoding="utf-8") as f:
        json.dump(data, f, indent=4, ensure_ascii=False)
        
    print(f"✅ Data updated. Score: {data['risk_score']}")
