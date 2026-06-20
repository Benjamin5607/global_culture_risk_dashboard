import requests
import csv
import os
from bs4 import BeautifulSoup

os.makedirs("output", exist_ok=True)
OUTPUT = "output/raw_terms_wiktionary.csv"

# 언어별 카테고리 정확한 명칭
LANGS = {
    "ko": "Korean_slang",
    "ja": "Japanese_slang",
    "fr": "French_slang",
    "de": "German_slang",
    "ru": "Russian_slang",
    "es": "Spanish_slang",
    "pt": "Portuguese_slang",
    "it": "Italian_slang"
}

def run():
    print("🚀 Wiktionary Crawling Start...")
    rows = []
    # 봇 차단 방지를 위한 헤더
    headers = {
        "User-Agent": "Mozilla/5.0 (compatible; GlobalSlangBot/1.0)"
    }

    for lang, category in LANGS.items():
        # ✅ [수정] limit=500 파라미터를 URL에 명시적으로 추가
        base_url = f"https://en.wiktionary.org/wiki/Category:{category}"
        
        try:
            # params 딕셔너리로 넘기면 requests가 알아서 ?limit=500을 붙여줌
            res = requests.get(base_url, headers=headers, params={'limit': 500}, timeout=10)
            res.encoding = 'utf-8' # 🛠️ 한글 깨짐 방지
            
            if res.status_code != 200:
                print(f"⚠️ Failed to fetch {lang}: Status {res.status_code}")
                continue
            
            soup = BeautifulSoup(res.text, "html.parser")
            
            # Wiktionary의 단어 목록 그룹 찾기
            category_groups = soup.find_all("div", class_="mw-category-group")
            
            count = 0
            for group in category_groups:
                links = group.find_all("a")
                for link in links:
                    term = link.get_text() # 🛠️ 원어(Native Script) 그대로 가져옴
                    if term:
                        rows.append([
                            term,
                            f"Wiktionary ({category})",
                            "Wiktionary",
                            lang,
                            lang.upper()
                        ])
                        count += 1
            print(f"✅ {lang}: {count} terms collected.")

        except Exception as e:
            print(f"❌ Error in {lang}: {e}")

    # utf-8-sig로 저장해야 엑셀/윈도우에서 안 깨짐
    with open(OUTPUT, "w", newline="", encoding="utf-8-sig") as f:
        writer = csv.writer(f)
        writer.writerow(["term", "definition", "source", "language", "country"])
        writer.writerows(rows)
        
    print(f"🎉 Wiktionary finished. Total {len(rows)} terms saved.")

if __name__ == "__main__":
    run()
