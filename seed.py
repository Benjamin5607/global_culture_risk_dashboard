import os
import json
import requests
import time
import random
from datetime import datetime

# 깃허브 Secrets에서 키를 가져옵니다
API_KEY = os.environ.get("GROQ_API_KEY")

def get_current_date():
    return datetime.now().strftime("%Y-%m-%d")

def generate_massive_data():
    print("🏭 GitHub Cloud Factory: Five Eyes (US/UK/CA/AU/NZ) Mode Started...")

    if not API_KEY:
        print("❌ Error: GROQ_API_KEY not found in Secrets.")
        return

    # 1. 기존 데이터 로드
    try:
        with open("data.json", "r", encoding="utf-8") as f:
            current_data = json.load(f)
        print(f"📂 Loaded existing data: {len(current_data)} items")
    except:
        current_data = []
        print("📂 No existing data. Starting fresh.")

    existing_terms = {item['term'].lower() for item in current_data}

    # ==========================================
    # 질문 리스트 생성 (미국, 영국, 캐나다, 호주, 뉴질랜드 집중)
    # ==========================================
    prompts = []
    target_countries = ["USA", "UK", "Canada", "Australia", "New Zealand"]
    
    # 전략: 국가별 + 알파벳별 분할 정복
    alphabet_chunks = ["ABCDE", "FGHIJ", "KLMNO", "PQRST", "UVWXYZ"]
    
    for country in target_countries:
        # 알파벳별 슬랭 찾기
        for chunk in alphabet_chunks:
            prompts.append(f"Gen Z internet slang in {country} starting with letters {chunk}")
        
        # 국가별 특수 주제
        prompts.append(f"Political dog whistles used in {country}")
        prompts.append(f"Controversial influencers in {country} (2024-2025)")
        prompts.append(f"Corporate buzzwords specific to {country}")

    # 공통 주제
    common_topics = [
        "Incel and Manosphere terminology (English)",
        "Gaming and Twitch chat slang (Western)",
        "Algospeak words on TikTok (English)",
        "Crypto slang"
    ]
    prompts.extend(common_topics)

    random.shuffle(prompts) # 순서 섞기

    # ==========================================
    # 공장 가동 (깃허브 액션 시간 제한 고려하여 최대 15번 배치만 실행)
    # ==========================================
    # 로컬과 달리 깃허브는 너무 오래 돌면 강제 종료될 수 있어서
    # 한 번 실행에 15번 질문(약 100~120개 생산) 정도로 제한하는 게 안전합니다.
    max_batches = 15 
    
    url = "https://api.groq.com/openai/v1/chat/completions"
    headers = {"Authorization": f"Bearer {API_KEY}", "Content-Type": "application/json"}

    for i, specific_topic in enumerate(prompts[:max_batches]):
        print(f"\n🔄 Batch [{i+1}/{max_batches}] Topic: '{specific_topic}'")

        system_prompt = f"""
        List 8 distinct real-world terms related to "{specific_topic}".
        Target Countries: USA, UK, Canada, Australia, New Zealand ONLY.
        Focus on trends from 2024-2026.
        
        Output JSON object with key "items".
        Schema: term, group, country (list), category, risk_level, trend_score (40-99), status ('Active'), first_detected, last_updated, context: {{en, ko, ja}}
        """

        payload = {
            "model": "llama-3.3-70b-versatile",
            "messages": [
                {"role": "system", "content": "Output JSON only."},
                {"role": "user", "content": system_prompt}
            ],
            "response_format": {"type": "json_object"}
        }

        try:
            response = requests.post(url, headers=headers, json=payload)
            if response.status_code == 200:
                result = response.json()
                content = result['choices'][0]['message']['content']
                batch_data = json.loads(content).get('items', [])
                
                added = 0
                for item in batch_data:
                    term_key = item['term'].lower().strip()
                    if term_key not in existing_terms:
                        item['term'] = item['term'].strip()
                        item['last_updated'] = get_current_date()
                        current_data.append(item)
                        existing_terms.add(term_key)
                        added += 1
                print(f"   ✅ Added {added} items.")
            else:
                print(f"   ❌ API Error: {response.text}")
        except Exception as e:
            print(f"   ⚠️ Exception: {e}")

        time.sleep(1) # 1초 휴식

    # 저장
    print(f"\n💾 Saving to data.json... Total items: {len(current_data)}")
    with open("data.json", "w", encoding="utf-8") as f:
        json.dump(current_data, f, indent=4, ensure_ascii=False)

if __name__ == "__main__":
    generate_massive_data()
