import google.generativeai as genai
import json
import os
from datetime import datetime

# GitHub Secrets에 등록한 API 키를 환경 변수로 가져옵니다
api_key = os.getenv("GEMINI_API_KEY")

if not api_key:
    print("❌ API Key not found. Please check GitHub Secrets.")
    exit(1)

genai.configure(api_key=api_key)
model = genai.GenerativeModel('gemini-1.5-flash')

def update_research():
    file_path = 'data.json'
    
    # 기존 데이터 로드 (없으면 빈 리스트)
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            old_data = json.load(f)
    except:
        old_data = []

    # AI 리서치 프롬프트 (전부 영어로 요청)
    prompt = f"""
    You are a Global Brand Safety & Culture Intelligence Expert. 
    Research and update risk data for 5 markets: US, UK, AU, CA, NZ as of Jan 2026.
    
    [Target Categories]
    - Public Figure
    - Risk Term
    - Algospeak
    - Dangerous Group
    - Adult/Substance

    [Requirements]
    - ALL content MUST be in English.
    - Return ONLY a pure JSON array.
    - Use this exact structure:
      {{"id": number, "country": "US/UK/AU/CA/NZ", "category": "category_name", "term": "term", "risk_level": "High/Medium/Low", "context": "explanation", "last_updated": "2026-01-13"}}

    Current Data for reference: {json.dumps(old_data[-5:])}
    """

    try:
        response = model.generate_content(prompt)
        # JSON 부분만 추출하는 안전장치
        json_text = response.text
        if "```json" in json_text:
            json_text = json_text.split("```json")[1].split("```")[0]
        elif "```" in json_text:
            json_text = json_text.split("```")[1].split("```")[0]
        
        new_data = json.loads(json_text.strip())
        
        # 파일 저장
        with open(file_path, 'w', encoding='utf-8') as f:
            json.dump(new_data, f, indent=4, ensure_ascii=False)
        print(f"✅ Data updated successfully at {datetime.now()}")
        
    except Exception as e:
        print(f"❌ Error during AI research: {e}")
        print(f"Response text was: {response.text if 'response' in locals() else 'No response'}")

if __name__ == "__main__":
    update_research()