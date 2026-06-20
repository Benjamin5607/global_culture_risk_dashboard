import os
import pandas as pd
from github import Github

# =====================
# GitHub 설정
GITHUB_TOKEN = os.environ["GH_PAT"]       # 리포지토리 시크릿
REPO_NAME    = "Benjamin5607/global_culture_risk_dashboard"
COMMIT_MSG   = "Update raw_terms_clean.csv"
FILE_PATH    = "output/raw_terms_clean.csv"
TARGET_PATH  = "output/raw_terms_clean.csv"  # 리포지토리 내 경로
# =====================

# 1️⃣ 파일 읽기
df = pd.read_csv(FILE_PATH)
content = df.to_csv(index=False, encoding="utf-8")

# 2️⃣ GitHub 연결
g = Github(GITHUB_TOKEN)
repo = g.get_repo(REPO_NAME)

# 3️⃣ 기존 파일 확인 후 업데이트 또는 새로 생성
try:
    f = repo.get_contents(TARGET_PATH)
    repo.update_file(f.path, COMMIT_MSG, content, f.sha)
    print(f"✅ {TARGET_PATH} updated in GitHub")
except:
    repo.create_file(TARGET_PATH, COMMIT_MSG, content)
    print(f"✅ {TARGET_PATH} created in GitHub")
