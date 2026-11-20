import os
import sys
from pathlib import Path

import pyautogui
from mcp.server.mcpserver import MCPServer

mcp = MCPServer("actions")


def trouver_dossier_bureau(nom_dossier: str) -> Path | None:
    accueil = Path.home()
    for bureau in (
        accueil / "Desktop",
        accueil / "OneDrive" / "Desktop",
        accueil / "OneDrive" / "Bureau",
        accueil / "Bureau",
    ):
        cible = bureau / nom_dossier
        if cible.is_dir():
            return cible
    return None


@mcp.tool()
def bouger_souris_et_ouvrir_dossier(nom_dossier: str) -> str:
    """Déplace le curseur de la souris puis ouvre un dossier situé sur le Bureau."""
    dossier = trouver_dossier_bureau(nom_dossier)
    if dossier is None:
        return f"Erreur : le dossier '{nom_dossier}' n'existe pas sur le Bureau."

    try:
        pyautogui.moveTo(500, 500, duration=0.5)
    except Exception as erreur:
        print(f"[souris] {erreur}", file=sys.stderr)

    os.startfile(str(dossier))
    return f"OK : souris déplacée et dossier '{dossier}' ouvert."

@mcp.tool()
def dire_bonjour(prenom: str) -> str:
    """Dit bonjour à une personne à partir de son prénom."""
    return f"Bonjour {prenom} !"

if __name__ == "__main__":
    mcp.run(transport="stdio")