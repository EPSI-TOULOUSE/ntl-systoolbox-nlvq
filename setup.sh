#!/usr/bin/env bash
# ============================================================
# NTL-SysToolbox — Setup Linux / macOS
# Création du venv Python et installation des dépendances
# ============================================================

set -euo pipefail

# ---- Couleurs console ----
VERT="\033[0;32m"
ROUGE="\033[0;31m"
JAUNE="\033[1;33m"
RESET="\033[0m"

ok()    { echo -e "  ${VERT}[OK]${RESET} $*"; }
erreur(){ echo -e "  ${ROUGE}[ERREUR]${RESET} $*" >&2; exit 1; }
info()  { echo -e "  ${JAUNE}[~]${RESET} $*"; }

echo ""
echo " ============================================================"
echo "  NTL-SysToolbox v1.0 — Nord Transit Logistics"
echo "  Script d'installation Linux / macOS"
echo " ============================================================"
echo ""

# ---- Rendre ce script exécutable ----
chmod +x "$0"

# ---- Détection de Python 3 ----
PYTHON=""
for candidate in python3 python; do
    if command -v "$candidate" &>/dev/null; then
        version=$("$candidate" --version 2>&1 | awk '{print $2}')
        major=$(echo "$version" | cut -d. -f1)
        if [ "$major" -ge 3 ]; then
            PYTHON="$candidate"
            break
        fi
    fi
done

if [ -z "$PYTHON" ]; then
    erreur "Python 3 introuvable. Installez-le via votre gestionnaire de paquets."
fi

ok "Python détecté : $($PYTHON --version)"

# ---- Création du virtualenv ----
if [ ! -d ".venv" ]; then
    info "Création de l'environnement virtuel (.venv)..."
    "$PYTHON" -m venv .venv
    ok "Venv créé."
else
    ok "Venv existant détecté."
fi

# ---- Activation du venv ----
info "Activation du venv..."
# shellcheck disable=SC1091
source .venv/bin/activate

# ---- Mise à jour pip ----
info "Mise à jour de pip..."
pip install --upgrade pip --quiet

# ---- Installation des dépendances ----
info "Installation des dépendances (requirements.txt)..."
pip install -r requirements.txt

echo ""
echo " ============================================================"
ok "Installation terminée avec succès !"
echo "  Pour lancer l'outil : python main.py"
echo " ============================================================"
echo ""

# ---- Lancement optionnel ----
read -r -p "  Voulez-vous lancer NTL-SysToolbox maintenant ? (o/n) : " LANCER
if [[ "$LANCER" =~ ^[oO]$ ]]; then
    python main.py
fi
