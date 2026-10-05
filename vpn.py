import pexpect
import random
import sys
from pathlib import Path
import requests
from bs4 import BeautifulSoup

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
    response = requests.get(
        "https://www.vpnbook.com/pt/freevpn/openvpn",
        timeout=10,
    )
    response.raise_for_status()
    soup = BeautifulSoup(response.text, "html.parser")
    openvpn_password = next(
        (
            tag.get_text(strip=True)
            for tag in soup.find_all("code")
            if 6 <= len(tag.get_text(strip=True)) <= 20
            and tag.get_text(strip=True) != "vpnbook"
        ),
        None,
    )
    if openvpn_password is None:
        raise RuntimeError("Não foi possível encontrar a senha do OpenVPN.")

    project_dir = Path(__file__).resolve().parent
    for _ in range(5):

        vpn_file = random.choice(vpn_files)

        print(f"\nTentando: {vpn_file}")

        process = pexpect.spawn(
            "sudo",
            [
                "openvpn",
                "--config",
                str(project_dir / "VPNBook" / vpn_file)
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

    raise RuntimeError("Não foi possível conectar à VPN após 5 tentativas.")