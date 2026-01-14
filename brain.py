import os
import json
import requests
import random
from datetime import datetime, timedelta

# 1. Groq API 키 가져오기
API_KEY = os.environ.get("GROQ_API_KEY")

def get_current_date():
    return datetime.now().strftime("%Y-%m-%d")

# 날짜 차이 계산 함수
def days_between(d1, d2):
    d1 = datetime.strptime(d1, "%Y-%m-%d")
    d2 = datetime.strptime(d2, "%Y-%m-%d")
    return abs((d2 - d1).days)

def update_database():
    if not API_KEY:
        print("❌ Error: GROQ_API_KEY is missing.")
        return

    print("🚀 Starting Groq AI Agent...")

    # 2. 기존 데이터 로드
    try:
        with open("data.json", "r", encoding="utf-8") as f:
            current_data = json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        current_data = []

    # ==========================================
    # [기능 1] 오래된 데이터 아카이브 처리 (3개월 = 90일)
    # ==========================================
    today = get_current_date()
    for item in current_data:
        # 날짜 형식이 올바른지 확인 후 계산
        try:
            detected_date = item.get('first_detected', today)
            if days_between(detected_date, today) > 90:
                if item['status'] == 'Active':
                    item['status'] = 'Archived'
                    print(f"📦 Archived old item: {item['term']}")
        except:
            continue
    
    # ==========================================
    # [기능 2] 새로운 트렌드 추가
    # ==========================================
    topics = [
        "Gen Z Slang", "Controversial Influencer", "Viral TikTok Challenge", 
        "Alt-Right Hate Symbol", "Algospeak (Hidden words)", "Political Dog Whistle"
    ]
    topic = random.choice(topics)
    print(f"🤖 Researching Topic: {topic}")

    url = "https://api.groq.com/openai/v1/chat/completions"
    headers = {"Authorization": f"Bearer {API_KEY}", "Content-Type": "application/json"}
    
    system_prompt = "You are a cultural risk intelligence analyst. Output MUST be a valid JSON object only."
    
    # 3개월 전 데이터도 가끔 찾도록 프롬프트 조정
    user_prompt = f"""
    Find one specific real-world example of a "{topic}".
    It can be a current trend OR something from the last 3 months (since { (datetime.now() - timedelta(days=90)).strftime('%Y-%m') }).
    
    Return a single JSON object with this EXACT schema:
    {{
        "term": "Term Name",
        "group": "Choose one: 'language', 'person', 'group', 'trend'",
        "country": ["Country Code", "e.g. US"],
        "category": "Short Category",
        "risk_level": "High/Medium/Low",
        "trend_score": (Integer 1-100),
        "status": "Active",
        "first_detected": "YYYY-MM-DD",
        "last_updated": "{get_current_date()}",
        "context": {{
            "en": "English explanation (max 2 sentences).",
            "ko": "Korean explanation (max 2 sentences).",
            "ja": "Japanese explanation (max 2 sentences)."
        }}
    }}
    """

    payload = {
        "model": "llama3-70b-8192",
        "messages": [{"role": "system", "content": system_prompt}, {"role": "user", "content": user_prompt}],
        "temperature": 0.8, # 창의성 약간 높임
        "response_format": {"type": "json_object"}
    }

    try:
        response = requests.post(url, headers=headers, json=payload)
        if response.status_code == 200:
            new_entry = json.loads(response.json()['choices'][0]['message']['content'])
            
            # 중복 검사
            existing_terms = {item['term'] for item in current_data}
            if new_entry['term'] not in existing_terms:
                current_data.insert(0, new_entry)
                print(f"✅ Added: {new_entry['term']}")
            else:
                print(f"⚠️ Duplicate skipped: {new_entry['term']}")
    except Exception as e:
        print(f"❌ AI Error: {e}")

    # ==========================================
    # [저장]
    # ==========================================
    # 아카이브 된 것들은 리스트 뒤로 보내기 (정렬)
    current_data.sort(key=lambda x: x['status'] == 'Archived')

    with open("data.json", "w", encoding="utf-8") as f:
        json.dump(current_data, f, indent=4, ensure_ascii=False)
    print("💾 Database updated.")

if __name__ == "__main__":
    update_database()
