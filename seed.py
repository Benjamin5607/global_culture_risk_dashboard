import os
import json
import requests
import time
import random
from datetime import datetime

# API 키 가져오기
API_KEY = os.environ.get("GROQ_API_KEY")

def get_current_date():
    return datetime.now().strftime("%Y-%m-%d")

def generate_massive_data_safe():
    print("🏭 Factory Started (Model: Llama 3.1 Instant + Image Support)...")

    if not API_KEY:
        print("❌ Error: GROQ_API_KEY not found.")
        return

    # 1. 기존 데이터 로드
    try:
        with open("data.json", "r", encoding="utf-8") as f:
            current_data = json.load(f)
    except:
        current_data = []

    existing_terms = {item['term'].lower() for item in current_data}
    print(f"📂 Loaded {len(current_data)} existing items.")

    # 2. 5개국 타겟 질문 리스트
    prompts = []
    target_countries = ["USA", "UK", "Canada", "Australia", "New Zealand"]
    
    for country in target_countries:
        prompts.append(f"Trending internet slang in {country}")
        prompts.append(f"Controversial public figures in {country}") # 인물
        prompts.append(f"Dangerous extremist groups in {country}")   # 그룹
        prompts.append(f"Political dog whistles in {country}")
        prompts.append(f"TikTok trends in {country}")

    random.shuffle(prompts)

    url = "https://api.groq.com/openai/v1/chat/completions"
    headers = {"Authorization": f"Bearer {API_KEY}", "Content-Type": "application/json"}

    # 공장 가동 (최대 15번 반복 - 깃허브 시간 제한 고려)
    max_batches = 15
    for i, topic in enumerate(prompts[:max_batches]):
        if len(current_data) >= 500:
            print("\n🎉 500개 달성!")
            break

        print(f"\n🔄 [{i+1}/{max_batches}] '{topic}' (이미지 찾는 중...)")

        # [핵심] 여기에 image_url을 요청하는 줄을 넣었습니다! 👇
        system_prompt = f"""
        List 8 distinct items related to "{topic}". 
        Focus on 2024-2026 trends in USA, UK, Canada, Australia, NZ.
        
        Output JSON object with key "items".
        Schema: 
        - term: string
        - image_url: string (URL of a public image/logo if available, otherwise "null")
        - group: 'language' | 'person' | 'group' | 'trend'
        - country: list of strings
        - category: string
        - risk_level: 'High' | 'Medium' | 'Low'
        - trend_score: Integer (40-99)
        - status: 'Active'
        - first_detected: 'YYYY-MM-DD'
        - last_updated: '{get_current_date()}'
        - context: {{ "en": "...", "ko": "...", "ja": "..." }}
        """

        payload = {
            "model": "llama-3.1-8b-instant", # 가장 빠른 모델
            "messages": [
                {"role": "system", "content": "Output JSON only."},
                {"role": "user", "content": system_prompt}
            ],
            "response_format": {"type": "json_object"}
        }

        try:
            response = requests.post(url, headers=headers, json=payload)
            if response.status_code == 200:
                content = response.json()['choices'][0]['message']['content']
                items = json.loads(content).get('items', [])
                
                added = 0
                for item in items:
                    if item['term'].lower() not in existing_terms:
                        # 이미지 URL이 없거나 이상하면 null로 처리
                        if 'image_url' not in item: item['image_url'] = "null"
                        
                        item['last_updated'] = get_current_date()
                        current_data.append(item)
                        existing_terms.add(item['term'].lower())
                        added += 1
                print(f"   ✅ {added} items added.")
                
            elif response.status_code == 429:
                print("   ⏳ Rate limit. Sleeping 30s...")
                time.sleep(30)
            else:
                print(f"   ❌ API Error: {response.text}")

        except Exception as e:
            print(f"   ⚠️ Exception: {e}")

        time.sleep(2) # 2초 휴식

    # 저장
    print(f"\n💾 Saving {len(current_data)} items to data.json...")
    with open("data.json", "w", encoding="utf-8") as f:
        json.dump(current_data, f, indent=4, ensure_ascii=False)

if __name__ == "__main__":
    generate_massive_data_safe()
