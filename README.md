# NTL-SysToolbox — Nord Transit Logistics

> Boîte à outils DevOps modulaire pour l'administration système NTL.

---

## 📁 Structure du projet

```
NTL-SysToolbox/
├── main.py                  # Menu CLI interactif (point d'entrée)
├── config.yaml              # Configuration centralisée (IPs, ports, users)
├── requirements.txt         # Dépendances Python
├── setup.bat                # Installation automatique Windows
├── setup.sh                 # Installation automatique Linux/macOS
├── modules/
│   ├── __init__.py
│   ├── diagnostic.py        # Diagnostic Windows (WinRM) + Linux (SSH)
│   ├── backup.py            # Sauvegarde MySQL (SQL dump + CSV)
│   └── audit.py             # Audit obsolescence + scan réseau
├── rapports/                # Rapports JSON générés automatiquement
├── backups/                 # Dumps SQL et CSV générés automatiquement
└── logs/                    # Journaux applicatifs
```

---

## ⚡ Installation rapide

### Windows
```bat
setup.bat
```

### Linux / macOS
```bash
bash setup.sh
# ou après un premier lancement :
chmod +x setup.sh && ./setup.sh
```

---

## 🚀 Lancement

```bash
# Activer le venv au préalable
# Linux  : source .venv/bin/activate
# Windows: .venv\Scripts\activate

python main.py
```

---

## 🌐 Variables d'environnement (surcharge de config.yaml)

| Variable            | Paramètre surchargé          |
|---------------------|------------------------------|
| `NTL_WIN_IP`        | IP du serveur Windows        |
| `NTL_WIN_USER`      | Utilisateur WinRM            |
| `NTL_WIN_PASSWORD`  | Mot de passe WinRM           |
| `NTL_WIN_PORT`      | Port WinRM (défaut 5985)     |
| `NTL_LIN_IP`        | IP du serveur Linux          |
| `NTL_LIN_USER`      | Utilisateur SSH              |
| `NTL_LIN_PASSWORD`  | Mot de passe SSH             |
| `NTL_LIN_PORT`      | Port SSH (défaut 22)         |
| `NTL_MYSQL_HOST`    | Hôte MySQL                   |
| `NTL_MYSQL_USER`    | Utilisateur MySQL            |
| `NTL_MYSQL_PASSWORD`| Mot de passe MySQL           |
| `NTL_SUBNET`        | Sous-réseau à scanner        |

---

## 🧩 Modules

### 1. Diagnostic (`modules/diagnostic.py`)
- **Windows** via WinRM (`pywinrm`) : état services `adws`/`dns`, uptime, CPU, RAM, disque
- **Linux** via SSH (`paramiko`) : uptime, CPU, RAM, disque, port 3306
- Sortie : console + `rapports/diag_report_<timestamp>.json`

### 2. Sauvegarde WMS (`modules/backup.py`)
- Connexion MySQL avec `allow_local_infile=True` et `get_server_public_key`
- **[a]** Dump SQL complet de `wms_db` → `backups/wms_db_dump_<timestamp>.sql`
- **[b]** Export CSV de la table `stocks` → `backups/stocks_export_<timestamp>.csv`

### 3. Audit Obsolescence (`modules/audit.py`)
- Ping sweep parallèle sur `192.168.1.0/24`
- Base EOL interne : Windows Server 2012/2016/2019/2022, Ubuntu 20.04/22.04/24.04
- Statuts : `Supported` / `Warning` (< 6 mois) / `Critical` (dépassée)
- Sortie : `rapports/audit_report_<timestamp>.json`

---

## 📋 Dépendances

| Package                  | Usage              |
|--------------------------|--------------------|
| `pyyaml`                 | Lecture config.yaml|
| `pywinrm`                | WinRM Windows      |
| `paramiko`               | SSH Linux          |
| `mysql-connector-python` | Connexion MySQL    |

---

## 🔁 Exit Codes

| Code | Signification              |
|------|----------------------------|
| `0`  | Succès                     |
| `1`  | Erreur (connexion, I/O...) |

---

*NTL-SysToolbox — Compatible Windows / Linux / macOS (pathlib)*
