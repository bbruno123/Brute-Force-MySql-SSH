import pexpect
import threading
import time
import os

# Remove sinais antigos
if os.path.exists("/tmp/status"):
    os.remove("/tmp/status")

while True:
    mode = input("Escolha (mysql/ssh): ").strip().lower()

    if mode in ("mysql", "ssh"):
        break

    print("Opção inválida. Digite mysql ou ssh.")

with open("/tmp/status", "w") as f:
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
        if os.path.exists("/tmp/status"):
            with open("/tmp/status", "r") as f:
                lines = f.readlines()

            if lines[3].strip() == "True":
                print("mysql.py informou: finded = True")

            # Fecha somente a VPN
            #vpn.openvpn_enter_().close()

            break

        time.sleep(0.5)


thread = threading.Thread(target=finded_, daemon=True)
thread.start()

try:
    # Fica esperando o segundo terminal fechar
    terminal.wait()

    # Se chegou aqui, o terminal foi encerrado
    print("\nSegundo terminal foi fechado.")

    if os.path.exists("/tmp/status"):
        with open("/tmp/status", "r", encoding="utf-8") as f:
            lines = f.readlines()

        i = lines[1].strip() # Lê o valor de i do arquivo
        j = lines[2].strip() # Lê o valor de j do arquivo
        mysql_or_ssh = lines[0].strip() # Lê o valor de mysql_or_ssh do arquivo
        finded = lines[3].strip() # Lê o valor de finded do arquivo
        status = lines[4].strip() # Lê o valor de status do arquivo

        print(f"usuário atual: {i}")
        print(f"senha atual: {j}")
        print(f"modo atual: {mysql_or_ssh}")
        print(f"finded atual: {finded}")
        print(f"status atual: {status}")
            
    else:
        print("Arquivo /tmp/status não encontrado.")

except KeyboardInterrupt:
    print("\nmain.py interrompido.")