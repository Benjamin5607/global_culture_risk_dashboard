import os
import json
import requests
from datetime import datetime

def analyze_risk():
    api_key = os.environ.get("GEMINI_API_KEY")
    if not api_key:
        return get_fallback_data("API Key is missing")

    # [모델 변경] 1.5-flash -> gemini-pro (가장 안정적인 모델로 변경)
    url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-pro:generateContent?key={api_key}"
    
    headers = {'Content-Type': 'application/json'}
    payload = {
        "contents": [{
            "parts": [{"text": """
                Analyze the current global geopolitical and economic risks for the next 12 hours.
                Focus on South Korea, USA, China, and Middle East.
                Return the result ONLY in JSON format with the following structure:
                {
                    "timestamp": "YYYY-MM-DD HH:MM:ss",
                    "risk_score": (1-100 integer),
                    "summary": "One sentence summary",
                    "details": ["Bullet point 1", "Bullet point 2", "Bullet point 3"]
                }
            """}]
        }]
    }

    try:
        response = requests.post(url, headers=headers, json=payload)
        
        if response.status_code != 200:
            print(f"❌ API Error: {response.text}")
            return get_fallback_data(f"Google API Error: {response.status_code}")

        result = response.json()
        
        # gemini-pro 응답 구조 안전하게 추출
        try:
            text_response = result['candidates'][0]['content']['parts'][0]['text']
        except (KeyError, IndexError):
            return get_fallback_data("AI Response Structure Changed")
        
        clean_text = text_response.replace("```json", "").replace("```", "").strip()
        return json.loads(clean_text)

    except Exception as e:
        print(f"❌ Connection Error: {e}")
        return get_fallback_data(str(e))

def get_fallback_data(error_msg):
    return {
        "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "risk_score": 0,
        "summary": "System Maintenance",
        "details": [f"Error: {error_msg}"]
    }

if __name__ == "__main__":
    data = analyze_risk()
    with open("data.json", "w", encoding="utf-8") as f:
        json.dump(data, f, indent=4, ensure_ascii=False)
    print("✅ Data saved to data.json")
