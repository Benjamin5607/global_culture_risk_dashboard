import csv
import json
import os
import urllib.parse
import urllib.request

from flask import Flask, jsonify, request, send_file

from modules.risk_war_room import (
    analyze_risk_detail,
    get_available_models,
    get_country_summary,
    get_top_3_risks,
)
from modules.slang_curator import curate_slang

app = Flask(__name__)


@app.route("/")
def home():
    return send_file("index.html")


@app.route("/data.json")
def risk_data():
    return send_file("data.json")


@app.route("/output/raw_terms_clean.csv")
def slang_csv():
    return send_file("output/raw_terms_clean.csv")


@app.route("/curate")
def curate():
    term = request.args.get("term", "")
    country = request.args.get("country", "US")
    return jsonify(curate_slang(term, country))


@app.route("/api/risk/top3")
def risk_top3():
    scope = request.args.get("scope", "Global (All)")
    model = request.args.get("model")
    return jsonify(get_top_3_risks(scope, model))


@app.route("/api/risk/analyze", methods=["POST"])
def risk_analyze():
    data = request.get_json(silent=True) or {}
    text = data.get("text", "")
    model = data.get("model")
    return jsonify(analyze_risk_detail(text, model))


@app.route("/api/risk/country")
def risk_country():
    scope = request.args.get("scope", "Global (All)")
    model = request.args.get("model")
    return jsonify(get_country_summary(scope, model))


@app.route("/api/models")
def models():
    return jsonify({"models": get_available_models()})


@app.route("/search")
def urban_search():
    term = request.args.get("term", "")
    if not term:
        return jsonify({"error": "No term provided"}), 400

    target_url = f"https://api.urbandictionary.com/v0/define?term={urllib.parse.quote(term)}"
    try:
        req = urllib.request.Request(target_url, headers={"User-Agent": "Mozilla/5.0"})
        with urllib.request.urlopen(req, timeout=10) as response:
            data = json.loads(response.read().decode())
        return jsonify(data)
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route("/api/slang/stats")
def slang_stats():
    csv_path = "output/raw_terms_clean.csv"
    if not os.path.exists(csv_path):
        return jsonify({"total": 0, "languages": 0, "sources": 0})

    languages = set()
    sources = set()
    total = 0
    with open(csv_path, encoding="utf-8-sig") as f:
        reader = csv.DictReader(f)
        for row in reader:
            total += 1
            if row.get("language"):
                languages.add(row["language"])
            if row.get("source"):
                sources.add(row["source"])

    return jsonify({"total": total, "languages": len(languages), "sources": len(sources)})


if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8080))
    app.run(host="0.0.0.0", port=port)
