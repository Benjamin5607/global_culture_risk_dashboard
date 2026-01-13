import os
import json
from google import genai # 구형(google.generativeai) 아님!
from datetime import datetime

def analyze_risk():
    try:
        # 1. API 키 가져오기
        api_key = os.environ.get("GEMINI_API_KEY")
        if not api_key:
            raise ValueError("API Key is missing")

        # 2. 신형 클라이언트 연결 (이게 최신 방식)
        client = genai.Client(api_key=api_key)

        # 3. 모델에게 질문 (gemini-1.5-flash 사용)
        response = client.models.generate_content(
            model="gemini-1.5-flash",
            contents="""
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
        )

        # 4. 응답 처리 (JSON 추출)
        # 신형 SDK는 response.text로 바로 접근 가능
        text_response = response.text.replace("```json", "").replace("```", "").strip()
        return json.loads(text_response)

    except Exception as e:
        print(f"❌ Error: {e}")
        # 에러 나도 파일은 만들어서 배포가 멈추지 않게 함
        return {
            "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "risk_score": 0,
            "summary": "System Maintenance: Update in progress",
            "details": [f"Error Log: {str(e)}"]
        }

# 5. 실행 및 저장
if __name__ == "__main__":
    data = analyze_risk()
    with open("data.json", "w", encoding="utf-8") as f:
        json.dump(data, f, indent=4, ensure_ascii=False)
    print("✅ Data saved to data.json")
