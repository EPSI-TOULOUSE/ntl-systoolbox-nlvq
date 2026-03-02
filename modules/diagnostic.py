#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
============================================================
NTL-SysToolbox — Module Diagnostic
============================================================
- Windows (WinRM / pywinrm) :
    * État des services 'adws' et 'dns'
    * Uptime, CPU (%), RAM (%), Disque (%)
- Linux (SSH / paramiko) :
    * Uptime, CPU (%), RAM (%), Disque (%)
    * Vérification port 3306 (MySQL)
- Sortie : console + fichier JSON horodaté
============================================================
Exit codes : 0 = succès, 1 = erreur
============================================================
"""

import json
import logging
import socket
import sys
from datetime import datetime
from pathlib import Path

logger = logging.getLogger("diagnostic")

# Dossier de sortie des rapports (relatif à ce fichier)
RAPPORT_DIR = Path(__file__).resolve().parent.parent / "rapports"
RAPPORT_DIR.mkdir(parents=True, exist_ok=True)


# ──────────────────────────────────────────────────────────
# Utilitaires
# ──────────────────────────────────────────────────────────
def _horodatage() -> str:
    """Retourne un horodatage formaté pour les noms de fichiers."""
    return datetime.now().strftime("%Y%m%d_%H%M%S")


def _sauvegarder_rapport(donnees: dict) -> Path:
    """Écrit le rapport JSON dans le dossier /rapports."""
    nom_fichier = RAPPORT_DIR / f"diag_report_{_horodatage()}.json"
    with nom_fichier.open("w", encoding="utf-8") as f:
        json.dump(donnees, f, indent=4, ensure_ascii=False, default=str)
    logger.info("Rapport JSON sauvegardé : %s", nom_fichier)
    return nom_fichier


def _afficher_section(titre: str) -> None:
    """Affiche un titre de section dans la console."""
    print(f"\n{'─' * 55}")
    print(f"  {titre}")
    print(f"{'─' * 55}")


# ──────────────────────────────────────────────────────────
# Diagnostic Windows via WinRM
# ──────────────────────────────────────────────────────────
def diagnostiquer_windows(config: dict) -> dict:
    """
    Connexion WinRM au serveur Windows.
    Récupère l'état des services 'adws' et 'dns',
    ainsi que Uptime, CPU, RAM et Disque.

    :param config: dictionnaire de configuration global
    :return: dictionnaire des résultats Windows
    """
    resultats = {
        "hote": config["windows"]["ip"],
        "statut_connexion": "ERREUR",
        "services": {},
        "uptime": None,
        "cpu_pct": None,
        "ram_pct": None,
        "disque_pct": None,
    }

    try:
        import winrm  # noqa: PLC0415

        _afficher_section(
            f"Diagnostic Windows — {config['windows']['ip']}"
        )

        session = winrm.Session(
            target=config["windows"]["ip"],
            auth=(config["windows"]["user"], config["windows"]["password"]),
            transport="basic",
            server_cert_validation="ignore",
        )

        # --- État des services adws et dns ---
        services_cibles = ["adws", "dns"]
        for service in services_cibles:
            commande = (
                f"(Get-Service -Name '{service}').Status"
            )
            reponse = session.run_ps(commande)
            etat = reponse.std_out.decode("utf-8", errors="replace").strip()
            resultats["services"][service] = etat if etat else "Inconnu"
            icone = "✔" if etat.lower() == "running" else "✘"
            print(f"  Service {service:>6} : {icone} {etat}")

        # --- Uptime ---
        cmd_uptime = (
            "(Get-Date) - (gcim Win32_OperatingSystem).LastBootUpTime"
            " | Select-Object -ExpandProperty TotalHours"
        )
        rep = session.run_ps(cmd_uptime)
        uptime_str = rep.std_out.decode("utf-8", errors="replace").strip()
        try:
            resultats["uptime"] = f"{float(uptime_str):.1f} heures"
        except ValueError:
            resultats["uptime"] = uptime_str
        print(f"  Uptime            : {resultats['uptime']}")

        # --- CPU ---
        cmd_cpu = (
            "(Get-CimInstance Win32_Processor | Measure-Object -Property"
            " LoadPercentage -Average).Average"
        )
        rep = session.run_ps(cmd_cpu)
        resultats["cpu_pct"] = rep.std_out.decode("utf-8", errors="replace").strip()
        print(f"  CPU               : {resultats['cpu_pct']} %")

        # --- RAM ---
        cmd_ram = (
            "$os = Get-CimInstance Win32_OperatingSystem;"
            "$used = $os.TotalVisibleMemorySize - $os.FreePhysicalMemory;"
            "[math]::Round(($used / $os.TotalVisibleMemorySize) * 100, 2)"
        )
        rep = session.run_ps(cmd_ram)
        resultats["ram_pct"] = rep.std_out.decode("utf-8", errors="replace").strip()
        print(f"  RAM utilisée      : {resultats['ram_pct']} %")

        # --- Disque C: ---
        cmd_disque = (
            "$d = Get-PSDrive C;"
            "[math]::Round(($d.Used / ($d.Used + $d.Free)) * 100, 2)"
        )
        rep = session.run_ps(cmd_disque)
        resultats["disque_pct"] = rep.std_out.decode("utf-8", errors="replace").strip()
        print(f"  Disque C:         : {resultats['disque_pct']} %")

        resultats["statut_connexion"] = "OK"
        logger.info("Diagnostic Windows réussi pour %s", config["windows"]["ip"])

    except ImportError:
        msg = "pywinrm non installé. Lancez : pip install pywinrm"
        logger.error(msg)
        print(f"  [ERREUR] {msg}")
    except Exception as exc:  # noqa: BLE001
        logger.error("Erreur diagnostic Windows : %s", exc)
        resultats["erreur"] = str(exc)
        print(f"  [ERREUR] {exc}")

    return resultats


# ──────────────────────────────────────────────────────────
# Diagnostic Linux via SSH (paramiko)
# ──────────────────────────────────────────────────────────
def _executer_commande_ssh(client, commande: str) -> str:
    """Exécute une commande SSH et retourne la sortie standard."""
    _, stdout, stderr = client.exec_command(commande)
    sortie = stdout.read().decode("utf-8", errors="replace").strip()
    erreur = stderr.read().decode("utf-8", errors="replace").strip()
    if erreur:
        logger.debug("stderr SSH [%s] : %s", commande, erreur)
    return sortie


def _verifier_port(hote: str, port: int, timeout: float = 2.0) -> bool:
    """
    Tente une connexion TCP sur hote:port.
    :return: True si le port répond, False sinon.
    """
    try:
        with socket.create_connection((hote, port), timeout=timeout):
            return True
    except (OSError, ConnectionRefusedError, socket.timeout):
        return False


def diagnostiquer_linux(config: dict) -> dict:
    """
    Connexion SSH au serveur Linux.
    Récupère Uptime, CPU, RAM, Disque et vérifie le port 3306.

    :param config: dictionnaire de configuration global
    :return: dictionnaire des résultats Linux
    """
    resultats = {
        "hote": config["linux"]["ip"],
        "statut_connexion": "ERREUR",
        "uptime": None,
        "cpu_pct": None,
        "ram_pct": None,
        "disque_pct": None,
        "port_3306": None,
    }

    try:
        import paramiko  # noqa: PLC0415

        _afficher_section(
            f"Diagnostic Linux — {config['linux']['ip']}"
        )

        client = paramiko.SSHClient()
        # Accepte automatiquement les clés hôtes inconnues
        client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        client.connect(
            hostname=config["linux"]["ip"],
            port=int(config["linux"]["port"]),
            username=config["linux"]["user"],
            password=config["linux"]["password"],
            timeout=10,
        )

        # --- Uptime ---
        uptime_raw = _executer_commande_ssh(client, "uptime -p")
        resultats["uptime"] = uptime_raw
        print(f"  Uptime            : {uptime_raw}")

        # --- CPU (% d'inactivité → 100 - idle = utilisation) ---
        cpu_raw = _executer_commande_ssh(
            client,
            "top -bn1 | grep 'Cpu(s)' | awk '{print $2 + $4}'",
        )
        resultats["cpu_pct"] = cpu_raw
        print(f"  CPU utilisé       : {cpu_raw} %")

        # --- RAM ---
        ram_raw = _executer_commande_ssh(
            client,
            "free | awk '/Mem:/ {printf \"%.1f\", $3/$2 * 100}'",
        )
        resultats["ram_pct"] = ram_raw
        print(f"  RAM utilisée      : {ram_raw} %")

        # --- Disque (partition racine /) ---
        disque_raw = _executer_commande_ssh(
            client,
            "df / | awk 'NR==2 {print $5}' | tr -d '%'",
        )
        resultats["disque_pct"] = disque_raw
        print(f"  Disque /          : {disque_raw} %")

        client.close()

        # --- Port 3306 ---
        port_ouvert = _verifier_port(config["linux"]["ip"], 3306)
        resultats["port_3306"] = "Ouvert" if port_ouvert else "Fermé"
        icone = "✔" if port_ouvert else "✘"
        print(f"  Port 3306 MySQL   : {icone} {resultats['port_3306']}")

        resultats["statut_connexion"] = "OK"
        logger.info("Diagnostic Linux réussi pour %s", config["linux"]["ip"])

    except ImportError:
        msg = "paramiko non installé. Lancez : pip install paramiko"
        logger.error(msg)
        print(f"  [ERREUR] {msg}")
    except Exception as exc:  # noqa: BLE001
        logger.error("Erreur diagnostic Linux : %s", exc)
        resultats["erreur"] = str(exc)
        print(f"  [ERREUR] {exc}")

    return resultats


# ──────────────────────────────────────────────────────────
# Point d'entrée du module
# ──────────────────────────────────────────────────────────
def executer_diagnostic(config: dict) -> int:
    """
    Lance le diagnostic Windows et Linux,
    affiche les résultats et génère le rapport JSON.

    :param config: configuration globale
    :return: 0 si succès, 1 si au moins une erreur
    """
    erreur_detectee = False

    rapport = {
        "timestamp": datetime.now().isoformat(),
        "windows": {},
        "linux": {},
    }

    # Diagnostic Windows
    try:
        rapport["windows"] = diagnostiquer_windows(config)
        if rapport["windows"]["statut_connexion"] != "OK":
            erreur_detectee = True
    except Exception as exc:  # noqa: BLE001
        logger.error("Diagnostic Windows interrompu : %s", exc)
        rapport["windows"] = {"erreur": str(exc)}
        erreur_detectee = True

    # Diagnostic Linux
    try:
        rapport["linux"] = diagnostiquer_linux(config)
        if rapport["linux"]["statut_connexion"] != "OK":
            erreur_detectee = True
    except Exception as exc:  # noqa: BLE001
        logger.error("Diagnostic Linux interrompu : %s", exc)
        rapport["linux"] = {"erreur": str(exc)}
        erreur_detectee = True

    # Sauvegarde du rapport JSON
    chemin = _sauvegarder_rapport(rapport)
    print(f"\n  [✔] Rapport JSON : {chemin}")

    return 1 if erreur_detectee else 0
