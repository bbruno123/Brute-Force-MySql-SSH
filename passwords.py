from pathlib import Path

def load_passwords():
    folder = Path(__file__).parent/"wordlists"/"passwords"

    files = []

    for file in folder.iterdir():
        if file.is_file():
            files.append(file)

    for i, file in enumerate(files):
        print(f"{i} - {file.name}")

    option = int(input("\nEscolha a wordlist de senhas: "))

    chosed_file = files[option]

    passwords_ = []

    with open(chosed_file, "r", encoding="utf-8") as f:
        for line in f:
            passwords_.append(line.strip())

    return passwords_