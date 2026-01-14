import os
import json
import requests
import random
import time
from datetime import datetime, timedelta

# Groq API 키 (GitHub Secrets에서 가져옴)
API_KEY = os.environ.get("GROQ_API_KEY")

def get_current_date():
    return datetime.now().strftime("%Y-%m-%d")

def generate_bulk_data():
    if not API_KEY:
        print("❌ Error: GROQ_API_KEY is missing.")
        return

    print("🏭 Starting Bulk Data Factory...")

    # 1. 기존 데이터 로드 (중복 방지용)
    try:
        with open("data.json", "r", encoding="utf-8") as f:
            current_data = json.load(f)
    except:
        current_data = []

    existing_terms = {item['term'].lower() for item in current_data}
    print(f"📊 Current Database Size: {len(current_data)} items")

    # 2. 주제 리스트 (다양성을 위해)
    categories = [
        "Gen Z Internet Slang", "Right-Wing Political Dog Whistles", 
        "Controversial Influencers 2024-2025", "Dangerous TikTok Challenges",
        "Online Hate Symbols", "Algospeak words used on TikTok",
        "Gender War terms in Korea/US", "Cryptocurrency Scams/Slang"
    ]

    # 3. 10번 반복 (한 번에 5개씩 = 총 50개 생산)
    for i in range(10):
        category = random.choice(categories)
        print(f"\n🔄 Batch {i+1}/10 - Researching: {category}...")

        url = "https://api.groq.com/openai/v1/chat/completions"
        headers = {"Authorization": f"Bearer {API_KEY}", "Content-Type": "application/json"}

        # [핵심] 한 번에 5개씩 리스트로 달라고 요청
        prompt = f"""
        Generate a list of 5 distinct real-world examples of "{category}".
        Focus on trends from the last 2 years.
        
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
            "model": "llama3-70b-8192",
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
                
                # JSON 파싱
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
        
        # Groq 부하 방지를 위해 2초 휴식
        time.sleep(2)

    # 4. 최종 저장
    print(f"\n💾 Saving... New Total: {len(current_data)} items")
    with open("data.json", "w", encoding="utf-8") as f:
        json.dump(current_data, f, indent=4, ensure_ascii=False)

if __name__ == "__main__":
    generate_bulk_data()
