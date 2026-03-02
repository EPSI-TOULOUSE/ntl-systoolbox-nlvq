#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
============================================================
NTL-SysToolbox - Nord Transit Logistics
Script principal : menu CLI interactif
============================================================
Auteur  : DevOps NTL
Version : 1.0.0
============================================================
"""

import sys
import os
import platform
import logging
from pathlib import Path

import yaml

# ──────────────────────────────────────────────────────────
# Chemins de base (compatibilité Windows / Linux via pathlib)
# ──────────────────────────────────────────────────────────
BASE_DIR = Path(__file__).resolve().parent
CONFIG_FILE = BASE_DIR / "config.yaml"
LOG_DIR = BASE_DIR / "logs"
LOG_DIR.mkdir(parents=True, exist_ok=True)

# ──────────────────────────────────────────────────────────
# Configuration du journal
# ──────────────────────────────────────────────────────────
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s - %(message)s",
    handlers=[
        logging.StreamHandler(sys.stdout),
        logging.FileHandler(LOG_DIR / "ntl_toolbox.log", encoding="utf-8"),
    ],
)
logger = logging.getLogger("main")


# ──────────────────────────────────────────────────────────
# Chargement de la configuration (YAML + surcharge ENV)
# ──────────────────────────────────────────────────────────
def charger_config() -> dict:
    """
    Charge config.yaml et surcharge les valeurs
    via les variables d'environnement si elles sont définies.

    Variables d'environnement reconnues :
      NTL_WIN_IP, NTL_WIN_USER, NTL_WIN_PASSWORD, NTL_WIN_PORT
      NTL_LIN_IP, NTL_LIN_USER, NTL_LIN_PASSWORD, NTL_LIN_PORT
      NTL_MYSQL_HOST, NTL_MYSQL_USER, NTL_MYSQL_PASSWORD
      NTL_SUBNET
    """
    if not CONFIG_FILE.exists():
        logger.error("Fichier config.yaml introuvable : %s", CONFIG_FILE)
        sys.exit(1)

    with CONFIG_FILE.open("r", encoding="utf-8") as f:
        config = yaml.safe_load(f)

    # Surcharge Windows
    surcharges_win = {
        "ip": "NTL_WIN_IP",
        "user": "NTL_WIN_USER",
        "password": "NTL_WIN_PASSWORD",
        "port": "NTL_WIN_PORT",
    }
    for cle, var_env in surcharges_win.items():
        valeur = os.getenv(var_env)
        if valeur:
            config["windows"][cle] = int(valeur) if cle == "port" else valeur
            logger.info("Surcharge ENV appliquée : %s", var_env)

    # Surcharge Linux
    surcharges_lin = {
        "ip": "NTL_LIN_IP",
        "user": "NTL_LIN_USER",
        "password": "NTL_LIN_PASSWORD",
        "port": "NTL_LIN_PORT",
    }
    for cle, var_env in surcharges_lin.items():
        valeur = os.getenv(var_env)
        if valeur:
            config["linux"][cle] = int(valeur) if cle == "port" else valeur
            logger.info("Surcharge ENV appliquée : %s", var_env)

    # Surcharge MySQL
    surcharges_mysql = {
        "host": "NTL_MYSQL_HOST",
        "user": "NTL_MYSQL_USER",
        "password": "NTL_MYSQL_PASSWORD",
    }
    for cle, var_env in surcharges_mysql.items():
        valeur = os.getenv(var_env)
        if valeur:
            config["mysql"][cle] = valeur
            logger.info("Surcharge ENV appliquée : %s", var_env)

    # Surcharge réseau
    if os.getenv("NTL_SUBNET"):
        config["network"]["subnet"] = os.getenv("NTL_SUBNET")

    return config


# ──────────────────────────────────────────────────────────
# Détection de l'OS (exigence jury : OS-Aware)
# ──────────────────────────────────────────────────────────
def detecter_os() -> str:
    """Retourne une description lisible du système d'exploitation."""
    systeme = platform.system()
    version = platform.version()
    machine = platform.machine()
    return f"{systeme} | Version : {version} | Architecture : {machine}"


# ──────────────────────────────────────────────────────────
# Affichage du menu principal
# ──────────────────────────────────────────────────────────
SEPARATEUR = "=" * 65

def afficher_menu(os_info: str) -> None:
    """Affiche le menu CLI principal."""
    print(f"\n{SEPARATEUR}")
    print("   NTL-SysToolbox v1.0 — Nord Transit Logistics")
    print(SEPARATEUR)
    print(f"  OS détecté : {os_info}")
    print(SEPARATEUR)
    print("  [1] Diagnostic système (Windows + Linux)")
    print("  [2] Sauvegarde WMS (MySQL dump + export CSV)")
    print("  [3] Audit d'obsolescence réseau")
    print("  [0] Quitter")
    print(SEPARATEUR)


# ──────────────────────────────────────────────────────────
# Point d'entrée principal
# ──────────────────────────────────────────────────────────
def main() -> None:
    """Boucle principale du menu interactif."""
    os_info = detecter_os()
    config = charger_config()
    logger.info("NTL-SysToolbox démarré sur %s", platform.system())

    # Import différé des modules pour éviter les erreurs
    # au démarrage si une dépendance est manquante
    from modules.diagnostic import executer_diagnostic
    from modules.backup import executer_sauvegarde
    from modules.audit import executer_audit

    while True:
        afficher_menu(os_info)
        choix = input("  Votre choix : ").strip()

        if choix == "1":
            print("\n[+] Lancement du module Diagnostic...\n")
            code_retour = executer_diagnostic(config)
            print(f"\n[i] Module Diagnostic terminé avec le code : {code_retour}")

        elif choix == "2":
            print("\n[+] Lancement du module Sauvegarde WMS...\n")
            print("  [a] Dump SQL complet")
            print("  [b] Export CSV table 'stocks'")
            sous_choix = input("  Votre choix : ").strip().lower()
            code_retour = executer_sauvegarde(config, mode=sous_choix)
            print(f"\n[i] Module Sauvegarde terminé avec le code : {code_retour}")

        elif choix == "3":
            print("\n[+] Lancement du module Audit Obsolescence...\n")
            code_retour = executer_audit(config)
            print(f"\n[i] Module Audit terminé avec le code : {code_retour}")

        elif choix == "0":
            print("\n  Au revoir — NTL-SysToolbox fermé.\n")
            logger.info("NTL-SysToolbox arrêté par l'utilisateur.")
            sys.exit(0)

        else:
            print("\n  [!] Choix invalide. Veuillez réessayer.")


if __name__ == "__main__":
    main()
