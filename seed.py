import os
import json
import requests
import time
import random
from datetime import datetime

API_KEY = os.environ.get("GROQ_API_KEY")

def get_current_date():
    return datetime.now().strftime("%Y-%m-%d")

# ==========================================
# [핵심] 얼반 딕셔너리 데이터 크롤링 함수
# ==========================================
def fetch_urban_data(term):
    try:
        # 얼반 딕셔너리 무료 API 호출
        url = f"https://api.urbandictionary.com/v0/define?term={term}"
        response = requests.get(url, timeout=5)
        
        if response.status_code == 200:
            data = response.json()
            items = data.get('list', [])
            
            if not items:
                return None # 검색 결과 없음

            # 좋아요(thumbs_up)가 가장 많은 정의 1등 선택
            best_def = sorted(items, key=lambda x: x.get('thumbs_up', 0), reverse=True)[0]
            
            # 너무 길면 자르기 (300자)
            definition = best_def.get('definition', '').replace('[', '').replace(']', '')
            if len(definition) > 300: definition = definition[:300] + "..."
            
            return definition
    except Exception as e:
        print(f"   ⚠️ Urban Dict Error for '{term}': {e}")
    
    return None

# ==========================================
# 메인 공장 코드
# ==========================================
def generate_hybrid_data():
    print("🏭 Hybrid Factory: AI Search + Urban Dictionary Definitions...")

    if not API_KEY:
        print("❌ Error: GROQ_API_KEY not found.")
        return

    try:
        with open("data.json", "r", encoding="utf-8") as f:
            current_data = json.load(f)
    except:
        current_data = []

    existing_terms = {item['term'].lower() for item in current_data}
    print(f"📂 Loaded {len(current_data)} existing items.")

    # 질문 리스트 (단어 수집용)
    prompts = []
    target_countries = ["USA", "UK", "Canada", "Australia"]
    
    # AI에게는 "단어 리스트"만 달라고 요청합니다. (뜻은 우리가 찾을 거니까)
    for country in target_countries:
        prompts.append(f"Most viral Gen Z slang words in {country} (2024-2025)")
        prompts.append(f"Controversial political dog whistles in {country}")
        prompts.append(f"TikTok trends and acronyms in {country}")

    random.shuffle(prompts)

    url = "https://api.groq.com/openai/v1/chat/completions"
    headers = {"Authorization": f"Bearer {API_KEY}", "Content-Type": "application/json"}

    max_batches = 10
    for i, topic in enumerate(prompts[:max_batches]):
        if len(current_data) >= 500: break
        
        print(f"\n🔄 [{i+1}/{max_batches}] AI: '{topic}' 단어 수집 중...")

        # 프롬프트: AI야, 뜻은 필요 없고 '단어'랑 '카테고리'만 줘.
        system_prompt = f"""
        List 8 viral terms related to "{topic}".
        Only output JSON.
        Schema:
        - term: string
        - category: string (Short hashtag style)
        - country: list of strings
        - group: 'language'
        - risk_level: 'Low' | 'Medium' | 'High'
        - trend_score: Integer (50-99)
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
            # 1. AI가 단어 물어옴
            response = requests.post(url, headers=headers, json=payload)
            if response.status_code == 200:
                content = response.json()['choices'][0]['message']['content']
                ai_items = json.loads(content).get('items', [])
                
                added_count = 0
                for item in ai_items:
                    term = item['term'].strip()
                    
                    if term.lower() not in existing_terms:
                        print(f"   🔎 '{term}' -> Urban Dictionary 검색 중...", end="")
                        
                        # 2. 얼반 딕셔너리에서 진짜 뜻 가져오기
                        urban_def = fetch_urban_data(term)
                        
                        # 데이터 조립
                        item['term'] = term
                        item['image_url'] = "null" # 슬랭은 이미지 불필요
                        item['status'] = 'Active'
                        item['first_detected'] = get_current_date()
                        item['last_updated'] = get_current_date()
                        
                        # 뜻 채워넣기 (얼반 데이터가 있으면 그거 쓰고, 없으면 AI가 준거 쓰거나 'No data')
                        real_def = urban_def if urban_def else "Definition provided by AI analysis."
                        
                        # 언어별 컨텍스트 (한국어는 번역이 없으므로 영어 뜻을 그대로 넣거나 간단히 표시)
                        item['context'] = {
                            "en": real_def,
                            "ko": f"(Urban Dict): {real_def}" if urban_def else "데이터 수집 중...",
                            "ja": real_def
                        }

                        current_data.append(item)
                        existing_terms.add(term.lower())
                        added_count += 1
                        print(" 완료 ✅")
                        
                        # API 과부하 방지 (살짝 쉼)
                        time.sleep(0.5)
                
                print(f"   ✨ 배치 완료: {added_count}개 저장됨.")
            
            else:
                print(f"   ❌ AI Error: {response.text}")

        except Exception as e:
            print(f"   ⚠️ Error: {e}")

        time.sleep(1) # AI API 휴식

    # 저장
    print(f"\n💾 Saving {len(current_data)} items to data.json...")
    with open("data.json", "w", encoding="utf-8") as f:
        json.dump(current_data, f, indent=4, ensure_ascii=False)

if __name__ == "__main__":
    generate_hybrid_data()
