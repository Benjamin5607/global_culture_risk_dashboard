import os
import json
from datetime import datetime, timedelta
from google import genai

def update_research():
    api_key = os.getenv("GEMINI_API_KEY")
    if not api_key:
        print("❌ CRITICAL: API Key not found.")
        return

    client = genai.Client(api_key=api_key)
    file_path = 'data.json'

    # 1. 기존 데이터 로드 (기존 3개월치 데이터를 AI에게 학습시킴)
    existing_data = []
    try:
        if os.path.exists(file_path):
            with open(file_path, 'r', encoding='utf-8') as f:
                existing_data = json.load(f)
    except Exception as e:
        print(f"⚠️ Warning: Starting fresh. {e}")

    # 2. 강력한 대량 리서치 프롬프트
    # 한 번의 호출로 최대한 많은 데이터를 뽑아내도록 설정
    current_date = "2026-01-13" 
    
    prompt = f"""
    You are a Senior Cultural Intelligence Lead. Your goal is to build a COMPREHENSIVE risk database for 5 key markets: US, UK, AU, CA, and NZ.

    [Current Database Snapshot (Truncated to last 50 for context)]
    {json.dumps(existing_data[-50:])}

    [MANDATORY MISSION]
    1. **MASSIVE EXPANSION**: Identify and add at least 50-100 NEW entries across all categories. Do not be lazy. Dig deep into niche Algospeak, local scandals, and emerging extremist groups.
    2. **3-MONTH MAINTENANCE**: 
       - Keep high-value historical risks from the past 90일 (3 months).
       - PURGE any data that is objectively dead or irrelevant as of {current_date}.
    3. **CATEGORIES**: Public Figure, Risk Term, Algospeak, Dangerous Group, Adult/Substance.
    4. **ENGLISH ONLY**: Ensure every single field is professional English.
    5. **PUBLIC FIGURE URL**: Use specific search query: https://www.google.com/search?q=[NAME]+[MARKET]+controversy+2026&tbm=isch

    [JSON FORMATTING]
    - Return ONLY a pure JSON array. No conversational text.
    - Fields: "id" (unique), "country", "category", "term", "risk_level" (High/Medium/Low), "context", "image_url", "last_updated" ("{current_date}")
    """

    try:
        # 3. AI 리서치 실행 (Gemini 1.5 Flash는 대량 데이터 생성에 최적화됨)
        response = client.models.generate_content(
            model="gemini-1.5-flash",
            contents=prompt
        )
        
        raw_text = response.text
        # JSON 블록만 정밀하게 추출
        if "```json" in raw_text:
            json_text = raw_text.split("```json")[1].split("```")[0]
        elif "```" in raw_text:
            json_text = raw_text.split("```")[1].split("```")[0]
        else:
            json_text = raw_text.strip()
            
        updated_list = json.loads(json_text)

        # 4. 데이터 중복 제거 및 최종 저장
        # 용어(term)와 국가(country)가 같은 데이터는 최신 것으로 덮어씀
        final_dict = {}
        for item in (existing_data + updated_list):
            # 90일 지난 데이터는 여기서 한 번 더 필터링 (Python 로직)
            try:
                updated_dt = datetime.strptime(item['last_updated'], '%Y-%m-%d')
                if updated_dt > datetime.now() - timedelta(days=90):
                    key = f"{item['country']}-{item['term']}"
                    final_dict[key] = item
            except:
                continue
        
        final_list = list(final_dict.values())

        with open(file_path, 'w', encoding='utf-8') as f:
            json.dump(final_list, f, indent=4, ensure_ascii=False)
            
        print(f"✅ [{datetime.now()}] Database updated. Total entries: {len(final_list)}")

    except Exception as e:
        print(f"❌ Error during massive update: {e}")

if __name__ == "__main__":
    update_research()
