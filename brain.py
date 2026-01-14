import os
import json
import requests
import random
from datetime import datetime, timedelta

API_KEY = os.environ.get("GROQ_API_KEY")

def get_current_date():
    return datetime.now().strftime("%Y-%m-%d")

def days_between(d1, d2):
    try:
        d1 = datetime.strptime(d1, "%Y-%m-%d")
        d2 = datetime.strptime(d2, "%Y-%m-%d")
        return abs((d2 - d1).days)
    except:
        return 0

def update_database():
    if not API_KEY:
        print("❌ Error: GROQ_API_KEY is missing.")
        return

    print("🚀 Starting Daily Update (Model: Llama 3.3)...")

    # 기존 데이터 로드
    try:
        with open("data.json", "r", encoding="utf-8") as f:
            current_data = json.load(f)
    except:
        current_data = []

    # 1. 아카이빙 (90일 지난거)
    today = get_current_date()
    for item in current_data:
        detected = item.get('first_detected', today)
        if days_between(detected, today) > 90 and item['status'] == 'Active':
            item['status'] = 'Archived'
            print(f"📦 Archived: {item['term']}")

    # 2. 새 트렌드 찾기
    topics = ["Gen Z Slang", "Controversial Figure", "TikTok Trend", "Hate Symbol"]
    topic = random.choice(topics)
    print(f"🤖 Researching: {topic}")

    url = "https://api.groq.com/openai/v1/chat/completions"
    headers = {"Authorization": f"Bearer {API_KEY}", "Content-Type": "application/json"}
    
    prompt = f"""
    Find one specific real-world example of a "{topic}".
    Return a single JSON object (schema: term, group, country, category, risk_level, trend_score, status, first_detected, last_updated, context: {{en, ko, ja}}).
    """

    payload = {
        "model": "llama-3.3-70b-versatile", # [수정됨] 최신 모델!
        "messages": [
            {"role": "system", "content": "Output JSON only."},
            {"role": "user", "content": prompt}
        ],
        "response_format": {"type": "json_object"}
    }

    try:
        response = requests.post(url, headers=headers, json=payload)
        if response.status_code == 200:
            new_entry = json.loads(response.json()['choices'][0]['message']['content'])
            
            # 중복 체크 후 추가
            existing_terms = {item['term'].lower() for item in current_data}
            if new_entry['term'].lower() not in existing_terms:
                current_data.insert(0, new_entry)
                print(f"✅ Added: {new_entry['term']}")
            else:
                print(f"⚠️ Duplicate: {new_entry['term']}")
    except Exception as e:
        print(f"❌ Error: {e}")

    # 저장
    current_data.sort(key=lambda x: x['status'] == 'Archived')
    with open("data.json", "w", encoding="utf-8") as f:
        json.dump(current_data, f, indent=4, ensure_ascii=False)
    print("💾 Saved.")

if __name__ == "__main__":
    update_database()
