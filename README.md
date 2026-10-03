Sim. Para o GitHub reconhecer a estrutura e a formatação, copie **todo o conteúdo abaixo** diretamente para o `README.md`:

 README.md

# BruteForceMySql

 Programa para testes de autenticação em **MySQL** e **SSH**, utilizando uma wordlist configurável e gerenciamento de conexões VPN através do OpenVPN.

 > ⚠️ **Aviso:** utilize este projeto somente em sistemas, contas e ambientes para os quais você tenha autorização explícita para realizar testes de segurança.

 ## 📁 Estrutura do projeto

```
BruteForceMySql/
├── main.py
├── mysql.py
├── passwords.py
├── ssh.py
├── vpn.py
│
├── __pycache__/
│   ├── passwords.cpython-314.pyc
│   ├── Passwords.cpython-314.pyc
│   ├── ssh.cpython-314.pyc
│   └── vpn.cpython-314.pyc
│
├── VPNBook/
│   ├── vpnbook-ca149-tcp443.ovpn
│   ├── vpnbook-ca196-tcp443.ovpn
│   ├── vpnbook-de20-tcp443.ovpn
│   ├── vpnbook-de220-tcp443.ovpn
│   ├── vpnbook-fr200-tcp443.ovpn
│   ├── vpnbook-fr2311-tcp443.ovpn
│   ├── vpnbook-uk205-tcp443.ovpn
│   ├── vpnbook-uk68-tcp443.ovpn
│   ├── vpnbook-us16-tcp443.ovpn
│   └── vpnbook-us178-tcp443.ovpn
│
└── wordlists/
    ├── 100k-most-used-passwords-NCSC_.txt
    ├── 10k-most-common_.txt
    └── default-passwords.txt
```

 > **Nota:** recomendo utilizar `wordlists` em vez de `wordists`, pois é o nome convencional para esse tipo de diretório.

 ## 🔑 Alterando a Wordlist

 A wordlist utilizada pelo programa pode ser alterada no arquivo:

```
passwords.py
```

 No início do arquivo existe:

```
from pathlib import Path

folder = Path(__file__).parent
file = folder / "wordlists" / "100k-most-used-passwords-NCSC_.txt"
```

 Para utilizar outra wordlist, altere apenas o nome do arquivo.

 Por exemplo:

```
file = folder / "wordlists" / "10k-most-common_.txt"
```

 ou:

```
file = folder / "wordlists" / "default-passwords.txt"
```

 ### ➕ Adicionando uma nova Wordlist

 Coloque o arquivo `.txt` dentro da pasta `wordlists/`.

 Exemplo:

```
wordlists/
├── 100k-most-used-passwords-NCSC_.txt
├── 10k-most-common_.txt
├── default-passwords.txt
└── minha-wordlist.txt
```

 Depois, altere `passwords.py`:

```
file = folder / "wordlists" / "minha-wordlist.txt"
```

 ## 🔧 Configuração do `main.py`

 No `main.py`, existe um caminho utilizado para executar `mysql.py` ou `ssh.py`:

```
f"bash -c 'python3 /home/kali/Desktop/BruteForceMySql/{mode}.py; exec bash'"
```

 Se o projeto estiver em outro local, altere:

```
/home/kali/Desktop/BruteForceMySql/
```

 para o diretório correto.

 Por exemplo:

```
f"bash -c 'python3 /home/kali/Projetos/BruteForceMySql/{mode}.py; exec bash'"
```

 ## 🔐 VPN

 As configurações do OpenVPN ficam na pasta:

```
VPNBook/
```

 O projeto possui atualmente 10 arquivos de configuração:

```
vpnbook-ca149-tcp443.ovpn
vpnbook-ca196-tcp443.ovpn
vpnbook-de20-tcp443.ovpn
vpnbook-de220-tcp443.ovpn
vpnbook-fr200-tcp443.ovpn
vpnbook-fr2311-tcp443.ovpn
vpnbook-uk205-tcp443.ovpn
vpnbook-uk68-tcp443.ovpn
vpnbook-us16-tcp443.ovpn
vpnbook-us178-tcp443.ovpn
```

 O gerenciamento das conexões VPN é realizado pelo arquivo:

```
vpn.py
```

 ## ▶️ Execução

 Para iniciar o programa:

```
python3 main.py
```

 O programa solicitará o modo de operação:

```
Escolha (mysql/ssh):
```

 As opções disponíveis são:

```
mysql
ssh
```

 ## 📝 Arquivos principais

 | Arquivo | Função |
| --- | --- |
| `main.py` | Programa principal e seleção do modo |
| `mysql.py` | Módulo relacionado ao MySQL |
| `ssh.py` | Módulo relacionado ao SSH |
| `passwords.py` | Carregamento da wordlist |
| `vpn.py` | Gerenciamento das conexões VPN |
| `VPNBook/` | Arquivos de configuração `.ovpn` |
| `wordlists/` | Wordlists utilizadas pelo projeto |

## ⚠️ Uso autorizado

 Este projeto foi desenvolvido para fins de **estudo, laboratório, CTF e testes de segurança autorizados**.

 Não utilize o programa contra sistemas, servidores ou contas de terceiros sem autorização explícita.

 ## 📄 Licença

 Defina aqui a licença do projeto, caso aplicável.
