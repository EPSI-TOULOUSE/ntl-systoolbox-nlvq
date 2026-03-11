#!/usr/bin/env python3
"""
============================================================
NTL-SysToolbox — Module Sauvegarde WMS
============================================================
- Connexion MySQL via mysql-connector-python
    * allow_local_infile=True
    * Gestion de la clé publique (get_server_public_key)
- Fonction 1 : dump SQL complet de wms_db → .sql
- Fonction 2 : export table 'stocks' → .csv
============================================================
Exit codes : 0 = succès, 1 = erreur
============================================================
"""

import csv
import logging
from datetime import datetime
from pathlib import Path

logger = logging.getLogger('backup')

# Dossier de sauvegarde (relatif à la racine du projet)
BACKUP_DIR = Path(__file__).resolve().parent.parent / 'backups'
BACKUP_DIR.mkdir(parents=True, exist_ok=True)


# ──────────────────────────────────────────────────────────
# Utilitaires
# ──────────────────────────────────────────────────────────
def _horodatage() -> str:
    """Retourne un horodatage formaté pour les noms de fichiers."""
    return datetime.now().strftime('%Y%m%d_%H%M%S')


def _obtenir_connexion(config: dict):
    """
    Crée et retourne une connexion MySQL.
    Connexion minimale : pas de paramètres SSL/auth superflus.
    Les options avancées (SSL, auth_plugin) sont gérées côté serveur MySQL.
    """
    try:
        import mysql.connector  # noqa: PLC0415
    except ImportError:
        logger.error(
            'mysql-connector-python non installé. '
            'Lancez : pip install mysql-connector-python'
        )
        raise

    connexion = mysql.connector.connect(
        host=config['mysql']['host'],
        port=int(config['mysql']['port']),
        user=config['mysql']['user'],
        password=config['mysql']['password'],
        database=config['mysql']['database'],
        connection_timeout=10,
    )
    logger.info(
        'Connexion MySQL établie sur %s:%s',
        config['mysql']['host'],
        config['mysql']['port'],
    )
    return connexion


# ──────────────────────────────────────────────────────────
# Fonction 1 : Dump SQL complet
# ──────────────────────────────────────────────────────────
def dump_sql(config: dict) -> int:
    """
    Effectue un dump SQL complet de wms_db.
    Génère un fichier : backups/wms_db_dump_YYYYMMDD_HHMMSS.sql

    :param config: configuration globale
    :return: 0 si succès, 1 si erreur
    """
    nom_fichier = BACKUP_DIR / f'wms_db_dump_{_horodatage()}.sql'

    try:
        connexion = _obtenir_connexion(config)
        curseur = connexion.cursor()
        base = config['mysql']['database']

        with nom_fichier.open('w', encoding='utf-8') as fichier_sql:
            # En-tête du dump
            fichier_sql.write('-- NTL-SysToolbox — Dump SQL\n')
            fichier_sql.write(
                f'-- Base : {base} | Date : {datetime.now().isoformat()}\n\n'
            )
            fichier_sql.write(f'USE `{base}`;\n\n')

            # Récupération de toutes les tables
            curseur.execute('SHOW TABLES;')
            tables = [row[0] for row in curseur.fetchall()]

            if not tables:
                logger.warning('Aucune table trouvée dans %s', base)
                print('  [!] Base de données vide ou inaccessible.')

            for table in tables:
                print(f'  [~] Dump de la table : {table}')

                # Structure de la table (CREATE TABLE)
                curseur.execute(f'SHOW CREATE TABLE `{table}`;')
                create_stmt = curseur.fetchone()[1]
                fichier_sql.write(f'-- Table : {table}\n')
                fichier_sql.write(f'DROP TABLE IF EXISTS `{table}`;\n')
                fichier_sql.write(f'{create_stmt};\n\n')

                # Données (INSERT INTO)
                curseur.execute(f'SELECT * FROM `{table}`;')
                lignes = curseur.fetchall()
                colonnes = [desc[0] for desc in curseur.description]

                if lignes:
                    cols_str = ', '.join(f'`{c}`' for c in colonnes)
                    fichier_sql.write(f'INSERT INTO `{table}` ({cols_str}) VALUES\n')
                    for idx, ligne in enumerate(lignes):
                        # Échappement des valeurs
                        valeurs = []
                        for val in ligne:
                            if val is None:
                                valeurs.append('NULL')
                            elif isinstance(val, (int, float)):
                                valeurs.append(str(val))
                            else:
                                val_esc = str(val).replace("'", "\\'")
                                valeurs.append(f"'{val_esc}'")
                        vals_str = f'  ({", ".join(valeurs)})'
                        if idx < len(lignes) - 1:
                            fichier_sql.write(f'{vals_str},\n')
                        else:
                            fichier_sql.write(f'{vals_str};\n\n')

        curseur.close()
        connexion.close()
        print(f'\n  [✔] Dump SQL généré : {nom_fichier}')
        logger.info('Dump SQL réussi : %s', nom_fichier)
        return 0

    except Exception as exc:  # noqa: BLE001
        logger.error('Erreur lors du dump SQL : %s', exc)
        print(f'\n  [✘] Erreur dump SQL : {exc}')
        # Supprime le fichier partiel si existant
        if nom_fichier.exists():
            nom_fichier.unlink()
        return 1


# ──────────────────────────────────────────────────────────
# Fonction 2 : Export CSV de la table stocks
# ──────────────────────────────────────────────────────────
def export_csv_stocks(config: dict) -> int:
    """
    Exporte la table 'stocks' au format CSV.
    Génère : backups/stocks_export_YYYYMMDD_HHMMSS.csv

    :param config: configuration globale
    :return: 0 si succès, 1 si erreur
    """
    nom_fichier = BACKUP_DIR / f'stocks_export_{_horodatage()}.csv'

    try:
        connexion = _obtenir_connexion(config)
        curseur = connexion.cursor()

        curseur.execute('SELECT * FROM `stocks`;')
        lignes = curseur.fetchall()
        colonnes = [desc[0] for desc in curseur.description]

        with nom_fichier.open('w', newline='', encoding='utf-8-sig') as fichier_csv:
            # utf-8-sig → BOM pour ouverture correcte dans Excel
            ecrivain = csv.writer(fichier_csv, delimiter=';', quoting=csv.QUOTE_MINIMAL)
            ecrivain.writerow(colonnes)  # En-tête
            ecrivain.writerows(lignes)

        curseur.close()
        connexion.close()

        nb_lignes = len(lignes)
        print(f'\n  [✔] Export CSV généré : {nom_fichier} ({nb_lignes} lignes)')
        logger.info('Export CSV réussi : %s (%d lignes)', nom_fichier, nb_lignes)
        return 0

    except Exception as exc:  # noqa: BLE001
        logger.error("Erreur lors de l'export CSV : %s", exc)
        print(f'\n  [✘] Erreur export CSV : {exc}')
        if nom_fichier.exists():
            nom_fichier.unlink()
        return 1


# ──────────────────────────────────────────────────────────
# Point d'entrée du module
# ──────────────────────────────────────────────────────────
def executer_sauvegarde(config: dict, mode: str = 'a') -> int:
    """
    Aiguille vers dump SQL (mode='a') ou export CSV (mode='b').

    :param config: configuration globale
    :param mode: 'a' pour dump SQL, 'b' pour export CSV
    :return: 0 si succès, 1 si erreur
    """
    if mode == 'a':
        print('  [~] Dump SQL complet de wms_db en cours...')
        return dump_sql(config)
    elif mode == 'b':
        print("  [~] Export CSV de la table 'stocks' en cours...")
        return export_csv_stocks(config)
    else:
        print(f"  [!] Mode inconnu : '{mode}'. Utilisez 'a' ou 'b'.")
        logger.warning('Mode de sauvegarde invalide : %s', mode)
        return 1
