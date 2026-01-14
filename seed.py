import os
import json
import requests
import random
import time
from datetime import datetime

# API 키 확인
API_KEY = os.environ.get("GROQ_API_KEY")

def get_current_date():
    return datetime.now().strftime("%Y-%m-%d")

# [비상용] API가 죽었을 때 강제로 넣을 데이터
BACKUP_DATA = [
    {
        "term": "Debug Mode Active",
        "group": "trend",
        "country": ["Test"],
        "category": "System Check",
        "risk_level": "Low",
        "trend_score": 99,
        "status": "Active",
        "first_detected": "2026-01-01",
        "last_updated": get_current_date(),
        "context": {
            "en": "If you see this, the Python script is working, but API might be failed.",
            "ko": "이게 보이면 파이썬은 정상입니다. API 키나 호출에 문제가 있는 겁니다.",
            "ja": "これが表示されたらシステムは正常です。"
        }
    }
]

def generate_bulk_data():
    print("🏭 Factory Started...")

    # 1. API 키 검사
    if not API_KEY:
        print("❌ CRITICAL: 'GROQ_API_KEY' not found in Secrets!")
        print("⚠️ Using BACKUP data to test file write...")
        new_items = BACKUP_DATA
    else:
        print(f"🔑 API Key found (starts with {API_KEY[:4]}...)")
        new_items = []

    # 2. 기존 데이터 로드
    try:
        with open("data.json", "r", encoding="utf-8") as f:
            current_data = json.load(f)
        print(f"📂 Loaded {len(current_data)} existing items.")
    except:
        current_data = []
        print("📂 No existing data found. Creating new.")

    # 3. API 호출 (키가 있을 때만)
    if API_KEY:
        categories = ["Internet Slang", "Viral Trends"]
        
        # 테스트를 위해 딱 1번만 호출해봅니다 (확실하게 하기 위해)
        print("\n📡 Calling Groq API (Test Run)...")
        
        url = "https://api.groq.com/openai/v1/chat/completions"
        headers = {"Authorization": f"Bearer {API_KEY}", "Content-Type": "application/json"}
        
        prompt = """
        Generate 3 distinct slang terms.
        Output JSON object with key "items".
        Schema: {"term", "group", "country", "category", "risk_level", "trend_score", "status", "first_detected", "last_updated", "context": {"en", "ko", "ja"}}
        """

        payload = {
            "model": "llama3-70b-8192",
            "messages": [
                {"role": "system", "content": "Output JSON only."},
                {"role": "user", "content": prompt}
            ],
            "response_format": {"type": "json_object"}
        }

        try:
            response = requests.post(url, headers=headers, json=payload)
            
            if response.status_code == 200:
                result = response.json()
                content = result['choices'][0]['message']['content']
                new_items = json.loads(content).get('items', [])
                print(f"✅ API Success! Got {len(new_items)} items.")
            else:
                print(f"❌ API Error: {response.status_code} - {response.text}")
                print("⚠️ Switching to BACKUP data.")
                new_items = BACKUP_DATA

        except Exception as e:
            print(f"❌ Exception: {e}")
            new_items = BACKUP_DATA

    # 4. 데이터 병합 및 저장
    if new_items:
        # 중복 제거
        existing_terms = {item['term'].lower() for item in current_data}
        added = 0
        for item in new_items:
            if item['term'].lower() not in existing_terms:
                current_data.insert(0, item)
                added += 1
        
        print(f"💾 Saving {len(current_data)} items to data.json...")
        with open("data.json", "w", encoding="utf-8") as f:
            json.dump(current_data, f, indent=4, ensure_ascii=False)
        print("✅ File Write Complete.")
    else:
        print("⚠️ No new items to save.")

if __name__ == "__main__":
    generate_bulk_data()
