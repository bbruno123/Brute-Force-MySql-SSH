import pexpect
import vpn
import threading
import time
import os

# Remove sinais antigos
if os.path.exists("/tmp/manager"):
    os.remove("/tmp/manager")

while True:
    mode = input("Escolha (mysql/ssh): ").strip().lower()

    if mode in ("mysql", "ssh"):
        break

    print("Opção inválida. Digite mysql ou ssh.")

with open("/tmp/manager", "w") as f:
    f.write(f"{mode}\n")
    f.write("0\n")  # Inicializa o valor de i como 0
    f.write("0\n")  # Inicializa o valor de j como 0
    f.write("False\n")  # Inicializa o valor de finded como False
    f.write("Tudo certo!\n")  # Inicializa o valor de status como uma mensagem padrão

# Abre o segundo terminal
terminal = pexpect.spawn(
    "/usr/bin/xfce4-terminal",
    [
        "--disable-server",
        "--title=Segundo Terminal",
        "--command",
        f"bash -c 'python3 /home/kali/Desktop/BruteForce_mysql:ssh/{mode}.py; exec bash'"
    ],
    encoding="utf-8"
)

print("Segundo terminal aberto.")


def finded_():
    while True:
        if os.path.exists("/tmp/manager"):
            with open("/tmp/manager", "r") as f:
                lines = f.readlines()

            if lines[3].strip() == "True":
                print("mysql.py informou: finded = True")

            # Fecha somente a VPN
            vpn.openvpn_enter_().close()

            break

        time.sleep(0.5)


thread = threading.Thread(target=finded_, daemon=True)
thread.start()

try:
    # Fica esperando o segundo terminal fechar
    terminal.wait()

    # Se chegou aqui, o terminal foi encerrado
    print("\nSegundo terminal foi fechado.")

    if os.path.exists("/tmp/manager"):
        with open("/tmp/manager", "r") as f:
            i = f.read().strip()

        print(f"i atual: {i}")
    else:
        print("Arquivo /tmp/manager não encontrado.")

except KeyboardInterrupt:
    print("\nmain.py interrompido.")