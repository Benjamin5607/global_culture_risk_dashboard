import os
import json
from datetime import datetime
from google import genai # Updated library

def update_research():
    api_key = os.getenv("GEMINI_API_KEY")
    if not api_key:
        print("❌ API Key not found.")
        return

    client = genai.Client(api_key=api_key)
    file_path = 'data.json'

    prompt = """
    Research US, UK, AU, CA, NZ markets (Jan 2026). 
    Categories: Public Figure, Risk Term, Algospeak, Dangerous Group, Adult/Substance.
    Requirements:
    - ALL in English.
    - For 'Public Figure', add a Google Image search URL in the 'image_url' field.
    - Return ONLY a JSON array.
    Structure: {"id": 1, "country": "US", "category": "Public Figure", "term": "Name", "risk_level": "High", "context": "Reason", "image_url": "https://www.google.com/search?q=Name&tbm=isch", "last_updated": "2026-01-13"}
    """

    try:
        response = client.models.generate_content(model="gemini-1.5-flash", contents=prompt)
        json_text = response.text.replace('```json', '').replace('```', '').strip()
        new_data = json.loads(json_text)
        
        with open(file_path, 'w', encoding='utf-8') as f:
            json.dump(new_data, f, indent=4)
        print("✅ Success")
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    update_research()
