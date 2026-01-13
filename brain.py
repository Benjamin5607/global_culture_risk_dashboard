import json
import feedparser
from datetime import datetime

# 리스크를 감지할 키워드 목록 (이 단어가 뉴스에 나오면 위험도 증가)
RISK_KEYWORDS = [
    "war", "conflict", "crisis", "missile", "nuclear", "attack", 
    "dead", "kill", "threat", "tension", "military", "army", 
    "sanction", "collapse", "emergency", "danger"
]

def analyze_risk_from_news():
    # BBC 월드 뉴스 RSS 주소 (API 키 필요 없음, 무료 공개)
    rss_url = "http://feeds.bbci.co.uk/news/world/rss.xml"
    
    try:
        # 1. 뉴스 다운로드
        feed = feedparser.parse(rss_url)
        
        risk_score = 30 # 기본 점수 (평화로울 때)
        details = []
        
        # 2. 최신 뉴스 10개만 분석
        for entry in feed.entries[:10]:
            title = entry.title
            summary = entry.summary
            
            # 제목에서 위험 키워드 찾기
            found_keywords = [word for word in RISK_KEYWORDS if word in title.lower()]
            
            # 키워드 하나당 점수 5점 추가
            if found_keywords:
                risk_score += (len(found_keywords) * 5)
                # 리스크와 관련된 뉴스는 상세 목록에 추가
                details.append(f"⚠️ {title}")
            else:
                # 일반 뉴스는 그냥 목록에만 살짝 추가 (너무 많으면 3개까지만)
                if len(details) < 3:
                    details.append(f"- {title}")

        # 점수 보정 (최대 95점, 최소 10점)
        risk_score = min(max(risk_score, 10), 95)
        
        # 3. 결과 생성
        risk_data = {
            "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "risk_score": risk_score,
            "summary": f"Analyzed {len(feed.entries)} news articles from BBC World.",
            "details": details[:5] # 상위 5개만 보여줌
        }
        
        return risk_data

    except Exception as e:
        print(f"Error parsing news: {e}")
        return {
            "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "risk_score": 50,
            "summary": "News Feed Unavailable",
            "details": ["Could not fetch BBC RSS feed."]
        }

if __name__ == "__main__":
    data = analyze_risk_from_news()
    
    with open("data.json", "w", encoding="utf-8") as f:
        json.dump(data, f, indent=4, ensure_ascii=False)
        
    print(f"✅ Data updated without AI. Risk Score: {data['risk_score']}")
