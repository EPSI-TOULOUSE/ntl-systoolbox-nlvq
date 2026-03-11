# NTL-SysToolbox — Nord Transit Logistics

> Boîte à outils DevOps modulaire pour l'administration système NTL.

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

_NTL-SysToolbox — Compatible Windows / Linux / macOS_
