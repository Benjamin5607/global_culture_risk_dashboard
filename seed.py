import os
import json
import requests
import random
import time
from datetime import datetime

# API 키
API_KEY = os.environ.get("GROQ_API_KEY")

def get_current_date():
    return datetime.now().strftime("%Y-%m-%d")

def generate_bulk_data():
    print("🏭 Factory Started (Model: Llama 3.3)...")

    if not API_KEY:
        print("❌ Error: GROQ_API_KEY not found.")
        return

    # 1. 기존 데이터 로드
    try:
        with open("data.json", "r", encoding="utf-8") as f:
            current_data = json.load(f)
        print(f"📂 Loaded {len(current_data)} existing items.")
    except:
        current_data = []

    existing_terms = {item['term'].lower() for item in current_data}

    # 2. 주제 리스트 (다양화)
    categories = [
        "Gen Z Internet Slang", "Right-Wing Political Dog Whistles", 
        "Controversial Influencers 2025", "Dangerous TikTok Challenges",
        "Online Hate Symbols", "Algospeak words used on TikTok",
        "Gender War terms", "Cryptocurrency Slang"
    ]

    # 3. 10번 반복 (총 50개 생산)
    for i in range(10):
        category = random.choice(categories)
        print(f"\n🔄 Batch {i+1}/10 - Researching: {category}...")

        url = "https://api.groq.com/openai/v1/chat/completions"
        headers = {"Authorization": f"Bearer {API_KEY}", "Content-Type": "application/json"}

        prompt = f"""
        Generate a list of 5 distinct real-world examples of "{category}".
        Focus on trends relevant in 2024-2026.
        
        Output MUST be a valid JSON object containing a key "items" which is a list of objects.
        Schema for each object:
        {{
            "term": "Term Name",
            "group": "Choose one: 'language', 'person', 'group', 'trend'",
            "country": ["Country Code"],
            "category": "Short Category",
            "risk_level": "High/Medium/Low",
            "trend_score": (Integer 40-99),
            "status": "Active",
            "first_detected": "YYYY-MM-DD",
            "last_updated": "{get_current_date()}",
            "context": {{
                "en": "Explanation in English.",
                "ko": "Explanation in Korean.",
                "ja": "Explanation in Japanese."
            }}
        }}
        """

        payload = {
            "model": "llama-3.3-70b-versatile", # [수정됨] 최신 모델!
            "messages": [
                {"role": "system", "content": "You are a database generator. Output JSON only."},
                {"role": "user", "content": prompt}
            ],
            "response_format": {"type": "json_object"}
        }

        try:
            response = requests.post(url, headers=headers, json=payload)
            if response.status_code == 200:
                result = response.json()
                content = result['choices'][0]['message']['content']
                batch_data = json.loads(content).get('items', [])
                
                added_count = 0
                for item in batch_data:
                    if item['term'].lower() not in existing_terms:
                        current_data.append(item)
                        existing_terms.add(item['term'].lower())
                        added_count += 1
                print(f"✅ Batch {i+1} Success: Added {added_count} new items.")
            else:
                print(f"❌ API Error: {response.text}")

        except Exception as e:
            print(f"⚠️ Error in batch {i+1}: {e}")
            
        time.sleep(1) # 1초 휴식

    # 4. 저장
    print(f"\n💾 Saving... Total items: {len(current_data)}")
    with open("data.json", "w", encoding="utf-8") as f:
        json.dump(current_data, f, indent=4, ensure_ascii=False)

if __name__ == "__main__":
    generate_bulk_data()
