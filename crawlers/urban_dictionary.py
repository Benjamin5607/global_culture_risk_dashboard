import requests
import csv
from tqdm import tqdm
import os

os.makedirs("output", exist_ok=True)

OUTPUT = "output/raw_terms_urban.csv"

def fetch_terms(pages=20):
    rows = []
    for page in tqdm(range(1, pages + 1)):
        url = f"https://api.urbandictionary.com/v0/random"
        res = requests.get(url, timeout=10)
        if res.status_code != 200:
            continue

        data = res.json().get("list", [])
        for item in data:
            rows.append([
                item["word"],
                item["definition"].replace("\n", " "),
                "UrbanDictionary",
                "en",
                "US"
            ])
    return rows

def run():
    rows = fetch_terms()
    with open(OUTPUT, "a", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerows(rows)

if __name__ == "__main__":
    run()
