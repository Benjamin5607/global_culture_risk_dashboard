import os
import json
import google.generativeai as genai
from datetime import datetime

# 1. API 키 설정 (환경변수에서 가져옴)
API_KEY = os.environ.get("GEMINI_API_KEY")

# 키가 없으면 에러 발생 (로그 확인용)
if not API_KEY:
    raise ValueError("CRITICAL: GEMINI_API_KEY is missing!")

genai.configure(api_key=API_KEY)

# 2. 모델 설정 (가장 안정적인 최신 버전 지정)
# 404 에러 방지를 위해 명확한 모델명 사용
model = genai.GenerativeModel('gemini-1.5-flash')

def analyze_risk():
    # 3. 프롬프트 (리스크 분석)
    prompt = """
    Analyze the current global geopolitical and economic risks for the next 12 hours.
    Focus on South Korea, USA, China, and Middle East.
    Return the result ONLY in JSON format with the following structure:
    {
        "timestamp": "YYYY-MM-DD HH:MM:ss",
        "risk_score": (1-100 integer),
        "summary": "One sentence summary",
        "details": ["Bullet point 1", "Bullet point 2", "Bullet point 3"]
    }
    """

    try:
        # 4. AI에게 요청
        response = model.generate_content(prompt)
        
        # 응답 텍스트에서 JSON 부분만 추출 (가끔 ```json ... ``` 으로 줄 때가 있음)
        text_response = response.text.replace("```json", "").replace("```", "").strip()
        
        return json.loads(text_response)
        
    except Exception as e:
        print(f"Error generating AI response: {e}")
        # 에러 발생 시 기본 데이터 리턴 (빈 파일 방지)
        return {
            "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "risk_score": 0,
            "summary": f"AI Update Failed: {str(e)}",
            "details": ["Check API Key", "Check Model Name", "Check GitHub Actions Log"]
        }

# 5. 실행 및 파일 저장
if __name__ == "__main__":
    risk_data = analyze_risk()
    
    # data.json 파일로 저장
    with open("data.json", "w", encoding="utf-8") as f:
        json.dump(risk_data, f, indent=4, ensure_ascii=False)
        
    print("Risk analysis complete. Data saved to data.json.")
