import pexpect
import vpn
import threading
import time
import os

# Remove sinais antigos
if os.path.exists("/tmp/mysql_finded"):
    os.remove("/tmp/mysql_finded")

# Remove sinais antigos
#with open("/tmp/mysql_i", "w") as f:
#    f.write("0")

while True:
    mode = input("Escolha (mysql/ssh): ").strip().lower()

    if mode in ("mysql", "ssh"):
        break

    print("Opção inválida. Digite mysql ou ssh.")

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
        if os.path.exists("/tmp/mysql_finded"):
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

    if os.path.exists("/tmp/mysql_i"):
        with open("/tmp/mysql_i", "r") as f:
            i = f.read().strip()

        print(f"i atual: {i}")
    else:
        print("Arquivo /tmp/mysql_i não encontrado.")

except KeyboardInterrupt:
    print("\nmain.py interrompido.")