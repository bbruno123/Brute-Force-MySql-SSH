from pathlib import Path

folder = Path(__file__).parent
file = folder/"wordlists"/"users"/"top-usernames-shortlist.txt"

users_ = []

with open(file, "r", encoding="utf-8") as f:
    for line in f:
        users_.append(line.strip())