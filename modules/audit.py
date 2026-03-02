#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
============================================================
NTL-SysToolbox — Module Audit Obsolescence
============================================================
- Scan réseau (ping sweep) sur 192.168.1.0/24
- Base interne des dates EOL (Windows Server + Ubuntu)
- Rapport JSON : 'Supported', 'Warning' ou 'Critical'
    * Warning  : EOL dans moins de 6 mois
    * Critical : EOL déjà dépassée
============================================================
Exit codes : 0 = succès, 1 = erreur
============================================================
"""

import concurrent.futures
import ipaddress
import json
import logging
import platform
import subprocess
from datetime import date, datetime, timedelta
from pathlib import Path

logger = logging.getLogger("audit")

RAPPORT_DIR = Path(__file__).resolve().parent.parent / "rapports"
RAPPORT_DIR.mkdir(parents=True, exist_ok=True)

# ──────────────────────────────────────────────────────────
# Base de données EOL interne
# Clé : nom du système | Valeur : date de fin de support
# Sources : Microsoft / Canonical
# ──────────────────────────────────────────────────────────
BASE_EOL: dict[str, date] = {
    # Windows Server
    "Windows Server 2012":    date(2023, 10, 10),
    "Windows Server 2012 R2": date(2023, 10, 10),
    "Windows Server 2016":    date(2027, 1, 12),
    "Windows Server 2019":    date(2029, 1, 9),
    "Windows Server 2022":    date(2031, 10, 14),
    # Ubuntu LTS
    "Ubuntu 20.04":           date(2025, 4, 2),
    "Ubuntu 22.04":           date(2027, 4, 1),
    "Ubuntu 24.04":           date(2029, 4, 1),
}

SEUIL_WARNING_JOURS = 180  # 6 mois


# ──────────────────────────────────────────────────────────
# Utilitaires
# ──────────────────────────────────────────────────────────
def _horodatage() -> str:
    return datetime.now().strftime("%Y%m%d_%H%M%S")


def _statut_eol(nom_systeme: str) -> dict:
    """
    Retourne le statut EOL pour un système donné.

    :param nom_systeme: nom du système (ex: 'Windows Server 2019')
    :return: dict avec 'eol_date', 'statut', 'jours_restants'
    """
    aujourd_hui = date.today()

    # Recherche par correspondance partielle
    eol_date = None
    for cle, val in BASE_EOL.items():
        if cle.lower() in nom_systeme.lower():
            eol_date = val
            break

    if eol_date is None:
        return {
            "eol_date": "Inconnue",
            "statut": "Inconnu",
            "jours_restants": None,
        }

    jours_restants = (eol_date - aujourd_hui).days

    if jours_restants < 0:
        statut = "Critical"
    elif jours_restants <= SEUIL_WARNING_JOURS:
        statut = "Warning"
    else:
        statut = "Supported"

    return {
        "eol_date": eol_date.isoformat(),
        "statut": statut,
        "jours_restants": jours_restants,
    }


# ──────────────────────────────────────────────────────────
# Ping sweep
# ──────────────────────────────────────────────────────────
def _ping_hote(ip: str, timeout: int = 1) -> bool:
    """
    Envoie un ping à un hôte.
    Adapté automatiquement à Windows et Linux.

    :param ip: adresse IP cible
    :param timeout: timeout en secondes
    :return: True si l'hôte répond
    """
    systeme = platform.system().lower()

    if systeme == "windows":
        # -n : nombre de paquets, -w : timeout en ms
        cmd = ["ping", "-n", "1", "-w", str(timeout * 1000), ip]
    else:
        # -c : nombre de paquets, -W : timeout en secondes
        cmd = ["ping", "-c", "1", "-W", str(timeout), ip]

    try:
        resultat = subprocess.run(
            cmd,
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
            timeout=timeout + 2,
        )
        return resultat.returncode == 0
    except (subprocess.TimeoutExpired, OSError):
        return False


def scan_reseau(subnet: str, timeout: int = 1, max_workers: int = 50) -> list[str]:
    """
    Effectue un ping sweep parallèle sur le sous-réseau donné.

    :param subnet: CIDR (ex: '192.168.1.0/24')
    :param timeout: timeout ping par hôte (secondes)
    :param max_workers: nombre de threads simultanés
    :return: liste des IPs actives
    """
    hotes_actifs = []

    try:
        reseau = ipaddress.ip_network(subnet, strict=False)
    except ValueError as exc:
        logger.error("Sous-réseau invalide '%s' : %s", subnet, exc)
        return hotes_actifs

    # Exclut l'adresse réseau et broadcast
    ips = [str(ip) for ip in reseau.hosts()]
    total = len(ips)

    print(f"  [~] Scan de {total} hôtes sur {subnet}...")
    print(f"  [~] Threads parallèles : {max_workers}")

    with concurrent.futures.ThreadPoolExecutor(max_workers=max_workers) as executor:
        resultats = executor.map(lambda ip: (ip, _ping_hote(ip, timeout)), ips)
        for ip, actif in resultats:
            if actif:
                hotes_actifs.append(ip)
                print(f"  [✔] Actif : {ip}")

    print(f"\n  [i] {len(hotes_actifs)} hôte(s) actif(s) trouvé(s).")
    logger.info(
        "Scan terminé : %d/%d hôtes actifs", len(hotes_actifs), total
    )
    return hotes_actifs


# ──────────────────────────────────────────────────────────
# Génération du rapport
# ──────────────────────────────────────────────────────────
def generer_rapport_audit(hotes_actifs: list[str]) -> dict:
    """
    Construit le rapport d'audit pour chaque hôte actif.
    Les systèmes sont simulés pour la démonstration :
    - IPs paires → Windows Server 2019
    - IPs impaires → Ubuntu 22.04
    (En production, remplacer par une détection réelle via SSH/WMI)

    :param hotes_actifs: liste des IPs actives
    :return: dictionnaire structuré du rapport
    """
    rapport = {
        "timestamp": datetime.now().isoformat(),
        "subnet_scanne": "",
        "total_actifs": len(hotes_actifs),
        "resume": {"Supported": 0, "Warning": 0, "Critical": 0, "Inconnu": 0},
        "machines": [],
    }

    for ip in hotes_actifs:
        # Simulation de l'OS détecté (à remplacer par snmp/ssh en prod)
        dernier_octet = int(ip.split(".")[-1])
        if dernier_octet % 2 == 0:
            os_detecte = "Windows Server 2019"
        else:
            os_detecte = "Ubuntu 22.04"

        info_eol = _statut_eol(os_detecte)
        statut = info_eol["statut"]

        # Comptage résumé
        rapport["resume"][statut] = rapport["resume"].get(statut, 0) + 1

        machine = {
            "ip": ip,
            "os_detecte": os_detecte,
            **info_eol,
        }
        rapport["machines"].append(machine)

    return rapport


def _afficher_rapport(rapport: dict) -> None:
    """Affiche un résumé coloré du rapport dans la console."""
    resume = rapport["resume"]
    print(f"\n{'─' * 55}")
    print("  RÉSUMÉ AUDIT OBSOLESCENCE")
    print(f"{'─' * 55}")
    print(f"  ✔  Supportés  : {resume.get('Supported', 0)}")
    print(f"  ⚠  Avertissements (Warning)  : {resume.get('Warning', 0)}")
    print(f"  ✘  Critiques  : {resume.get('Critical', 0)}")
    print(f"  ?  Inconnus   : {resume.get('Inconnu', 0)}")
    print(f"{'─' * 55}")

    for machine in rapport["machines"]:
        icone = {"Supported": "✔", "Warning": "⚠", "Critical": "✘"}.get(
            machine["statut"], "?"
        )
        jours = machine.get("jours_restants")
        if jours is not None:
            info_jours = (
                f"(dans {jours} j)" if jours >= 0 else f"(dépassée de {-jours} j)"
            )
        else:
            info_jours = ""

        print(
            f"  {icone} {machine['ip']:<16} {machine['os_detecte']:<26} "
            f"EOL:{machine['eol_date']} {machine['statut']} {info_jours}"
        )


# ──────────────────────────────────────────────────────────
# Point d'entrée du module
# ──────────────────────────────────────────────────────────
def executer_audit(config: dict) -> int:
    """
    Lance le scan réseau et génère le rapport d'obsolescence.

    :param config: configuration globale
    :return: 0 si succès, 1 si erreur
    """
    try:
        subnet = config["network"]["subnet"]
        timeout = int(config["network"].get("ping_timeout", 1))

        # Scan réseau
        hotes_actifs = scan_reseau(subnet, timeout=timeout)

        # Construction du rapport
        rapport = generer_rapport_audit(hotes_actifs)
        rapport["subnet_scanne"] = subnet

        # Affichage console
        _afficher_rapport(rapport)

        # Sauvegarde JSON
        nom_fichier = RAPPORT_DIR / f"audit_report_{_horodatage()}.json"
        with nom_fichier.open("w", encoding="utf-8") as f:
            json.dump(rapport, f, indent=4, ensure_ascii=False, default=str)

        print(f"\n  [✔] Rapport JSON : {nom_fichier}")
        logger.info("Audit terminé. Rapport : %s", nom_fichier)
        return 0

    except Exception as exc:  # noqa: BLE001
        logger.error("Erreur dans le module Audit : %s", exc)
        print(f"\n  [✘] Erreur audit : {exc}")
        return 1
