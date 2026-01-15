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
# [검수관] Urban Dictionary API
# ==========================================
def verify_and_get_definition(term):
    """
    단어가 Urban Dictionary에 있는지 확인하고, 있으면 가장 인기 있는 뜻을 반환.
    없으면 None 반환 (가짜 단어 판별).
    """
    try:
        url = f"https://api.urbandictionary.com/v0/define?term={term}"
        # 타임아웃 3초 (빨리빨리 넘어가기 위해)
        response = requests.get(url, timeout=3)
        
        if response.status_code == 200:
            data = response.json()
            items = data.get('list', [])
            
            if not items:
                return None # 탈락 (사전에 없는 단어)

            # 좋아요 순으로 정렬해서 1등 뜻 가져오기
            best = sorted(items, key=lambda x: x.get('thumbs_up', 0), reverse=True)[0]
            definition = best.get('definition', '').replace('[', '').replace(']', '').replace('\r\n', ' ')
            
            # 너무 길면 자름
            if len(definition) > 250: definition = definition[:250] + "..."
            return definition
            
    except:
        pass
    return None

# ==========================================
# [공장장] 메인 로직
# ==========================================
def run_refinery():
    print("🏭 Slang Refinery Started: Mining 500+ -> Filtering Real Ones...")

    if not API_KEY:
        print("❌ Error: API Key missing.")
        return

    # 기존 데이터 로드
    try:
        with open("data.json", "r", encoding="utf-8") as f:
            current_data = json.load(f)
    except:
        current_data = []

    # 중복 방지 세트
    existing_terms = {item['term'].lower() for item in current_data}
    print(f"📂 Base Data: {len(current_data)} items")

    # ==========================================
    # [1단계] 채굴 전략: 알파벳 + 카테고리 조합으로 쥐어짜기
    # ==========================================
    mining_prompts = []
    
    # 전략 1: 알파벳 A~Z (가장 확실함)
    alphabet = "ABCDEFGHIJKLMNOPQRSTUVWXYZ"
    for char in alphabet:
        mining_prompts.append(f"List 15 trending Gen Z slang words starting with '{char}'")
    
    # 전략 2: 분야별 (보완용)
    niches = ["TikTok Trends", "Gaming Slang", "Crypto Slang", "Dating App Slang", "Corporate Buzzwords"]
    for niche in niches:
        mining_prompts.append(f"List 15 controversial or trending {niche}")

    random.shuffle(mining_prompts)
    
    # 목표: 순수 데이터 200개 이상 확보할 때까지 (기존 포함)
    target_count = 200 
    
    url = "https://api.groq.com/openai/v1/chat/completions"
    headers = {"Authorization": f"Bearer {API_KEY}", "Content-Type": "application/json"}

    # 배포 제한 피하기 위해 최대 30번 루프
    for i, prompt_text in enumerate(mining_prompts[:30]):
        if len(current_data) >= 500: # 최대 500개 차면 스톱
            print("🎉 Storage Full (500 items). Stopping.")
            break

        print(f"\n⛏️  Mining Batch [{i+1}] - Query: {prompt_text}")

        # AI에게는 "단어 리스트"만 요청 (뜻은 필요 없음, 우리가 찾을 거니까)
        system_prompt = f"""
        Provide a list of 15 slang terms related to: "{prompt_text}".
        Return JSON object with key "candidates" (list of strings).
        Example: {{ "candidates": ["Rizz", "Gyatt", "Fanum Tax"] }}
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
            # 1. AI에게 후보군 받기
            response = requests.post(url, headers=headers, json=payload)
            if response.status_code != 200:
                print(f"   ❌ AI Glitch: {response.status_code}")
                time.sleep(5)
                continue

            content = response.json()['choices'][0]['message']['content']
            candidates = json.loads(content).get('candidates', [])
            print(f"   🤖 AI suggested {len(candidates)} candidates.")

            # 2. 검수 시작 (Urban Dictionary Check)
            valid_count = 0
            for term in candidates:
                term = term.strip()
                if term.lower() in existing_terms:
                    continue # 이미 있는 건 패스

                print(f"     🔍 Checking '{term}'...", end="")
                
                # 얼반 딕셔너리 조회
                real_def = verify_and_get_definition(term)
                
                if real_def:
                    # [합격] 데이터 생성
                    new_item = {
                        "term": term,
                        "group": "language", # 기본값
                        "country": ["Global"],
                        "category": "Slang",
                        "risk_level": "Low", # 기본값 (나중에 조정 가능)
                        "trend_score": random.randint(50, 95), # 트렌드 점수 랜덤 부여
                        "status": "Active",
                        "first_detected": get_current_date(),
                        "last_updated": get_current_date(),
                        "image_url": "null",
                        "context": {
                            "en": real_def,
                            "ko": f"(뜻): {real_def}", # 한국어 번역 대신 원문 제공 (정확도 위해)
                            "ja": real_def
                        }
                    }
                    
                    current_data.append(new_item)
                    existing_terms.add(term.lower())
                    valid_count += 1
                    print(" ✅ Valid (Saved)")
                else:
                    # [불합격]
                    print(" ❌ Fake/Unknown (Discarded)")
                
                # API 예의상 0.5초 휴식
                time.sleep(0.5)

            print(f"   ✨ Batch Result: {valid_count}/{len(candidates)} survived.")
            
            # 중간 저장 (혹시 튕길까봐)
            with open("data.json", "w", encoding="utf-8") as f:
                json.dump(current_data, f, indent=4, ensure_ascii=False)

        except Exception as e:
            print(f"   ⚠️ Error: {e}")

        # AI API 휴식
        time.sleep(2)

    print(f"\n💾 Final Save: {len(current_data)} total items.")

if __name__ == "__main__":
    run_refinery()
