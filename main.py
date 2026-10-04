import pexpect
import threading
import time
import shlex
from pathlib import Path

PROJECT_DIR = Path(__file__).resolve().parent
STATUS_FILE = Path("/tmp/status")

# Remove sinais antigos
if STATUS_FILE.exists():
    STATUS_FILE.unlink()

while True:
    mode = input("Escolha (mysql/ssh): ").strip().lower()

    if mode in ("mysql", "ssh"):
        break

    print("Opção inválida. Digite mysql ou ssh.")

with STATUS_FILE.open("w", encoding="utf-8") as f:
    f.write(f"{mode}\n")
    f.write("0\n")  # Inicializa o valor de i como 0
    f.write("0\n")  # Inicializa o valor de j como 0
    f.write("False\n")  # Inicializa o valor de finded como False
    f.write("Tudo certo!\n")  # Inicializa o valor de status como uma mensagem padrão

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

        if len(lines) < 5:
            print("Arquivo de status incompleto.")
        else:
            i = lines[1].strip()
            j = lines[2].strip()
            mysql_or_ssh = lines[0].strip()
            finded = lines[3].strip()
            status = lines[4].strip()

            print(f"usuário atual: {i}")
            print(f"senha atual: {j}")
            print(f"modo atual: {mysql_or_ssh}")
            print(f"finded atual: {finded}")
            print(f"status atual: {status}")
            
    else:
        print("Arquivo /tmp/status não encontrado.")

except KeyboardInterrupt:
    print("\nmain.py interrompido.")