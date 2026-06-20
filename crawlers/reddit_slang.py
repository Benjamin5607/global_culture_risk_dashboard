import requests
import csv
import os
import time

os.makedirs("output", exist_ok=True)
OUTPUT = "output/raw_terms_reddit.csv"

# 은어의 성지 (Subreddits)
SUBREDDITS = [
    "Slang", "GenZ", "InternetSlang", "UrbanDictionary",
    "OutOfTheLoop", "NoStupidQuestions", "Tinder",
    "ExplainLikeImFive", "Twitch", "Fanfiction", "EnglishLearning"
]

def clean_text(text):
    if not text or text == "[deleted]" or text == "[removed]": 
        return ""
    return text.replace("\n", " ").replace('"', '').strip()

def fetch_from_pullpush(subreddit):
    # PullPush API 엔드포인트
    # size=50: 최신글 50개 가져오기
    url = f"https://api.pullpush.io/reddit/search/submission/?subreddit={subreddit}&size=50&sort=desc"
    
    try:
        # 여기는 레딧이 아니라서 그냥 requests로 찔러도 됨 (헤더도 필요 없음)
        res = requests.get(url, timeout=20)
        
        if res.status_code != 200:
            print(f"⚠️ Failed to fetch r/{subreddit} via PullPush: Status {res.status_code}")
            return []
        
        data = res.json()
        posts = data.get("data", [])
        extracted = []
        
        for post in posts:
            title = clean_text(post.get("title", ""))
            selftext = clean_text(post.get("selftext", ""))
            
            # 내용이 없으면 제목만
            if not selftext: selftext = title
            
            # 삭제된 글 제외
            if title == "" or selftext == "": continue
            
            # 데이터 정제
            context = f"[Title] {title} [Context] {selftext[:300]}..."

            extracted.append([
                title, 
                context, 
                f"Reddit (r/{subreddit})", 
                "en", 
                "Global"
            ])
            
        print(f"✅ r/{subreddit}: {len(extracted)} posts collected via PullPush.")
        return extracted

    except Exception as e:
        print(f"❌ Error scraping r/{subreddit}: {e}")
        return []

def run():
    all_rows = []
    print("🚀 Reddit Crawling Start (Backdoor via PullPush)...")
    
    for sub in SUBREDDITS:
        rows = fetch_from_pullpush(sub)
        all_rows.extend(rows)
        # 서버에 부담 안 주게 1초만 쉬기
        time.sleep(1)

    if all_rows:
        with open(OUTPUT, "w", newline="", encoding="utf-8-sig") as f:
            writer = csv.writer(f)
            writer.writerow(["term", "definition", "source", "language", "country"])
            writer.writerows(all_rows)
        print(f"🎉 Reddit crawling finished. Total {len(all_rows)} terms saved.")
    else:
        print("⚠️ No data collected. PullPush might be syncing or down.")

if __name__ == "__main__":
    run()
