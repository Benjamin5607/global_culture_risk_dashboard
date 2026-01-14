import os
import json
import requests
import random
from datetime import datetime

API_KEY = os.environ.get("GROQ_API_KEY")

def get_current_date():
    return datetime.now().strftime("%Y-%m-%d")

def days_between(d1, d2):
    try:
        d1 = datetime.strptime(str(d1), "%Y-%m-%d") # 문자열로 강제 변환 후 처리
        d2 = datetime.strptime(str(d2), "%Y-%m-%d")
        return abs((d2 - d1).days)
    except:
        return 0

def update_database():
    if not API_KEY:
        print("❌ Error: GROQ_API_KEY is missing.")
        return

    print("🚀 Starting Daily Update (Model: Llama 3.1 Instant)...")

    # 기존 데이터 로드
    try:
        with open("data.json", "r", encoding="utf-8") as f:
            current_data = json.load(f)
    except:
        current_data = []

    # ==========================================
    # [핵심 수정] 데이터 불량 검사 및 자동 수리
    # ==========================================
    print(f"🔧 Checking {len(current_data)} items for errors...")
    for item in current_data:
        # status가 없으면 'Active'로 강제 할당
        if 'status' not in item:
            item['status'] = 'Active'
        # 날짜가 없으면 오늘 날짜로 강제 할당
        if 'first_detected' not in item:
            item['first_detected'] = get_current_date()
        # term이 없으면 'Unknown' 처리
        if 'term' not in item:
            item['term'] = 'Unknown Issue'

    # 1. 아카이빙 (90일 지난거)
    today = get_current_date()
    for item in current_data:
        # .get()을 써서 안전하게 가져옴
        detected = item.get('first_detected', today)
        status = item.get('status', 'Active')
        
        if days_between(detected, today) > 90 and status == 'Active':
            item['status'] = 'Archived'
            print(f"📦 Archived: {item.get('term', 'Unknown')}")

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
        "model": "llama-3.1-8b-instant", # 최신 모델
        "messages": [
            {"role": "system", "content": "Output JSON only."},
            {"role": "user", "content": prompt}
        ],
        "response_format": {"type": "json_object"}
    }

    try:
        response = requests.post(url, headers=headers, json=payload)
        if response.status_code == 200:
            content = response.json()['choices'][0]['message']['content']
            new_entry = json.loads(content)
            
            # 안전장치: AI가 status를 빼먹었을 경우 대비
            if 'status' not in new_entry: new_entry['status'] = 'Active'
            if 'first_detected' not in new_entry: new_entry['first_detected'] = get_current_date()

            # 중복 체크
            existing_terms = {item.get('term', '').lower() for item in current_data}
            
            if new_entry.get('term', '').lower() not in existing_terms:
                current_data.insert(0, new_entry)
                print(f"✅ Added: {new_entry.get('term')}")
            else:
                print(f"⚠️ Duplicate: {new_entry.get('term')}")
    except Exception as e:
        print(f"❌ Error during AI fetch: {e}")

    # 3. 저장 및 정렬 (여기가 아까 에러 난 곳)
    # .get('status', 'Active')를 써서 status가 없어도 에러 안 나게 방어
    current_data.sort(key=lambda x: x.get('status', 'Active') == 'Archived')
    
    with open("data.json", "w", encoding="utf-8") as f:
        json.dump(current_data, f, indent=4, ensure_ascii=False)
    print("💾 Saved successfully.")

if __name__ == "__main__":
    update_database()
