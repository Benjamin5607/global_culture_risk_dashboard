import requests
import csv
import os

os.makedirs("output", exist_ok=True)
OUTPUT = "output/raw_terms_github_lists.csv"

# 남의 깃허브 Raw URL 리스트 (지속적으로 추가 가능)
TARGET_URLS = [
    # Google의 'What Do You Love' 프로젝트 욕설 리스트 (유명함)
    {
        "url": "https://raw.githubusercontent.com/zacanger/profane-words/master/words.json",
        "type": "json", 
        "lang": "en"
    },
    # 한국어 욕설 리스트 예시 (실제 URL 확인 필요, 예시임)
    {
        "url": "https://raw.githubusercontent.com/organization/korean-bad-words/master/list.txt",
        "type": "txt",
        "lang": "ko"
    }
    # 여기에 계속 추가하면 됨
]

def fetch_list(target):
    rows = []
    try:
        res = requests.get(target["url"], timeout=10)
        if res.status_code != 200:
            return []

        words = []
        if target["type"] == "json":
            # JSON 리스트 형태라고 가정 ["fuck", "shit", ...]
            import json
            words = res.json()
            if isinstance(words, dict): # 가끔 dict로 되어있는 경우
                words = words.keys()
        else:
            # 줄바꿈으로 구분된 텍스트 파일
            words = res.text.splitlines()

        for w in words:
            clean_w = str(w).strip()
            if clean_w:
                rows.append([
                    clean_w,
                    "Imported from Open Source Blacklist", # 정의는 따로 없으니 출처 표시
                    "GitHub_Raw_List",
                    target["lang"],
                    "Global"
                ])
    except Exception as e:
        print(f"Error processing {target['url']}: {e}")
    
    return rows

def run():
    print("🚀 GitHub List Scavenging Start...")
    all_rows = []
    for target in TARGET_URLS:
        all_rows.extend(fetch_list(target))

    with open(OUTPUT, "w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(["term", "definition", "source", "language", "country"])
        writer.writerows(all_rows)
    
    print(f"✅ Scavenging finished. {len(all_rows)} terms saved.")

if __name__ == "__main__":
    run()
