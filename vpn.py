import pexpect
import random
import sys
import requests
from bs4 import BeautifulSoup

url = "https://www.vpnbook.com/pt/freevpn/openvpn"

response = requests.get(url, timeout=10)
response.raise_for_status()

soup = BeautifulSoup(response.text, "html.parser")

openvpn_password = None

for tag in soup.find_all("code"):
    texto = tag.get_text(strip=True)

    if 6 <= len(texto) <= 20 and texto != "vpnbook":
        openvpn_password = texto
        break

if openvpn_password is None:
    raise RuntimeError("Não foi possível encontrar a senha do OpenVPN.")

vpn_files = [
    "vpnbook-ca149-tcp443.ovpn",
    "vpnbook-fr200-tcp443.ovpn",
    "vpnbook-us16-tcp443.ovpn",
    "vpnbook-ca196-tcp443.ovpn",
    "vpnbook-fr2311-tcp443.ovpn",
    "vpnbook-us178-tcp443.ovpn",
    "vpnbook-de20-tcp443.ovpn",
    "vpnbook-uk205-tcp443.ovpn",
    "vpnbook-de220-tcp443.ovpn",
    "vpnbook-uk68-tcp443.ovpn"
]

def openvpn_enter_():

    while True:

        vpn_file = random.choice(vpn_files)

        print(f"\nTentando: {vpn_file}")

        process = pexpect.spawn(
            "sudo",
            [
                "openvpn",
                "--config",
                f"VPNBook/{vpn_file}"
            ],
            encoding="utf-8",
            timeout=30
        )

        process.logfile = sys.stdout

        try:
            process.expect("Enter Auth Username:")
            process.sendline("vpnbook")

            process.expect("Enter Auth Password:")
            process.sendline(openvpn_password)

            process.expect("Initialization Sequence Completed")

            print("\nVPN conectada!")

            return process

        except pexpect.EOF:
            print("\nOpenVPN encerrou. Tentando outra VPN...")
            process.close()
            continue

        except pexpect.TIMEOUT:
            print("\nTimeout. Tentando outra VPN...")
            process.close()
            continue