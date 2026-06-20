import json
import os

GROQ_API_KEY = os.environ.get("GROQ_API_KEY")
client = None

if GROQ_API_KEY:
    try:
        from groq import Groq
        client = Groq(api_key=GROQ_API_KEY)
    except Exception:
        client = None


def get_available_models():
    if not client:
        return ["llama-3.3-70b-versatile", "llama-3.1-8b-instant"]
    try:
        models = client.models.list()
        return [m.id for m in models.data if "whisper" not in m.id]
    except Exception:
        return ["llama-3.3-70b-versatile", "llama-3.1-8b-instant"]


def get_top_3_risks(scope, model=None):
    if not client:
        return {"status": "error", "msg": "GROQ_API_KEY not configured", "events": []}

    model = model or get_available_models()[0]
    prompt = f"""
    You are a Strategic Risk Analyst.
    Identify the TOP 3 security/political/social risks in '{scope}' from the **PAST 7 DAYS**.

    CRITICAL INSTRUCTIONS:
    1. **NO HALLUCINATION:** Do not invent scenarios. Only list events that are actually reported or widely known in this context.
    2. **INCLUDE LOW RISKS:** If there are no High/Critical risks, you MUST include Medium or Low risks (e.g., minor policy changes, peaceful protests, economic trends). Do not return empty.
    3. **SORTING:** Rank them by severity: High > Medium > Low.

    Return ONLY a valid JSON object with a single key 'events'.

    JSON Structure:
    {{
        "events": [
            {{"title": "Event Title", "risk_level": "High", "summary": "One sentence fact-based summary"}},
            {{"title": "Event Title", "risk_level": "Medium", "summary": "One sentence fact-based summary"}},
            {{"title": "Event Title", "risk_level": "Low", "summary": "One sentence fact-based summary"}}
        ]
    }}
    """

    try:
        completion = client.chat.completions.create(
            model=model,
            messages=[{"role": "user", "content": prompt}],
            temperature=0.1,
            response_format={"type": "json_object"},
        )
        data = json.loads(completion.choices[0].message.content)
        events = data.get("events", [])
        if not events:
            for value in data.values():
                if isinstance(value, list):
                    events = value
                    break
        return {"status": "ok", "events": events}
    except Exception as e:
        return {
            "status": "error",
            "msg": str(e),
            "events": [
                {"title": "Data Unavailable", "risk_level": "Low", "summary": "No verified events found in the last 7 days."},
                {"title": "System Check", "risk_level": "Low", "summary": "Please check API connection or Scope settings."},
                {"title": "Stable Status", "risk_level": "Negligible", "summary": "No major incidents reported recently."},
            ],
        }


def analyze_risk_detail(text, model=None):
    if not client:
        return {"status": "error", "msg": "GROQ_API_KEY not configured"}

    model = model or get_available_models()[0]
    system_prompt = """
    Analyze the input event as a Senior T&S PM using the STAR framework.
    Output FORMAT:
    1. Risk Level: [Level]
    2. Incident Summary (STAR): [Content]
    3. Platform Impact: [Content]
    4. Target Groups: [Content]
    5. Policy Mapping: [Content]
    6. Watchlist Keywords: [Content]
    7. Action Plan: [Content]
    """

    try:
        completion = client.chat.completions.create(
            model=model,
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": text},
            ],
            temperature=0.2,
        )
        return {"status": "ok", "report": completion.choices[0].message.content}
    except Exception as e:
        return {"status": "error", "msg": str(e)}


def get_country_summary(scope, model=None):
    if not client:
        return {"status": "error", "msg": "GROQ_API_KEY not configured"}

    model = model or get_available_models()[0]
    summary_prompt = f"Give a 3-bullet point executive summary of the current stability status of {scope}."

    try:
        summary_res = client.chat.completions.create(
            model=model,
            messages=[{"role": "user", "content": summary_prompt}],
        )
        return {"status": "ok", "summary": summary_res.choices[0].message.content}
    except Exception as e:
        return {"status": "error", "msg": str(e)}
