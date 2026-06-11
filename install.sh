#!/bin/sh
# Installe le lanceur Thémo dans le menu d'applications de l'utilisateur,
# avec le chemin du dépôt courant injecté dans themo.desktop.
set -e

DIR="$(cd "$(dirname "$0")" && pwd)"
APPS="${XDG_DATA_HOME:-$HOME/.local/share}/applications"

mkdir -p "$APPS"
sed "s|@INSTALL_DIR@|$DIR|g" "$DIR/themo.desktop" > "$APPS/themo.desktop"
chmod +x "$DIR/themo.py"

echo "Lanceur installé : $APPS/themo.desktop"
echo "Application      : $DIR/themo.py"
