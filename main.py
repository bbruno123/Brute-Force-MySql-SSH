import pexpect
import threading
import time
import shlex
from pathlib import Path

PROJECT_DIR = Path(__file__).resolve().parent
STATUS_FILE = PROJECT_DIR / "status.txt"

while True:
    mode = input("Escolha (mysql/ssh): ").strip().lower()

    if mode in ("mysql", "ssh"):
        break

    print("Opção inválida. Digite mysql ou ssh.")

if STATUS_FILE.exists():
    lines = STATUS_FILE.read_text(encoding="utf-8").splitlines(keepends=True)
    lines.extend("\n" for _ in range(8 - len(lines)))
    lines[0] = f"{mode}\n"
else:
    lines = [
        f"{mode}\n",
        "0\n",
        "0\n",
        "False\n",
        "Tudo certo!\n",
        "\n",
        "\n",
        "\n",
    ]
STATUS_FILE.write_text("".join(lines), encoding="utf-8")

# Abre o segundo terminal
module_path = PROJECT_DIR / f"{mode}.py"
terminal = pexpect.spawn(
    "/usr/bin/xfce4-terminal",
    [
        "--disable-server",
        "--title=Segundo Terminal",
        "--command",
        f"python3 {shlex.quote(str(module_path))}"
    ],
    encoding="utf-8"
)

print("Segundo terminal aberto.")


def finded_():
    while True:
        if STATUS_FILE.exists():
            with STATUS_FILE.open("r", encoding="utf-8") as f:
                lines = f.readlines()

            if len(lines) >= 4 and lines[3].strip() == "True":
                print(f"{mode}.py informou: login encontrado")
                return

        time.sleep(0.5)


thread = threading.Thread(target=finded_, daemon=True)
thread.start()

try:
    # Fica esperando o segundo terminal fechar
    terminal.wait()

    # Se chegou aqui, o terminal foi encerrado
    print("\nSegundo terminal foi fechado.")

    if STATUS_FILE.exists():
        with STATUS_FILE.open("r", encoding="utf-8") as f:
            lines = f.readlines()

        if len(lines) < 8:
            print("Arquivo de status incompleto.")
        else:
            i = lines[1].strip()
            j = lines[2].strip()
            mysql_or_ssh = lines[0].strip()
            finded = lines[3].strip()
            status = lines[4].strip()
            user = lines[5].strip()
            password = lines[6].strip()
            host = lines[7].strip()

            print(f"usuário atual: {i}")
            print(f"senha atual: {j}")
            print(f"modo atual: {mysql_or_ssh}")
            print(f"finded atual: {finded}")
            print(f"status atual: {status}")
            if host:
                print(f"host atual: {host}")
            if user:
                print(f"usuário encontrado: {user}")
            if password:
                print(f"senha encontrada: {password}")
            
    else:
        print(f"Arquivo {STATUS_FILE} não encontrado.")

except KeyboardInterrupt:
    print("\nmain.py interrompido.")