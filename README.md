# BruteForce\_mysql:ssh

 Programa para testes de autenticação em **MySQL** e **SSH**, utilizando uma wordlist configurável e gerenciamento de conexões VPN através do OpenVPN.

 > ⚠️ **Aviso:** utilize este projeto somente em sistemas, contas e ambientes para os quais você tenha autorização explícita para realizar testes de segurança.

 > 🐧 **Sistema operacional:** este projeto foi desenvolvido e testado no **Kali Linux**. Atualmente, seu funcionamento é destinado a sistemas **Linux**. Windows e macOS não são suportados pela implementação atual.

 ## 📁 Estrutura do projeto

```
BruteForce_mysql:ssh/
├── main.py
├── mysql.py
├── passwords.py
├── ssh.py
├── vpn.py
├── requirements.txt
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

 > **Nota:** recomenda-se utilizar `wordlists` em vez de `wordists`, pois esse é o nome convencional para esse tipo de diretório.

 ## 🐧 Compatibilidade com Linux

 O projeto foi **desenvolvido e testado no Kali Linux**.

 A implementação atual depende de ferramentas e caminhos específicos do ambiente Linux.

 | Distribuição | Compatibilidade atual | Observação |
| --- | --- | --- |
| **Kali Linux** | ✅ Testado | Ambiente de desenvolvimento |
| **Debian** | ⚠️ Pode funcionar | Pode exigir instalação/configuração de pacotes |
| **Ubuntu** | ⚠️ Pode funcionar | Pode exigir instalação/configuração de pacotes |
| **Linux Mint** | ⚠️ Pode funcionar | Baseado em Ubuntu/Debian |
| **Pop!\_OS** | ⚠️ Pode funcionar | Baseado em Ubuntu |
| **Fedora** | ⚠️ Pode exigir ajustes | Gerenciador de pacotes e configuração podem ser diferentes |
| **Arch Linux** | ⚠️ Pode exigir ajustes | Instalação de pacotes e caminhos podem variar |
| **openSUSE** | ⚠️ Pode exigir ajustes | Pacotes e configuração podem variar |
| **Windows** | ❌ Não suportado | Implementação atual utiliza recursos específicos do Linux |
| **macOS** | ❌ Não suportado | Implementação atual não foi desenvolvida para macOS |

> **Importante:** "pode funcionar" significa que o código Python é potencialmente compatível, mas a configuração do sistema operacional, pacotes, permissões, OpenVPN e terminal pode exigir ajustes.

 ## 📦 Requisitos

 O projeto utiliza algumas bibliotecas externas do Python.

 As dependências estão listadas em:

```
requirements.txt
```

 Conteúdo:

```
pexpect
requests
beautifulsoup4
```

 As bibliotecas `threading`, `time`, `os`, `random` e `sys` fazem parte da biblioteca padrão do Python e não precisam ser instaladas.

 ### Instalação das dependências Python

 Dentro do diretório do projeto:

```
python3 -m pip install -r requirements.txt
```

 ### 🖥️ Instalação do `xfce4-terminal`

 O `xfce4-terminal` não é uma biblioteca Python e, portanto, não está no `requirements.txt`.

 No Kali/Debian/Ubuntu:

```
sudo apt update
sudo apt install xfce4-terminal
```

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

 ## 🔢 Valor inicial da Wordlist

 Os módulos `mysql.py` e `ssh.py` solicitam o valor inicial:

```
i = int(input("Qual o valor inicial: "))
```

 O valor de `i` representa o **índice da entrada da wordlist** a partir do qual o programa será iniciado.

 Os índices começam em `0`:

```
0 → primeira entrada
1 → segunda entrada
2 → terceira entrada
3 → quarta entrada
```

 Por exemplo:

```
Qual o valor inicial: 0
```

 começa na primeira entrada.

 Já:

```
Qual o valor inicial: 100
```

 começa na entrada de índice `100`, que corresponde à **101ª entrada**.

 > **Importante:** `i` é um índice. Portanto, a primeira entrada da lista corresponde a `0`, e não a `1`.

 ## 💾 Verificando onde o programa parou

 Durante a execução, o programa salva o índice atual no arquivo temporário:

```
/tmp/mysql_i
```

 O código responsável por isso é:

```
with open("/tmp/mysql_i", "w") as f:
    f.write(str(i))
```

 Esse arquivo contém o **índice da última posição registrada** durante a execução.

 Para verificar pelo terminal:

```
cat /tmp/mysql_i
```

 Por exemplo, se aparecer:

```
250
```

 significa que o último índice registrado foi `250`.

 Você também pode verificar o arquivo diretamente com:

```
cat /tmp/mysql_i
```

 > **Importante:** o arquivo fica em `/tmp`, portanto é um arquivo temporário do sistema. Ele pode ser removido pelo sistema operacional, especialmente após reinicializações, dependendo da configuração da distribuição Linux.

 ## 🔌 Configuração da conexão

 Depois de definir o valor inicial, cada módulo solicita as informações necessárias para sua conexão.

 ### 🔐 SSH

 No modo `ssh`:

```
user = str(input("Qual o usuário: "))
destino = str(input("Qual o destino: "))
port = str(input("Qual a porta: "))
```

 | Entrada | Descrição | Exemplo |
| --- | --- | --- |
| `user` | Usuário da conexão SSH | `usuario` |
| `destino` | Host ou endereço do servidor | `servidor.exemplo.com` |
| `port` | Porta do serviço SSH | `22` |

### 🗄️ MySQL

 No modo `mysql`:

```
user = input("Qual o usuário: ")
destino = input("Qual o destino: ")
```

 | Entrada | Descrição | Exemplo |
| --- | --- | --- |
| `user` | Usuário da conexão MySQL | `usuario` |
| `destino` | Host ou endereço do servidor MySQL | `servidor.exemplo.com` |

## 🔧 Configuração do `main.py`

 O projeto deve ser iniciado **sempre pelo `main.py`**.

 Não execute diretamente:

```
mysql.py
ssh.py
vpn.py
```

 Para iniciar:

```
python3 main.py
```

 O `main.py` apresenta:

```
Escolha (mysql/ssh):
```

 As opções disponíveis são:

```
mysql
ssh
```

 O `main.py` então inicia o módulo correspondente.

 ### 📍 Caminho do projeto

 No `main.py`, existe um caminho utilizado para executar `mysql.py` ou `ssh.py`:

```
f"bash -c 'python3 /home/kali/Desktop/BruteForce_mysql:ssh/{mode}.py; exec bash'"
```

 Se o projeto estiver em outro diretório, altere:

```
/home/kali/Desktop/BruteForce_mysql:ssh/
```

 para o caminho correto.

 > Uma melhoria futura seria utilizar `Path(__file__)` para descobrir automaticamente o diretório do projeto e eliminar essa configuração manual.

 ### ▶️ Exemplo de execução

 Entre no diretório do projeto:

```
cd /home/kali/Desktop/BruteForce_mysql:ssh
```

 Instale as dependências:

```
python3 -m pip install -r requirements.txt
```

 Instale o terminal necessário:

```
sudo apt install xfce4-terminal
```

 Depois execute:

```
python3 main.py
```

 Selecione:

```
Escolha (mysql/ssh): ssh
```

 ou:

```
Escolha (mysql/ssh): mysql
```

 > **Importante:** `main.py` é o ponto de entrada do projeto e deve ser utilizado para iniciar a aplicação.

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

 ## 📝 Arquivos principais

 | Arquivo | Função |
| --- | --- |
| `main.py` | Programa principal e ponto de entrada |
| `mysql.py` | Módulo relacionado ao MySQL |
| `ssh.py` | Módulo relacionado ao SSH |
| `passwords.py` | Carregamento da wordlist |
| `vpn.py` | Gerenciamento das conexões VPN |
| `requirements.txt` | Dependências externas do Python |
| `VPNBook/` | Arquivos de configuração `.ovpn` |
| `wordlists/` | Wordlists utilizadas pelo projeto |

## 🐧 Ambiente de desenvolvimento

 Este projeto foi desenvolvido utilizando:

 - **Sistema operacional:** Kali Linux
- **Python:** Python 3
- **Terminal:** XFCE Terminal
- **VPN:** OpenVPN
- **Automação:** Pexpect

 O ambiente principal de desenvolvimento é o **Kali Linux**. Outras distribuições Linux podem exigir adaptações relacionadas a pacotes, permissões, caminhos de executáveis e configuração do OpenVPN.

 ## ⚠️ Uso autorizado

 Este projeto foi desenvolvido para fins de **estudo, laboratório, CTF e testes de segurança autorizados**.

 Não utilize o programa contra sistemas, servidores ou contas de terceiros sem autorização explícita.