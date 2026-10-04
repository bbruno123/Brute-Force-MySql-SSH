from pathlib import Path

folder = Path(__file__).parent
file = folder/"wordlists"/"passwords"/"default-passwords_.txt"

passwords_ = []

with open(file, "r", encoding="utf-8") as f:
    for line in f:
        passwords_.append(line.strip())