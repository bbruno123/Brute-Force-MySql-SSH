from pathlib import Path

def load_users():
    folder = Path(__file__).parent/"wordlists"/"users"

    files = []

    for file in folder.iterdir():
        if file.is_file():
            files.append(file)

    for i, file in enumerate(files):
        print(f"{i} - {file.name}")

    option = int(input("\nEscolha a wordlist de usuários: "))

    chosed_file = files[option]

    users_ = []

    with open(chosed_file, "r", encoding="utf-8") as f:
        for line in f:
            users_.append(line.strip())

    return users_