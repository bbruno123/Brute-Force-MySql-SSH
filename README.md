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
    ├── passwords/
    │   ├── 100k-most-used-passwords-NCSC_.txt
    │   ├── 10k-most-common_.txt
    │   └── default-passwords_.txt
    │
    └── users/
        ├── top-usernames-shortlist.txt
        └── xato-net-10-million-usernames.txt
```

 > **Nota:** as wordlists são separadas nas pastas `wordlists/passwords/` e `wordlists/users/`.

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
file = folder / "wordlists" / "passwords" / "100k-most-used-passwords-NCSC_.txt"
```

 Para utilizar outra wordlist, altere apenas o nome do arquivo.

 Por exemplo:

```
file = folder / "wordlists" / "passwords" / "10k-most-common_.txt"
```

 ou:

```
file = folder / "wordlists" / "passwords" / "default-passwords_.txt"
```

 ### ➕ Adicionando uma nova Wordlist

 Coloque o arquivo `.txt` dentro da pasta `wordlists/passwords/`.

 Exemplo:

```
wordlists/
└── passwords/
    ├── 100k-most-used-passwords-NCSC_.txt
    ├── 10k-most-common_.txt
    ├── default-passwords_.txt
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

 ## 💾 Acompanhando o status

 Durante a execução, o programa salva o estado atual no arquivo temporário:

```
/tmp/status
```

 O arquivo possui cinco linhas:

 | Linha | Conteúdo |
 | --- | --- |
 | 1 | Modo atual: `mysql` ou `ssh` |
 | 2 | Índice atual do usuário |
 | 3 | Índice atual da senha |
 | 4 | Indica se uma combinação foi encontrada: `True` ou `False` |
 | 5 | Mensagem atual do programa |

 Para verificar o status pelo terminal:

```
cat /tmp/status
```

 O arquivo é atualizado durante a execução. As atualizações são feitas por meio de um arquivo temporário, reduzindo o risco de o `main.py` ler o status enquanto ele ainda está sendo gravado.

 Mensagens possíveis na última linha incluem:

```
Tudo certo!
Nenhuma combinação encontrada
Muitas tentativas falhadas. Arquivo encerrado
```

 > **Importante:** o arquivo fica em `/tmp`, portanto é temporário e pode ser removido pelo sistema operacional, especialmente após reinicializações.

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

### 🔎 Mensagens reconhecidas pelo MySQL

O módulo `mysql.py` reconhece prompts de senha em inglês e português:

```
Enter password:
Digite a senha:
```

Depois do envio da senha, o programa reconhece mensagens de sucesso em inglês e português:

```
Welcome to the MariaDB monitor
Welcome to the MySQL monitor
Bem-vindo ao monitor do MariaDB
Bem-vindo ao monitor do MySQL
```

Também é reconhecido o prompt interativo do banco, por exemplo:

```
mysql>
MariaDB [(none)]>
```

Os erros de autenticação são identificados pelos códigos:

```
ERROR 1698
ERROR 1045
```

O código `1045` normalmente indica que o acesso foi negado para o usuário informado.

### 🔎 Mensagens reconhecidas pelo SSH

O módulo `ssh.py` reconhece prompts de senha em inglês e português:

```
Password:
Senha:
```

Depois de uma autenticação bem-sucedida, são aceitos prompts de shell de usuário comum e de administrador, incluindo formatos como:

```
usuario@servidor:~$
usuario@servidor:/home/usuario$
root@servidor:~#
```

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

 ### 📍 Diretório do projeto

 O diretório dos módulos é obtido a partir da localização do próprio `main.py`. Dessa forma, o projeto pode ser movido para outro diretório sem precisar alterar manualmente um caminho fixo no código.

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

 A consulta da senha do OpenVPN é feita somente quando `openvpn_enter_()` é chamado. Importar o módulo `vpn.py` não inicia a conexão por si só.

 O caminho dos arquivos `.ovpn` é calculado a partir da pasta do projeto, portanto a execução não depende da pasta atual do terminal.

 Em caso de falha, o programa tenta conectar até três vezes. Depois disso, informa:

```
Não foi possível conectar à VPN após 3 tentativas.
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
| `wordlists/passwords/` | Wordlists de senhas utilizadas pelo projeto |
| `wordlists/users/` | Wordlists de usuários utilizadas pelo projeto |

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