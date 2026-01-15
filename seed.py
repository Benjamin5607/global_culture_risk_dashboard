import os
import json
import requests
import time
import random
from datetime import datetime

API_KEY = os.environ.get("GROQ_API_KEY")

def get_current_date():
    return datetime.now().strftime("%Y-%m-%d")

def generate_risk_data():
    print("🏭 Risk Factory: Mining Public Figures, Groups & Trends...")

    if not API_KEY:
        print("❌ Error: API Key missing.")
        return

    try:
        with open("data.json", "r", encoding="utf-8") as f:
            current_data = json.load(f)
        # 슬랭(language) 데이터는 이제 필요 없으니 제거할 수도 있지만,
        # 일단 기존 데이터는 두고 새 데이터 위주로 갑니다.
    except:
        current_data = []

    existing_terms = {item['term'].lower() for item in current_data}
    print(f"📂 Loaded {len(current_data)} items.")

    # [수정된 주제] 슬랭 제외, 리스크 중심 주제 선정
    prompts = []
    target_countries = ["USA", "UK", "Canada", "Australia", "New Zealand"]
    
    for country in target_countries:
        prompts.append(f"Controversial public figures in {country} (2024-2025)")
        prompts.append(f"Dangerous extremist groups or hate groups in {country}")
        prompts.append(f"Harmful TikTok/Social Media challenges in {country}")
        prompts.append(f"Political conspiracy theories in {country}")

    random.shuffle(prompts)
    
    url = "https://api.groq.com/openai/v1/chat/completions"
    headers = {"Authorization": f"Bearer {API_KEY}", "Content-Type": "application/json"}

    # 10번 배치 실행
    for i, topic in enumerate(prompts[:10]):
        if len(current_data) >= 500: break

        print(f"\n🕵️‍♂️ Analyzing: '{topic}'...")

        # [프롬프트] 이미지 URL 요청 + 명확한 스키마
        system_prompt = f"""
        List 6 items related to "{topic}".
        Focus on high-risk or controversial entities.
        
        Output JSON object with key "items".
        Schema:
        - term: string (Name of person, group, or challenge)
        - group: 'person' | 'group' | 'trend' (Do NOT use 'language')
        - category: string (e.g., 'Politics', 'Hate Speech', 'Viral Challenge')
        - country: list of strings
        - risk_level: 'High' | 'Medium' | 'Low'
        - image_url: string (URL of a public profile image/logo. If unknown, use "null")
        - trend_score: Integer (50-99)
        - context: {{ "en": "Description...", "ko": "Korean translation..." }}
        """

        payload = {
            "model": "llama-3.1-8b-instant",
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
                    # 슬랭이 섞여 들어오면 거름
                    if item.get('group') == 'language': continue

                    if item['term'].lower() not in existing_terms:
                        # 이미지 없으면 null 처리 (프론트엔드에서 아바타로 변환됨)
                        if 'image_url' not in item: item['image_url'] = "null"
                        
                        item['status'] = 'Active'
                        item['last_updated'] = get_current_date()
                        
                        current_data.append(item)
                        existing_terms.add(item['term'].lower())
                        added += 1
                print(f"   ✅ Added {added} risk entities.")
            else:
                print(f"   ❌ API Error: {response.status_code}")

        except Exception as e:
            print(f"   ⚠️ Error: {e}")

        time.sleep(2) # 휴식

    # 저장
    print(f"\n💾 Saving {len(current_data)} items...")
    with open("data.json", "w", encoding="utf-8") as f:
        json.dump(current_data, f, indent=4, ensure_ascii=False)

if __name__ == "__main__":
    generate_risk_data()
