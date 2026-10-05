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
├── users.py
├── vpn_vibe_coded.py
├── requirements.txt
│
├── ovpn_dinamics/
│   └── (arquivos .ovpn gerenciados automaticamente)
│
└── wordlists/
    ├── passwords/ (wordlists incluídas no repositório)
    │
    └── users/ (wordlists incluídas no repositório)
```

 > **Nota:** as wordlists que já estão nas pastas `wordlists/passwords/` e `wordlists/users/` são incluídas no repositório e virão junto com o clone ou download do projeto. Esses diretórios continuam sendo dinâmicos: o usuário pode adicionar ou remover arquivos `.txt` e a quantidade de listas pode mudar ao longo do tempo. Já `ovpn_dinamics/` é um cache de configurações `.ovpn` gerenciado automaticamente.

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

 ## 🔑 Selecionando as Wordlists

 As wordlists de usuários e senhas são encontradas automaticamente dentro de:

```
wordlists/users/
wordlists/passwords/
```

 Ao iniciar o programa, `users.py` e `passwords.py` exibem os arquivos disponíveis e permitem escolher uma wordlist pelo número apresentado. Não é necessário editar o código para trocar a lista.

 Para adicionar uma nova lista, coloque um arquivo de texto na pasta correspondente. O programa encontrará o arquivo automaticamente na próxima execução.

 Os caminhos são calculados a partir da localização dos próprios scripts. O programa pode ser iniciado a partir de outro diretório sem exigir caminhos absolutos manuais.

 ## 🔢 Valores iniciais das Wordlists

 Os módulos `mysql.py` e `ssh.py` solicitam o índice inicial do usuário e da senha:

```
i = int(input("Qual o valor inicial do usuário: "))
j = int(input("Qual o valor inicial da senha: "))
```

 `i` representa a posição inicial na wordlist de usuários e `j` representa a posição inicial na wordlist de senhas.

 Os índices começam em `0`:

```
0 → primeira entrada
1 → segunda entrada
2 → terceira entrada
3 → quarta entrada
```

 Por exemplo:

```
Qual o valor inicial do usuário: 100
Qual o valor inicial da senha: 0
```

 começa no usuário de índice `100` e na senha de índice `0`.

 > **Importante:** `i` é um índice. Portanto, a primeira entrada da lista corresponde a `0`, e não a `1`.

 ## 💾 Acompanhando o status

 Durante a execução, o programa salva o estado atual no arquivo persistente:

```
 status.txt
```

 O arquivo possui oito linhas:

 | Linha | Conteúdo |
 | --- | --- |
 | 1 | Modo atual: `mysql` ou `ssh` |
 | 2 | Índice atual do usuário |
 | 3 | Índice atual da senha |
 | 4 | Indica se uma combinação foi encontrada: `True` ou `False` |
 | 5 | Mensagem atual do programa |
 | 6 | Usuário encontrado, quando uma combinação é localizada |
 | 7 | Senha encontrada, quando uma combinação é localizada |
 | 8 | Host informado para a conexão |

 Para verificar o status pelo terminal:

```
cat status.txt
```

 O arquivo é atualizado durante a execução. As atualizações são feitas por meio de um arquivo temporário, reduzindo o risco de o `main.py` ler o status enquanto ele ainda está sendo gravado.

 Mensagens possíveis na quinta linha incluem:

```
Tudo certo!
Nenhuma combinação encontrada
Muitas tentativas falhadas. Arquivo encerrado
```

 > **Importante:** o arquivo fica na pasta do projeto e não é apagado ao iniciar o programa. Assim, o estado permanece disponível após reinicializações do computador.

 ## 🔌 Configuração da conexão

 Depois de definir o valor inicial, cada módulo solicita as informações necessárias para sua conexão.

 O host informado é salvo na linha 8. Quando uma combinação é encontrada, o módulo imprime o usuário e a senha no terminal. Esses valores também são salvos no `status.txt` nas linhas 6 e 7.

 ### 🔐 SSH

 No modo `ssh`:

```
 Qual o valor inicial do usuário: 0
 Qual o valor inicial da senha: 0
 Qual o destino: servidor.exemplo.com
 Qual a porta: 22
```

 | Entrada | Descrição | Exemplo |
| --- | --- | --- |
| `destino` | Host ou endereço do servidor | `servidor.exemplo.com` |
| `port` | Porta do serviço SSH | `22` |

 O SSH aguarda até 15 segundos por uma resposta antes de registrar um timeout.

 Vários timeouts consecutivos podem ocorrer por causa da distância ou da qualidade da VPN conectada; isso não significa necessariamente que a senha foi recusada.

### 🗄️ MySQL

 No modo `mysql`:

```
 Qual o valor inicial do usuário: 0
 Qual o valor inicial da senha: 0
 Qual o destino: servidor.exemplo.com
Qual a porta: 3306
```

 | Entrada | Descrição | Exemplo |
| --- | --- | --- |
| `destino` | Host ou endereço do servidor MySQL | `servidor.exemplo.com` |
| `port` | Porta do serviço MySQL | `3306` |

 O MySQL aguarda até 15 segundos por uma resposta antes de registrar um timeout.

 Vários timeouts consecutivos podem ocorrer por causa da distância ou da qualidade da VPN conectada; isso não significa necessariamente que a senha foi recusada.

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
vpn_vibe_coded.py
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

 ## 🧩 O que `prepare_vpn_configs()` faz

 `prepare_vpn_configs()` está no arquivo `vpn_vibe_coded.py` e é chamado tanto por `mysql.py` quanto por `ssh.py` antes do início das tentativas de autenticação.

 A função **não abre a conexão VPN diretamente**. Ela prepara e garante que exista um conjunto de pelo menos **3 configurações aprovadas**:

 1. Procura em `ovpn_dinamics/` configurações que já foram aprovadas, cujo conteúdo ainda corresponde ao hash salvo e cuja data de download não tenha mais de **7 dias**.
 2. Remove do diretório e do `vpn_status.json` as configurações expiradas ou que não possuem uma data de download válida.
 3. Reutiliza o cache somente quando existem pelo menos 3 configurações aprovadas e válidas.
 4. Se houver menos de 3 configurações válidas, mesmo que existam algumas aprovadas no cache, consulta a API do VPN Gate e inicia uma nova rodada para completar o conjunto.
 5. Remove duplicatas e acrescenta `remote-cert-tls server` quando a configuração não possui uma verificação equivalente.
 6. Conecta temporariamente em cada configuração nova para testar o túnel, a latência, a perda de pacotes, a estabilidade e, quando configurados, os destinos SSH e MySQL.
 7. Salva cada configuração aprovada em `vpn_status.json` com hash, estado, métricas e o campo `downloaded_at` em UTC.
 8. Se uma rodada aprovar menos configurações do que o necessário, mantém as aprovadas e repete o download e a validação em outra rodada.
 9. Só finaliza quando acumula pelo menos 3 configurações aprovadas; se uma rodada não encontrar nenhuma configuração OpenVPN utilizável ou válida, encerra com erro explícito.

 Depois dessa preparação, `openvpn_enter_()` escolhe uma configuração aprovada e inicia o OpenVPN. Se uma conexão falhar durante a execução, `mysql.py` e `ssh.py` chamam novamente essa rotina por meio de `reconnect_vpn()`.

 ## 🤖 Autoria e recursos adicionais identificados

 `vpn_vibe_coded.py` e este `README.md` foram feitos com auxílio de inteligência artificial. O restante do projeto foi desenvolvido por mim. Esta declaração se refere à autoria dos arquivos e não significa que todos os comportamentos abaixo existiam desde a primeira versão.

 Durante a leitura do código atual, além do fluxo básico de testar combinações de usuário e senha, foram identificados estes recursos adicionais:

 - seleção interativa de wordlists de usuários e senhas;
 - execução do modo escolhido em um segundo terminal XFCE por meio do `main.py`;
 - acompanhamento do índice atual, host, resultado e credenciais encontradas em `status.txt`;
 - suporte a prompts e mensagens de autenticação em português e inglês;
 - reconhecimento de prompts do MySQL, MariaDB e do shell SSH;
 - esperas aleatórias e troca periódica de VPN durante as tentativas;
 - troca de VPN depois de uma sequência de timeouts ou encerramentos inesperados;
 - download automático de configurações pelo VPN Gate;
 - cache persistente de configurações aprovadas em `vpn_status.json`;
 - registro da data de download (`downloaded_at`) e expiração automática após 7 dias;
 - exigência de pelo menos 3 configurações aprovadas antes de reutilizar o cache;
 - repetição de rodadas de download e validação quando o cache ou uma rodada ainda não atingir 3 configurações aprovadas;
 - verificação de hash, remoção de configurações duplicadas e descarte de configurações que falharam;
 - filtragem regional, limite de latência, medição de perda de pacotes e teste opcional de destinos TCP;
 - ordenação das VPNs pela estabilidade medida e escolha aleatória entre as configurações aprovadas.

 Essa lista é uma descrição do que está implementado no estado atual do código; não é uma reconstrução histórica precisa de quando cada item foi adicionado.

 ### Queda da VPN durante a execução

 Se a VPN cair enquanto `mysql.py` ou `ssh.py` estiver rodando, o programa normalmente identifica a falha como `timeout` ou encerramento da conexão (`EOF`). A tentativa atual é perdida, mas o fluxo continua tentando as próximas combinações.

 Depois de 10 falhas consecutivas desse tipo, o programa encerra a conexão VPN antiga e tenta conectar usando outra configuração aprovada. Ele também pode trocar de configuração periodicamente durante a execução.

 Essa recuperação não é garantida em todos os casos. O programa pode ser encerrado com erro se nenhuma configuração VPN aprovada estiver disponível ou se todas as tentativas de reconexão falharem. A queda da VPN também não é monitorada por um processo separado: ela só é percebida quando uma tentativa MySQL ou SSH deixa de responder ou é encerrada.

 ## 🔐 VPN

 As configurações do OpenVPN ficam na pasta:

 ```
 ovpn_dinamics/
 ```

 Essa pasta funciona como cache e pode ser atualizada automaticamente por `prepare_vpn_configs()`. Os arquivos presentes podem mudar conforme os servidores disponíveis no VPN Gate.

 O gerenciamento atual das conexões VPN é realizado pelo arquivo:

```
vpn_vibe_coded.py
```

 A função `openvpn_enter_()` solicita as credenciais `vpn` somente quando uma conexão é iniciada. Importar o módulo `vpn_vibe_coded.py` não inicia uma conexão por si só.

 Os arquivos `.ovpn` são armazenados em `ovpn_dinamics/`, cujo caminho é calculado a partir da localização do projeto. A execução, portanto, não depende da pasta atual do terminal.

 Antes de usar uma configuração, o programa pode consultar a API do VPN Gate, baixar configurações OpenVPN e testá-las. Os testes medem latência, perda de pacotes e estabilidade e podem também verificar os destinos definidos pelas variáveis `VPN_SSH_TARGET` e `VPN_MYSQL_TARGET`, no formato `host:porta`.

 O cache em `vpn_status.json` registra, para cada configuração aprovada, o hash do arquivo, o estado (`approved`), as métricas da validação e a data/hora UTC em `downloaded_at`. Uma configuração é considerada expirada após 7 dias do download. Na próxima execução de `prepare_vpn_configs()`, ela é removida junto com o arquivo `.ovpn`, e o processo de download e validação é executado novamente.

 Mesmo que existam configurações aprovadas no cache, elas só são reutilizadas quando pelo menos 3 continuam válidas. Com menos de 3, o programa mantém as configurações aproveitáveis e busca, baixa e valida novas configurações. Se a primeira rodada não atingir o mínimo, novas rodadas são executadas até acumular 3 configurações aprovadas. Cada configuração aprovada em uma rodada recebe sua própria data `downloaded_at`.

 A conexão pode apresentar timeouts quando o servidor VPN escolhido está distante do destino ou apresenta alta latência, perda de pacotes ou uma rota instável. Durante a execução, `mysql.py` e `ssh.py` reconectam após falhas consecutivas e também trocam periodicamente de configuração.

 Em caso de falha, `openvpn_enter_()` tenta cada configuração aprovada, repetindo cada uma até três vezes. Se todas falharem, as configurações são removidas do cache e o programa inicia uma nova rodada de download e validação antes de tentar novamente. O processo continua até uma configuração estabelecer o túnel ou até ocorrer um erro explícito durante a atualização das configurações.

 ## 📝 Arquivos principais

 | Arquivo | Função |
| --- | --- |
| `main.py` | Programa principal e ponto de entrada |
| `mysql.py` | Módulo relacionado ao MySQL |
| `ssh.py` | Módulo relacionado ao SSH |
| `passwords.py` | Carregamento da wordlist |
| `users.py` | Carregamento da wordlist de usuários |
| `vpn_vibe_coded.py` | Download, validação, cache e conexão das VPNs |
| `requirements.txt` | Dependências externas do Python |
| `ovpn_dinamics/` | Cache de arquivos de configuração `.ovpn` |
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