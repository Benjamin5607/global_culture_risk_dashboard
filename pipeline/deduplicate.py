import os
import pandas as pd
import csv
import re

SOURCE_FILES = [
    "output/raw_terms_urban.csv",
    "output/raw_terms_wiktionary.csv",
    "output/raw_terms_reddit.csv",
    "output/raw_terms_github_lists.csv"
]

os.makedirs("output", exist_ok=True)

dfs = []
for path in SOURCE_FILES:
    if os.path.exists(path) and os.path.getsize(path) > 0:
        try:
            # encoding="utf-8-sig" : 엑셀에서 한글 안 깨지게 하는 마법의 인코딩
            df = pd.read_csv(path, on_bad_lines='skip', encoding="utf-8-sig")
            
            if df.shape[1] >= 5:
                df.columns = ["term", "definition", "source", "language", "country"]
                dfs.append(df)
        except Exception as e:
            print(f"⚠️ Error reading {path}: {e}")

if not dfs:
    print("❌ No data found.")
    exit(0)

full_df = pd.concat(dfs, ignore_index=True)

# 🛠️ [수정됨] 정규화 로직 개선: 영어 외의 문자(한글, 한자 등)도 살림!
# [^\w] : 문자가 아닌 것(공백, 특수문자 등)만 제거. 한글/한자/일본어는 \w에 포함됨.
full_df["normalized"] = full_df["term"].astype(str).apply(lambda x: re.sub(r'[^\w]', '', x.lower()))

# 빈 값 제거 (정규화했더니 아무것도 안 남은 경우 삭제)
full_df = full_df[full_df["normalized"] != ""]

# 중복 제거
full_df = full_df.drop_duplicates(subset=["normalized", "language"], keep='first')

# 저장 (utf-8-sig 사용)
full_df.to_csv("output/raw_terms_clean.csv", index=False, encoding="utf-8-sig", quoting=csv.QUOTE_ALL)
print(f"🎉 Total merged terms: {len(full_df)} (Native Scripts Preserved!)")
