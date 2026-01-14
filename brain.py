import os
import json
import requests
import random
from datetime import datetime

# 1. Groq API 키 가져오기
API_KEY = os.environ.get("GROQ_API_KEY")

def get_current_date():
    return datetime.now().strftime("%Y-%m-%d")

def update_database():
    if not API_KEY:
        print("❌ Error: GROQ_API_KEY is missing.")
        return

    print("🚀 Starting Groq AI Agent...")

    # 2. 기존 데이터 로드
    try:
        with open("data.json", "r", encoding="utf-8") as f:
            current_data = json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        current_data = []

    # 3. 주제 랜덤 선택
    topics = [
        "Gen Z Slang", 
        "Controversial Influencer", 
        "Viral TikTok Challenge", 
        "Alt-Right Hate Symbol", 
        "Algospeak (Hidden words)"
    ]
    topic = random.choice(topics)
    print(f"🤖 Researching Topic: {topic}")

    # 4. Groq (Llama3-70b) 요청 설정
    url = "https://api.groq.com/openai/v1/chat/completions"
    
    headers = {
        "Authorization": f"Bearer {API_KEY}",
        "Content-Type": "application/json"
    }

    # 프롬프트: Llama3는 똑똑해서 JSON 구조를 잘 지킵니다.
    system_prompt = """
    You are a cultural risk intelligence analyst. 
    Output MUST be a valid JSON object only. No markdown, no commentary.
    """
    
    user_prompt = f"""
    Find one specific real-world example of a "{topic}" that is currently relevant globally or in the West.
    
    Return a single JSON object with this EXACT schema:
    {{
        "term": "Term Name",
        "group": "Choose one: 'language', 'person', 'group', 'trend'",
        "country": ["Country Code", "e.g. US"],
        "category": "Short Category",
        "risk_level": "High/Medium/Low",
        "trend_score": (Integer 1-100),
        "status": "Active",
        "first_detected": "YYYY-MM-DD",
        "last_updated": "{get_current_date()}",
        "context": {{
            "en": "English explanation (max 2 sentences).",
            "ko": "Korean explanation (max 2 sentences).",
            "ja": "Japanese explanation (max 2 sentences)."
        }}
    }}
    """

    payload = {
        "model": "llama3-70b-8192", # Llama 3 70B (똑똑하고 빠름)
        "messages": [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt}
        ],
        "temperature": 0.7,
        "response_format": {"type": "json_object"} # JSON 강제 모드 (핵심!)
    }

    try:
        # 5. API 호출
        response = requests.post(url, headers=headers, json=payload)
        
        if response.status_code != 200:
            print(f"❌ Groq API Error: {response.text}")
            return

        result = response.json()
        content = result['choices'][0]['message']['content']
        
        # JSON 파싱
        new_entry = json.loads(content)
        
        # 6. 중복 검사 및 저장
        existing_terms = {item['term'] for item in current_data}
        
        if new_entry['term'] in existing_terms:
            print(f"⚠️ Duplicate: {new_entry['term']}. Skipping.")
        else:
            current_data.insert(0, new_entry)
            # 데이터 50개 유지
            if len(current_data) > 50:
                current_data = current_data[:50]
                
            with open("data.json", "w", encoding="utf-8") as f:
                json.dump(current_data, f, indent=4, ensure_ascii=False)
            print(f"✅ Success! Added: {new_entry['term']}")

    except Exception as e:
        print(f"❌ Python Error: {e}")

if __name__ == "__main__":
    update_database()
