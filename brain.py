import os
import json
from datetime import datetime, timedelta
from google import genai

def update_research():
    api_key = os.getenv("GEMINI_API_KEY")
    if not api_key:
        print("❌ API Key not found.")
        return

    client = genai.Client(api_key=api_key)
    file_path = 'data.json'

    # 1. 기존 데이터 로드
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            existing_data = json.load(f)
    except:
        existing_data = []

    # 2. AI에게 '리서치 + 청소' 명령 전달 (영문 데이터 생성)
    prompt = f"""
    You are a Strategic Brand Safety Analyst. Your task is to maintain a rolling 3-month database of cultural risks for US, UK, AU, CA, and NZ.

    [Current Database Content]
    {json.dumps(existing_data)}

    [Task Instructions]
    1. **Review & Purge**: Examine each entry in the current database. Remove any that are:
       - No longer trending or valid as of Jan 2026.
       - Factually outdated or deemed low-risk noise.
       - Older than 90 days (3 months) unless they are critical, long-term risks.
    2. **Research New Items**: Identify 3-5 new, high-impact risks or public figures for each market that emerged recently.
    3. **English Only**: All fields (category, context, terms) MUST be in English.
    4. **Image Search**: For 'Public Figure', provide a Google Image search URL in 'image_url'.

    [JSON Structure]
    Return ONLY a single valid JSON array of objects.
    Structure: {{"id": int, "country": "US/UK/AU/CA/NZ", "category": "category_name", "term": "term", "risk_level": "High/Medium/Low", "context": "Detailed English explanation", "image_url": "URL or empty", "last_updated": "YYYY-MM-DD"}}
    """

    try:
        response = client.models.generate_content(
            model="gemini-1.5-flash",
            contents=prompt
        )
        
        # JSON 텍스트 추출 및 정제
        raw_text = response.text
        json_text = raw_text.replace('```json', '').replace('```', '').strip()
        
        # AI가 내뱉은 전체 리스트(기존 유지분 + 신규)를 저장
        updated_data = json.loads(json_text)
        
        with open(file_path, 'w', encoding='utf-8') as f:
            json.dump(updated_data, f, indent=4, ensure_ascii=False)
            
        print(f"✅ [{datetime.now()}] Database cleaned and updated (3-month rolling window).")

    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    update_research()
