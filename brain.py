import os
import json
import requests
from datetime import datetime

def get_available_model(api_key):
    """
    구글 서버에 '지금 사용 가능한 모델 목록'을 요청해서
    텍스트 생성이 가능한 모델 중 하나를 자동으로 선택합니다.
    """
    url = f"https://generativelanguage.googleapis.com/v1beta/models?key={api_key}"
    
    try:
        response = requests.get(url)
        if response.status_code != 200:
            print(f"⚠️ 모델 목록 조회 실패: {response.text}")
            return "models/gemini-1.5-flash" # 실패 시 기본값 강제 할당

        data = response.json()
        
        # 'generateContent' 기능을 지원하는 모델만 필터링
        for model in data.get('models', []):
            if 'generateContent' in model.get('supportedGenerationMethods', []):
                model_name = model['name']
                # 기왕이면 최신 'gemini' 모델 우선 선택
                if 'gemini' in model_name:
                    print(f"✅ Found available model: {model_name}")
                    return model_name
        
        # 목록은 왔는데 적당한 게 없으면 그냥 첫 번째 놈 선택
        return data['models'][0]['name']

    except Exception as e:
        print(f"⚠️ 모델 탐색 중 에러: {e}")
        return "models/gemini-1.5-flash" # 에러 나면 그냥 이거 씀

def analyze_risk():
    api_key = os.environ.get("GEMINI_API_KEY")
    if not api_key:
        return get_fallback_data("API Key is missing")

    # [핵심] 여기서 '되는 놈'을 잡아옵니다.
    target_model = get_available_model(api_key)
    
    # URL 조립 (모델명이 'models/gemini-pro' 형태이므로 바로 붙임)
    url = f"https://generativelanguage.googleapis.com/v1beta/{target_model}:generateContent?key={api_key}"
    
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
            print(f"❌ API Error ({target_model}): {response.text}")
            return get_fallback_data(f"Google API Error: {response.status_code}")

        result = response.json()
        
        # 응답 추출
        try:
            text_response = result['candidates'][0]['content']['parts'][0]['text']
        except (KeyError, IndexError):
            # 가끔 모델마다 응답 구조가 다를 수 있어서 안전장치
            print(f"❌ Unexpected structure from {target_model}: {result}")
            return get_fallback_data("AI Response Structure Error")
        
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
