import os
import json
from datetime import datetime
from google import genai

def update_research():
    # 1. API Key Check
    api_key = os.getenv("GEMINI_API_KEY")
    if not api_key:
        print("❌ CRITICAL: API Key not found in Environment Variables.")
        return

    client = genai.Client(api_key=api_key)
    file_path = 'data.json'

    # 2. Advanced Prompt for Precise Research
    prompt = """
    Identify the most critical cultural risks and influential figures in 5 markets: US, UK, AU, CA, NZ (as of Jan 2026).
    
    [Instructions]
    1. Research Categories: Public Figure, Risk Term, Algospeak, Dangerous Group, Adult/Substance.
    2. Provide at least 3-4 entries per country.
    3. 'Algospeak' must focus on coded words for drugs, weapons, or adult content used on TikTok/Instagram.
    4. ALL output fields must be in English.
    5. For 'Public Figure', generate a direct Google Image search URL in 'image_url'.
    
    [JSON Structure]
    Return ONLY a valid JSON array of objects:
    {
        "id": number,
        "country": "US/UK/AU/CA/NZ",
        "category": "category_name",
        "term": "term_or_name",
        "risk_level": "High/Medium/Low",
        "context": "Detailed explanation of the risk and advice for marketers",
        "image_url": "Search link if Public Figure, otherwise empty string",
        "last_updated": "YYYY-MM-DD"
    }
    """

    try:
        # 3. AI Research Request
        response = client.models.generate_content(
            model="gemini-1.5-flash",
            contents=prompt
        )
        
        # 4. JSON Extraction & Cleaning
        raw_text = response.text
        if "```json" in raw_text:
            json_text = raw_text.split("```json")[1].split("```")[0]
        elif "```" in raw_text:
            json_text = raw_text.split("```")[1].split("```")[0]
        else:
            json_text = raw_text.strip()
            
        new_data = json.loads(json_text)
        
        # 5. Local Save
        with open(file_path, 'w', encoding='utf-8') as f:
            json.dump(new_data, f, indent=4, ensure_ascii=False)
            
        print(f"✅ [{datetime.now()}] Brain updated data.json successfully.")

    except Exception as e:
        print(f"❌ Error during AI processing: {e}")

if __name__ == "__main__":
    update_research()
