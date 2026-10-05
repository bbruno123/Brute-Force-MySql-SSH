import base64
import binascii
import csv
from datetime import datetime, timedelta, timezone
import hashlib
import io
import json
import os
import random
import re
import socket
import subprocess
import sys
import time
from pathlib import Path

import pexpect
import requests


API_URL = "https://www.vpngate.net/api/iphone/"
VPN_DIRECTORY = Path(__file__).resolve().parent / "ovpn_dinamics"
STATUS_FILE = Path("/tmp/vpn_status.json")
REQUEST_TIMEOUT = 60
MAX_PING_MS = 300
MIN_VALID_CONFIGS = 3
MAX_DOWNLOAD_CANDIDATES = 35
PING_COUNT = 5
PING_TIMEOUT_SECONDS = 3
STABILITY_SECONDS = 5
MAX_PACKET_LOSS_PERCENT = 1.0
CONFIG_MAX_AGE = timedelta(days=7)

COUNTRY_TIERS = [
    ("BR",),
    ("AR", "UY", "PY", "CL", "BO", "PE", "CO", "EC", "VE"),
    ("MX", "GT", "CR", "PA", "DO", "PR"),
    ("US", "CA"),
    ("GB", "DE", "FR", "NL", "ES", "PT", "IT", "CH", "SE", "NO", "FI"),
    ("AU", "NZ", "JP", "SG"),
]
PREFERRED_COUNTRIES = [country for tier in COUNTRY_TIERS for country in tier]
PREFERRED_COUNTRY_SET = frozenset(PREFERRED_COUNTRIES)


def _field(server, name):
    return (server.get(name) or "").strip()


def _read_servers(response_text):
    lines = response_text.lstrip("\ufeff").splitlines()
    header_index = next(
        (
            index
            for index, line in enumerate(lines)
            if line.lstrip().startswith("#HostName,")
        ),
        None,
    )
    if header_index is None:
        raise RuntimeError("Cabeçalho #HostName não encontrado na API.")

    header = lines[header_index].lstrip()[1:]
    reader = csv.DictReader(
        io.StringIO("\n".join([header, *lines[header_index + 1 :]]))
    )
    required_columns = {"CountryShort", "OpenVPN_ConfigData_Base64"}
    missing = required_columns.difference(reader.fieldnames or [])
    if missing:
        raise RuntimeError(f"Colunas ausentes na API: {', '.join(sorted(missing))}")

    return list(reader)


def _ping_value(server):
    try:
        return int(_field(server, "Ping"))
    except ValueError:
        return 10**9


def _speed_value(server):
    try:
        return int(_field(server, "Speed"))
    except ValueError:
        return 0


def _country_priority(country):
    normalized = country.upper()
    for tier, countries in enumerate(COUNTRY_TIERS):
        if normalized in countries:
            return tier, countries.index(normalized)
    return len(COUNTRY_TIERS), 0


def _server_endpoint_key(server):
    address = _field(server, "IP") or _field(server, "HostName")
    return (
        (address.lower(), _field(server, "Port")),
    )


def _download_servers():
    response = requests.get(
        API_URL,
        headers={"User-Agent": "VPNGate dynamic OpenVPN client"},
        timeout=REQUEST_TIMEOUT,
    )
    response.raise_for_status()
    servers = _read_servers(response.content.decode("utf-8-sig", errors="replace"))

    candidates = []
    for server in servers:
        country = _field(server, "CountryShort").upper()
        if country not in PREFERRED_COUNTRY_SET:
            continue
        if not _field(server, "OpenVPN_ConfigData_Base64"):
            continue
        if _ping_value(server) > MAX_PING_MS:
            continue
        candidates.append(server)

    candidates.sort(
        key=lambda server: (
            *_country_priority(_field(server, "CountryShort")),
            _ping_value(server),
            -_speed_value(server),
        )
    )
    usable_servers = []
    known_endpoints = set()
    for server in candidates:
        endpoint = _server_endpoint_key(server)
        if endpoint in known_endpoints:
            continue
        known_endpoints.add(endpoint)
        usable_servers.append(server)

    regional_servers = [
        server
        for server in usable_servers
        if _country_priority(_field(server, "CountryShort"))[0] <= 2
    ]
    if len(regional_servers) >= MIN_VALID_CONFIGS:
        usable_servers = regional_servers

    return usable_servers


def _save_config(server, number):
    config = _decode_config(server)
    VPN_DIRECTORY.mkdir(parents=True, exist_ok=True)
    hostname = _field(server, "HostName") or f"server_{number}"
    safe_hostname = "".join(
        character if character.isalnum() or character in "-_" else "_"
        for character in hostname
    )
    path = VPN_DIRECTORY / f"{number:02d}_{safe_hostname}.ovpn"
    path.write_bytes(config)
    return path


def _decode_config(server):
    encoded = "".join(_field(server, "OpenVPN_ConfigData_Base64").split())
    try:
        config = base64.b64decode(encoded, validate=True)
    except (binascii.Error, ValueError) as error:
        raise ValueError(f"configuração Base64 inválida: {error}") from error

    if not config.strip():
        raise ValueError("configuração OpenVPN vazia")
    return _ensure_server_certificate_verification(config)


def _ensure_server_certificate_verification(config):
    active_lines = [
        line.strip()
        for line in config.splitlines()
        if line.strip() and not line.lstrip().startswith(b"#")
    ]
    if any(
        line.startswith((b"remote-cert-tls ", b"verify-x509-name "))
        for line in active_lines
    ):
        return config
    return config.rstrip() + b"\nremote-cert-tls server\n"


def _config_digest(config):
    return hashlib.sha256(config).digest()


def _file_digest(config_path):
    return _config_digest(config_path.read_bytes())


def _load_status():
    if not STATUS_FILE.exists():
        return {}
    try:
        data = json.loads(STATUS_FILE.read_text())
    except (OSError, json.JSONDecodeError) as error:
        print(f"Não foi possível ler {STATUS_FILE}: {error}")
        return {}
    configs = data.get("configs", {})
    if not isinstance(configs, dict):
        return {}
    configs.pop("__rejected__", None)
    return configs


def _save_status(status):
    status = {
        name: entry
        for name, entry in status.items()
        if name != "__rejected__" and isinstance(entry, dict)
    }
    payload = json.dumps(
        {"version": 1, "configs": status},
        ensure_ascii=False,
        indent=2,
        sort_keys=True,
    )
    try:
        STATUS_FILE.write_text(payload + "\n")
    except OSError as error:
        print(f"Não foi possível atualizar {STATUS_FILE}: {error}")


def _status_entry(digest, state, metrics=None, downloaded_at=None):
    entry = {"digest": digest.hex(), "state": state}
    if metrics is not None:
        entry["metrics"] = metrics
    if downloaded_at is not None:
        entry["downloaded_at"] = downloaded_at
    return entry


def _utc_timestamp():
    return datetime.now(timezone.utc).isoformat()


def _is_config_expired(entry, now=None):
    downloaded_at = entry.get("downloaded_at")
    if not isinstance(downloaded_at, str):
        return True
    try:
        downloaded_time = datetime.fromisoformat(downloaded_at)
    except ValueError:
        return True
    if downloaded_time.tzinfo is None:
        downloaded_time = downloaded_time.replace(tzinfo=timezone.utc)
    return (now or datetime.now(timezone.utc)) - downloaded_time > CONFIG_MAX_AGE


def _discard_expired_configs(status):
    now = datetime.now(timezone.utc)
    expired = []
    for name, entry in list(status.items()):
        if not name.endswith(".ovpn") or not _is_config_expired(entry, now):
            continue
        config_path = VPN_DIRECTORY / name
        try:
            config_path.unlink()
            print(f"Configuração expirada removida: {name}")
        except FileNotFoundError:
            pass
        except OSError as error:
            print(f"Não foi possível remover configuração expirada {name}: {error}")
            continue
        status.pop(name, None)
        expired.append(name)
    return expired


def _config_endpoint_key(config_path):
    remotes = []
    for line in config_path.read_text(errors="replace").splitlines():
        fields = line.split()
        if not fields or fields[0].startswith("#"):
            continue
        if fields[0] == "remote" and len(fields) >= 2:
            remotes.append(tuple(fields[1:3]))
    return tuple(sorted(remotes))


def _connect(config_path):
    process = pexpect.spawn(
        "sudo",
        ["openvpn", "--config", str(config_path)],
        encoding="utf-8",
        timeout=30,
    )
    process.logfile = sys.stdout

    try:
        while True:
            result = process.expect(
                [
                    "Initialization Sequence Completed",
                    r"Enter Auth Username:",
                    r"Enter Auth Password:",
                    pexpect.EOF,
                    pexpect.TIMEOUT,
                ]
            )
            if result == 0:
                print("\nVPN conectada!")
                return process
            if result == 1:
                process.sendline("vpn")
                continue
            if result == 2:
                process.sendline("vpn")
                continue

            process.close(force=True)
            return None
    except (pexpect.EOF, pexpect.TIMEOUT, OSError):
        process.close(force=True)
        return None


def _disconnect(process):
    try:
        process.close(force=True)
    except OSError as error:
        print(f"Falha ao encerrar a conexão de verificação: {error}")


def _ping_metrics():
    target = os.getenv("VPN_TEST_TARGET", "1.1.1.1")
    command = [
        "ping",
        "-n",
        "-c",
        str(PING_COUNT),
        "-W",
        str(PING_TIMEOUT_SECONDS),
        target,
    ]
    try:
        result = subprocess.run(
            command,
            capture_output=True,
            text=True,
            timeout=(PING_COUNT * PING_TIMEOUT_SECONDS) + 5,
            check=False,
        )
    except (OSError, subprocess.TimeoutExpired) as error:
        raise RuntimeError(f"teste de ping falhou: {error}") from error

    output = f"{result.stdout}\n{result.stderr}"
    loss_match = re.search(r"(\d+(?:\.\d+)?)%\s*packet loss", output)
    average_match = re.search(
        r"(?:rtt|round-trip).*=\s*"
        r"([0-9.]+)/([0-9.]+)/([0-9.]+)/",
        output,
    )
    if not loss_match or not average_match or result.returncode != 0:
        raise RuntimeError("não foi possível medir perda e latência do ping")

    average = float(average_match.group(2))
    maximum = float(average_match.group(3))
    return {
        "loss": float(loss_match.group(1)),
        "average": average,
        "maximum": maximum,
        "jitter": maximum - average,
    }


def _target_from_environment(name):
    value = os.getenv(name, "").strip()
    if not value:
        return None
    if ":" not in value:
        raise ValueError(f"{name} deve estar no formato host:porta")
    host, port = value.rsplit(":", 1)
    try:
        return host, int(port)
    except ValueError as error:
        raise ValueError(f"porta inválida em {name}: {port}") from error


def _check_tcp_target(name):
    target = _target_from_environment(name)
    if target is None:
        return True
    try:
        with socket.create_connection(target, timeout=5):
            return True
    except OSError as error:
        print(f"{name} indisponível: {error}")
        return False


def _validate_connected_config():
    metrics = _ping_metrics()
    if metrics["average"] > MAX_PING_MS:
        raise RuntimeError(
            f"ping médio acima do limite: {metrics['average']:.1f} ms"
        )
    if metrics["loss"] > MAX_PACKET_LOSS_PERCENT:
        raise RuntimeError(f"perda de pacotes: {metrics['loss']:.1f}%")
    if not _check_tcp_target("VPN_SSH_TARGET"):
        raise RuntimeError("teste SSH falhou")
    if not _check_tcp_target("VPN_MYSQL_TARGET"):
        raise RuntimeError("teste MySQL falhou")
    time.sleep(STABILITY_SECONDS)
    return metrics


def _validate_configs(configs, priorities=None):
    priorities = priorities or {}
    approved = []
    for config_path in configs:
        print(f"\nValidando estabilidade: {config_path.name}")
        process = None
        try:
            process = _connect(config_path)
            if process is None:
                raise RuntimeError("não foi possível estabelecer o túnel")
            metrics = _validate_connected_config()
            approved.append((config_path, metrics))
            print(
                f"Configuração aprovada: perda {metrics['loss']:.1f}%, "
                f"ping médio {metrics['average']:.1f} ms"
            )
        except (OSError, RuntimeError, ValueError) as error:
            print(f"Configuração rejeitada: {error}")
            try:
                config_path.unlink()
            except OSError as unlink_error:
                print(f"Não foi possível remover {config_path.name}: {unlink_error}")
        finally:
            if process is not None:
                _disconnect(process)

    return sorted(
        approved,
        key=lambda item: (
            item[1]["loss"],
            item[1]["jitter"],
            item[1]["average"],
            priorities.get(item[0], (len(COUNTRY_TIERS), 0)),
        ),
    )


def _check_existing_configs():
    if not VPN_DIRECTORY.exists():
        return [], _load_status()

    valid_configs = []
    status = _load_status()
    known_digests = set()
    known_endpoints = set()
    to_validate = []
    for config_path in sorted(VPN_DIRECTORY.glob("*.ovpn")):
        print(f"\nVerificando configuração existente: {config_path.name}")
        try:
            original_config = config_path.read_bytes()
            hardened_config = _ensure_server_certificate_verification(original_config)
            if hardened_config != original_config:
                config_path.write_bytes(hardened_config)
            digest = _file_digest(config_path)
            endpoint = _config_endpoint_key(config_path)
        except (OSError, ValueError) as error:
            print(f"Falha ao verificar {config_path.name}: {error}")
            continue

        if digest in known_digests or endpoint in known_endpoints:
            try:
                config_path.unlink()
                status.pop(config_path.name, None)
                print(f"Duplicata removida: {config_path.name}")
            except OSError as error:
                print(f"Não foi possível remover {config_path.name}: {error}")
            continue

        known_digests.add(digest)
        known_endpoints.add(endpoint)
        cached = status.get(config_path.name)
        if (
            isinstance(cached, dict)
            and cached.get("digest") == digest.hex()
            and cached.get("state") == "approved"
        ):
            print(f"Estado reutilizado: {config_path.name}")
            valid_configs.append(config_path)
            continue
        if (
            isinstance(cached, dict)
            and cached.get("digest") == digest.hex()
            and cached.get("state") == "rejected"
        ):
            print(f"Configuração rejeitada anteriormente: {config_path.name}")
            try:
                config_path.unlink()
                status.pop(config_path.name, None)
            except OSError as error:
                print(f"Não foi possível remover {config_path.name}: {error}")
            continue
        to_validate.append((config_path, digest, endpoint))

    if to_validate:
        validated = _validate_configs([path for path, _, _ in to_validate])
        approved_paths = {path for path, _ in validated}
        metrics_by_path = {path: metrics for path, metrics in validated}
        for config_path, digest, endpoint in to_validate:
            if config_path in approved_paths:
                valid_configs.append(config_path)
                status[config_path.name] = _status_entry(
                    digest,
                    "approved",
                    metrics_by_path[config_path],
                    cached.get("downloaded_at", _utc_timestamp())
                    if isinstance(cached, dict)
                    else _utc_timestamp(),
                )
            else:
                status.pop(config_path.name, None)

    existing_names = {path.name for path in VPN_DIRECTORY.glob("*.ovpn")}
    status = {
        name: entry
        for name, entry in status.items()
        if name in existing_names
    }
    _save_status(status)
    return valid_configs, status


def _next_config_number(configs):
    numbers = []
    for config_path in configs:
        prefix = config_path.name.split("_", 1)[0]
        if prefix.isdigit():
            numbers.append(int(prefix))
    return max(numbers, default=0) + 1


def _update_vpn_configs_once():
    """Baixa, valida e atualiza o cache de configurações VPN."""
    configs, status = _check_existing_configs()
    print("Consultando servidores VPN atuais...")

    try:
        servers = _download_servers()
    except (requests.RequestException, RuntimeError, UnicodeError, csv.Error) as error:
        raise RuntimeError(f"Não foi possível consultar o VPN Gate: {error}") from error

    if not servers:
        raise RuntimeError("A API não retornou servidores OpenVPN utilizáveis.")

    print(
        f"{len(servers)} servidores próximos ao Brasil com ping de até "
        f"{MAX_PING_MS} ms encontrados; baixando no máximo "
        f"{MAX_DOWNLOAD_CANDIDATES} novas configurações."
    )

    first_new_number = _next_config_number(configs)
    known_digests = set()
    known_endpoints = set()
    priorities = {}
    downloaded_count = 0
    new_metadata = {}
    for config_path in configs:
        try:
            known_digests.add(_file_digest(config_path))
            known_endpoints.add(_config_endpoint_key(config_path))
        except OSError as error:
            print(f"Não foi possível ler {config_path.name}: {error}")

    for server in servers:
        if downloaded_count >= MAX_DOWNLOAD_CANDIDATES:
            break
        hostname = _field(server, "HostName") or "desconhecido"
        country = _field(server, "CountryShort") or "??"

        try:
            config = _decode_config(server)
            digest = _config_digest(config)
            endpoint = _server_endpoint_key(server)
            if digest in known_digests or endpoint in known_endpoints:
                print("Configuração duplicada; download ignorado.")
                continue
            downloaded_count += 1
            download_number = downloaded_count
            config_number = first_new_number + download_number - 1
            print(
                f"\nBaixando {download_number}/{MAX_DOWNLOAD_CANDIDATES}: "
                f"{hostname} ({country}, ping {_field(server, 'Ping') or '??'} ms)"
            )
            config_path = _save_config(server, config_number)
            configs.append(config_path)
            known_digests.add(digest)
            known_endpoints.add(endpoint)
            priorities[config_path] = _country_priority(country)
            status.pop(config_path.name, None)
            new_metadata[config_path] = (digest, endpoint, _utc_timestamp())
        except (OSError, ValueError) as error:
            print(f"Configuração ignorada: {error}")
            continue

    if not configs:
        raise RuntimeError("Nenhuma configuração OpenVPN válida foi baixada.")

    new_configs = [
        config_path
        for config_path in configs
        if config_path.name not in status
    ]
    approved_new = _validate_configs(new_configs, priorities)
    approved_by_path = {path: metrics for path, metrics in approved_new}
    for config_path in new_configs:
        digest, endpoint, downloaded_at = new_metadata[config_path]
        if not config_path.exists():
            status.pop(config_path.name, None)
        elif config_path in approved_by_path:
            status[config_path.name] = _status_entry(
                digest,
                "approved",
                approved_by_path[config_path],
                downloaded_at,
            )
        else:
            status.pop(config_path.name, None)
    status = {
        name: entry
        for name, entry in status.items()
        if (VPN_DIRECTORY / name).exists()
    }
    _save_status(status)
    approved = [
        (
            config_path,
            status[config_path.name].get("metrics", {}),
        )
        for config_path in configs
        if config_path.name in status
        and status[config_path.name].get("state") == "approved"
        and config_path.exists()
    ]
    if len(approved) < MIN_VALID_CONFIGS:
        print(
            f"Apenas {len(approved)} configuração(ões) passaram na validação; "
            f"não foi possível atingir a meta de {MIN_VALID_CONFIGS}."
        )
    if not approved:
        raise RuntimeError("Nenhuma configuração VPN passou nos testes de estabilidade.")

    print(f"{len(approved)} configuração(ões) aprovadas e disponíveis.")
    return [config_path for config_path, _ in approved]


def update_vpn_configs():
    """Repete download e validação até reunir o mínimo de VPNs aprovadas."""
    while True:
        approved = _update_vpn_configs_once()
        if len(approved) >= MIN_VALID_CONFIGS:
            return approved
        print(
            f"Apenas {len(approved)} configuração(ões) aprovadas; "
            f"é necessário atingir {MIN_VALID_CONFIGS}. "
            "Iniciando outra rodada de download e validação..."
        )


def _discard_cached_config(config_path, status, reason):
    print(f"Removendo configuração desaprovada {config_path.name}: {reason}")
    status.pop(config_path.name, None)
    try:
        config_path.unlink()
    except FileNotFoundError:
        pass
    except OSError as error:
        print(f"Não foi possível remover {config_path.name}: {error}")
    _save_status(status)


def _approved_cached_configs():
    status = _load_status()
    approved = []
    for config_path in sorted(VPN_DIRECTORY.glob("*.ovpn")):
        cached = status.get(config_path.name)
        if not isinstance(cached, dict) or cached.get("state") != "approved":
            continue
        try:
            if cached.get("digest") != _file_digest(config_path).hex():
                continue
        except OSError as error:
            print(f"Não foi possível ler {config_path.name}: {error}")
            continue
        approved.append(config_path)
    return approved


def prepare_vpn_configs():
    """Garante VPNs aprovadas no cache sem iniciar uma conexão OpenVPN."""
    status = _load_status()
    expired = _discard_expired_configs(status)
    if expired:
        _save_status(status)

    approved = _approved_cached_configs()
    if len(approved) >= MIN_VALID_CONFIGS:
        print(f"{len(approved)} configuração(ões) aprovadas no cache.")
        return approved

    print(
        f"Apenas {len(approved)} configuração(ões) aprovadas no cache; "
        f"é necessário ter pelo menos {MIN_VALID_CONFIGS}. "
        "Atualizando VPNs..."
    )
    return update_vpn_configs()


def openvpn_enter_():
    """Conecta aleatoriamente usando configurações aprovadas no cache."""
    status = _load_status()
    approved = _approved_cached_configs()

    if not approved:
        raise RuntimeError(
            "Nenhuma configuração VPN aprovada está disponível. "
            "Execute update_vpn_configs() primeiro."
        )

    remaining = approved[:]
    print(f"{len(remaining)} configuração(ões) aprovadas disponíveis.")
    while remaining:
        config_path = random.choice(remaining)
        remaining.remove(config_path)
        print(
            f"\nConfiguração escolhida aleatoriamente: {config_path.name} "
            f"(configuração {len(approved) - len(remaining)}/{len(approved)}; "
            "máximo de 3 tentativas)"
        )

        for attempt in range(1, 4):
            print(f"Tentativa {attempt}/3: {config_path.name}")
            try:
                process = _connect(config_path)
            except OSError as error:
                print(f"Falha ao iniciar o OpenVPN: {error}")
                process = None
            if process is not None:
                return process
            if attempt < 3:
                print("Servidor indisponível. Repetindo esta configuração...")

        if config_path.exists():
            _discard_cached_config(
                config_path,
                status,
                "não foi possível estabelecer o túnel",
            )
        print("Limite de 3 tentativas atingido. Escolhendo outra configuração...")

    raise RuntimeError(
        f"Não foi possível conectar após testar as {len(approved)} "
        "configurações aprovadas, com até 3 tentativas por configuração."
    )


def connect_with_cached_configs():
    """Prepara o cache e conecta sem repetir a validação de estabilidade."""
    prepare_vpn_configs()
    return openvpn_enter_()


#if __name__ == "__main__":
#    prepare_vpn_configs()