import os
import json
from datetime import datetime
from google import genai # 최신 라이브러리

def update_research():
    # GitHub Secrets에서 키 가져오기
    api_key = os.getenv("GEMINI_API_KEY")
    if not api_key:
        print("❌ API Key not found.")
        return

    client = genai.Client(api_key=api_key)
    file_path = 'data.json'

    # 영문 데이터 생성을 위한 프롬프트
    prompt = """
    Research US, UK, AU, CA, NZ markets (current as of Jan 2026). 
    Focus on: Public Figure, Risk Term, Algospeak, Dangerous Group, Adult/Substance.
    
    Requirements:
    - ALL output must be in English.
    - Public Figures: Add a Google Image search link in the 'image_url' field.
    - Risk Terms: Include slang, slurs, and bullying terms.
    - Return ONLY a pure JSON array.
    
    Structure: 
    [{"id": 1, "country": "US", "category": "Public Figure", "term": "Name", "risk_level": "High", "context": "Reason", "image_url": "https://www.google.com/search?q=Name&tbm=isch", "last_updated": "2026-01-13"}]
    """

    try:
        # 모델 실행
        response = client.models.generate_content(
            model="gemini-1.5-flash", 
            contents=prompt
        )
        
        # JSON 텍스트 추출 가공
        raw_text = response.text
        json_text = raw_text.replace('```json', '').replace('```', '').strip()
        new_data = json.loads(json_text)
        
        with open(file_path, 'w', encoding='utf-8') as f:
            json.dump(new_data, f, indent=4)
        print("✅ Success: Data updated.")
        
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    update_research()
