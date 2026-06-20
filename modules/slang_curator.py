import json
import os
import requests
from bs4 import BeautifulSoup

GROQ_API_KEY = os.environ.get("GROQ_API_KEY")
client = None

if GROQ_API_KEY:
    try:
        from groq import Groq
        client = Groq(api_key=GROQ_API_KEY)
    except Exception:
        client = None


def get_best_model():
    default_model = "llama-3.1-8b-instant"
    if not client:
        return default_model

    try:
        models = client.models.list()
        available_models = [m.id for m in models.data]
        priority_keywords = [
            "llama-3.3-70b",
            "llama-3.1-70b",
            "llama3-70b",
            "mixtral-8x7b",
            "gemma2-9b",
            "llama-3.1-8b",
        ]

        for keyword in priority_keywords:
            for model_id in available_models:
                if keyword in model_id:
                    return model_id

        for model_id in available_models:
            if "whisper" not in model_id:
                return model_id
    except Exception:
        pass

    return default_model


def mine_info(term, country):
    if country == "KR":
        query = f'site:namu.wiki "{term}" OR "{term}" 뜻 유래'
    elif country == "JP":
        query = f"{term} とは スラング 元ネタ"
    else:
        query = f"{term} slang meaning origin"

    try:
        url = "https://lite.duckduckgo.com/lite/"
        payload = {"q": query, "kl": "wt-wt"}
        headers = {"User-Agent": "Mozilla/5.0"}
        res = requests.post(url, data=payload, headers=headers, timeout=5)
        soup = BeautifulSoup(res.text, "html.parser")
        snippets = []
        for row in soup.select("table:nth-of-type(3) tr .result-snippet"):
            snippets.append(row.get_text(strip=True))
        return " ".join(snippets[:5])
    except Exception:
        return ""


def curate_slang(term, country):
    if not client:
        return {"status": "error", "msg": "GROQ_API_KEY not configured"}

    if not term:
        return {"status": "error", "msg": "No term provided"}

    raw_data = mine_info(term, country)
    prompt = f"""
    You are a professional Slang Curator.
    Analyze the raw data and explain the slang "{term}" ({country}).
    [RAW DATA] {raw_data} [END DATA]
    Return strictly a JSON object:
    {{
        "definition": "Simple definition (Korean for KR/JP, English for others)",
        "origin": "Origin/Nuance (Korean for KR/JP, English for others)",
        "example": "Conversation example"
    }}
    Only JSON.
    """

    try:
        current_best_model = get_best_model()
        chat = client.chat.completions.create(
            messages=[{"role": "user", "content": prompt}],
            model=current_best_model,
        )
        clean_json = (
            chat.choices[0].message.content.replace("```json", "").replace("```", "").strip()
        )
        result = json.loads(clean_json)
        return {"status": "ok", "data": result}
    except Exception as e:
        return {"status": "error", "msg": str(e)}
