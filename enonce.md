# TP : faire agir une IA sur votre PC avec MCP

## Objectif

Vous allez écrire une petite action Python (déplacer la souris et ouvrir un dossier), puis la déclencher simplement en écrivant une phrase dans un chat.

À la fin, vous taperez :

```text
Ouvre le dossier TP sur le bureau.
```

et la souris bougera, puis le dossier `TP` s'ouvrira.

## Comprendre avant de commencer

Trois éléments travaillent ensemble. Chacun a un seul rôle.

| Élément | Rôle | Vous devez le lancer ? |
|---|---|---|
| **Ollama** | Fait tourner le modèle d'IA `llama3.2` sur votre PC. | Oui, une fois. Il reste ouvert. |
| **Serveur MCP** (`server.py`) | Contient votre action. Il la décrit à l'IA : « voici ce que je sais faire ». | Non. OpenCode le démarre tout seul. |
| **OpenCode** | Le chat où vous écrivez. Il envoie votre phrase à l'IA. Si l'IA choisit votre action, OpenCode l'exécute. | Oui, c'est votre point d'entrée. |

Le chemin d'une phrase :

```text
Vous écrivez  →  OpenCode  →  llama3.2 (Ollama)
                                   │ « j'appelle l'action bouger_souris_et_ouvrir_dossier »
                                   ▼
              OpenCode exécute l'action dans server.py  →  le dossier s'ouvre
```

MCP est le format standard qui permet à `server.py` de décrire ses actions à n'importe quel chat compatible.

---

## Étape 1 : installer Ollama et le modèle

1. Téléchargez Ollama pour Windows sur https://ollama.com/download et installez-le.
2. Ouvrez **PowerShell** (touche Windows, tapez `PowerShell`, Entrée).
3. Téléchargez le modèle :

```powershell
ollama pull llama3.2
```

4. Vérifiez :

```powershell
ollama list
```

**Résultat attendu :** une ligne `llama3.2:latest` apparaît dans la liste.

Laissez l'application Ollama ouverte (son icône est dans la zone de notification, en bas à droite).

## Étape 2 : installer Python

1. Téléchargez Python 3.12 sur https://www.python.org/downloads/windows/ et lancez l'installation.
2. Sur le premier écran, **cochez « Add python.exe to PATH »**, puis installez.
3. Fermez PowerShell et rouvrez-le. Vérifiez :

```powershell
python --version
```

**Résultat attendu :** `Python 3.12.x`.

## Étape 3 : installer OpenCode

OpenCode est le chat. Il en faut la version 2.

**Si Node.js est installé** (testez avec `node --version`) :

```powershell
npm install -g @opencode/cli
```

**Sinon :**

1. Allez sur https://opencode.ai/docs et téléchargez le CLI Windows **x64**.
2. Décompressez le fichier `opencode.exe` dans un dossier, par exemple `C:\outils`.
3. Ajoutez ce dossier à votre `PATH` (Paramètres Windows, recherchez « variables d'environnement »).

Fermez PowerShell, rouvrez-le, puis vérifiez :

```powershell
opencode --version
```

**Résultat attendu :** un numéro de version qui commence par `2.`.

## Étape 4 : créer le dossier du projet

Dans PowerShell :

```powershell
mkdir $HOME\exo-mcp
cd $HOME\exo-mcp
python -m venv .venv
.\.venv\Scripts\python.exe -m pip install mcp==2.3.0 PyAutoGUI==0.9.54
```

Cela crée le dossier `exo-mcp`, un environnement Python isolé dans `.venv`, puis y installe les deux bibliothèques nécessaires. L'installation peut durer une minute.

Ensuite, **créez à la main un dossier nommé `TP` sur votre Bureau** (clic droit sur le Bureau, Nouveau, Dossier). C'est lui que l'action va ouvrir.

Ouvrez enfin le dossier `exo-mcp` dans votre éditeur de code. Avec VS Code :

```powershell
code .
```

Dans les étapes suivantes, vous créerez deux fichiers dans ce dossier : `server.py` et `opencode.json`.

## Étape 5 : écrire le serveur MCP

Créez le fichier `server.py` dans `exo-mcp`, avec exactement ce contenu :

```python
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


if __name__ == "__main__":
    mcp.run(transport="stdio")
```

Ce que fait chaque partie :

- `mcp = MCPServer("actions")` crée le serveur. Son nom, `actions`, resservira à l'étape 6.
- `@mcp.tool()` déclare la fonction juste en dessous comme une **action MCP**. Le nom de l'action est le nom de la fonction : `bouger_souris_et_ouvrir_dossier`.
- La phrase entre `"""` est la **description** de l'action. C'est elle que l'IA lit pour décider quand l'utiliser. Une description claire donne une IA qui choisit bien.
- `nom_dossier: str` indique à l'IA qu'elle doit fournir un texte, ici le nom du dossier.
- `mcp.run(transport="stdio")` démarre le serveur. Il communique avec OpenCode par la sortie standard.

**Règle importante :** n'écrivez jamais `print("...")` seul dans ce fichier. Un affichage normal casse la communication avec OpenCode. Pour afficher quelque chose, écrivez `print("...", file=sys.stderr)`.

## Étape 6 : connecter OpenCode à votre serveur et créer l'agent `exo`

OpenCode lit un fichier `opencode.json` placé dans le dossier du projet. Il dit trois choses : où trouver Ollama, comment démarrer votre serveur, et comment se comporte l'agent `exo`.

**Pourquoi un agent `exo` ?** OpenCode a un agent par défaut, `Build`, pensé pour programmer. Il demande à `llama3.2` d'écrire du code au lieu d'appeler directement votre action, et le dossier ne s'ouvre pas. L'agent `exo` ne laisse à l'IA que votre action : elle l'appelle.

### 6.1 Relever vos deux chemins

Dans PowerShell, toujours dans `exo-mcp` :

```powershell
Resolve-Path .\.venv\Scripts\python.exe
Resolve-Path .\server.py
```

Chaque commande affiche un chemin complet, par exemple :

```text
C:\Users\sophie\exo-mcp\.venv\Scripts\python.exe
C:\Users\sophie\exo-mcp\server.py
```

Gardez ces deux chemins sous les yeux.

### 6.2 Créer `opencode.json`

Créez le fichier `opencode.json` dans `exo-mcp`, avec ce contenu :

```json
{
  "$schema": "https://opencode.ai/config.json",
  "model": "ollama/llama3.2:latest",
  "provider": {
    "ollama": {
      "npm": "@ai-sdk/openai-compatible",
      "name": "Ollama",
      "options": { "baseURL": "http://localhost:11434/v1" },
      "models": { "llama3.2:latest": { "name": "llama3.2" } }
    }
  },
  "mcp": {
    "servers": {
      "actions": {
        "type": "local",
        "command": [
          "C:\\Users\\sophie\\exo-mcp\\.venv\\Scripts\\python.exe",
          "C:\\Users\\sophie\\exo-mcp\\server.py"
        ],
        "codemode": false
      }
    }
  },
  "agents": {
    "exo": {
      "description": "Chat qui appelle les actions MCP",
      "mode": "primary",
      "model": "ollama/llama3.2:latest",
      "system": "Tu es un assistant. Dès que la demande correspond à un outil, tu appelles cet outil. Tu n'écris pas de code et tu n'inventes pas de commande.",
      "permissions": [
        { "action": "*", "resource": "*", "effect": "deny" },
        { "action": "execute", "resource": "*", "effect": "deny" },
        { "action": "actions_bouger_souris_et_ouvrir_dossier", "resource": "*", "effect": "allow" }
      ]
    }
  }
}
```

**Vous devez modifier une seule chose** : les deux lignes sous `"command"`. Remplacez `C:\\Users\\sophie\\...` par vos propres chemins relevés à l'étape 6.1. Dans un fichier JSON, chaque `\` doit être écrit **deux fois** : `C:\Users\sophie` devient `C:\\Users\\sophie`.

Ce que contient le fichier :

- `provider` : OpenCode doit parler à Ollama, qui tourne sur votre PC.
- `mcp` → `actions` : OpenCode démarre votre `server.py` avec le Python du `.venv`. Le nom `actions` est celui de l'étape 5.
- `"codemode": false` : l'action est présentée directement à l'IA. Sans cette ligne, OpenCode lui demande d'écrire un script et elle n'appelle rien.
- `agents` → `exo` : l'agent dédié à ce TP.
- `permissions` : tout est interdit, sauf votre action. Son nom complet est `actions_` (nom du serveur) suivi du nom de la fonction : `actions_bouger_souris_et_ouvrir_dossier`.

### 6.3 Vérifier la connexion

```powershell
opencode mcp list
```

**Résultat attendu :**

```text
✓ actions  connected
```

Si vous voyez `No MCP servers configured`, attendez quelques secondes et relancez la même commande : OpenCode charge le projet à la première utilisation.

Si la ligne indique une erreur, un des deux chemins de `command` est faux. Revenez à l'étape 6.1 et copiez-les depuis PowerShell, sans les retaper.

## Étape 7 : lancer le chat et déclencher l'action

```powershell
cd $HOME\exo-mcp
opencode
```

Lancez toujours `opencode` **depuis le dossier `exo-mcp`**, sinon il ne trouve pas votre `opencode.json`.

Dans le chat :

1. Choisissez l'agent : tapez `/agents`, puis sélectionnez **exo**. Raccourci : `Shift+Tab` jusqu'à voir `exo`.
2. Choisissez le modèle : tapez `/models`, puis sélectionnez **llama3.2**.
3. Envoyez ce message :

```text
Ouvre le dossier TP sur le bureau.
```

**Résultat attendu :**

- OpenCode affiche l'appel de l'action `actions_bouger_souris_et_ouvrir_dossier` avec `TP`.
- La souris se déplace.
- Le dossier `TP` s'ouvre.
- Le modèle confirme en une phrase. Sa formulation varie d'un essai à l'autre : seul compte le dossier qui s'ouvre.

Réussi ? Vous venez de faire exécuter du code Python par une IA locale, à partir d'une phrase.

## Étape 8 : créer votre propre action

Ajoutez une deuxième action à votre serveur. Exemple, à coller dans `server.py` **avant** la ligne `if __name__ == "__main__":` :

```python
@mcp.tool()
def dire_bonjour(prenom: str) -> str:
    """Dit bonjour à une personne à partir de son prénom."""
    return f"Bonjour {prenom} !"
```

Autorisez-la dans `opencode.json`, en ajoutant cette ligne dans la liste `permissions` (sans oublier la virgule à la ligne précédente) :

```json
{ "action": "actions_dire_bonjour", "resource": "*", "effect": "allow" }
```

Quittez OpenCode et relancez-le (`opencode`, depuis `exo-mcp`), choisissez de nouveau l'agent **exo**, puis écrivez :

```text
Dis bonjour à Léa.
```

**À vous maintenant :** inventez une action utile (ouvrir un site web, créer un fichier texte, afficher l'heure…). Écrivez la fonction avec une bonne description, autorisez-la, testez-la en français.

Règle à retenir : le nom à autoriser est toujours `actions_` suivi du nom de la fonction.

---

## Si ça ne marche pas

Vérifiez dans l'ordre :

1. **Ollama est-il ouvert ?** Son icône doit être dans la zone de notification. `ollama list` doit afficher `llama3.2`.
2. **`opencode mcp list` affiche-t-il `connected` ?** Sinon, les chemins de `opencode.json` sont faux (étape 6.1), ou il manque des `\\`.
3. **Êtes-vous sur l'agent `exo` ?** Le nom de l'agent s'affiche dans le chat. Avec `Build`, le dossier ne s'ouvre pas.
4. **Avez-vous lancé `opencode` depuis le dossier `exo-mcp` ?**
5. **Le dossier `TP` existe-t-il sur votre Bureau ?** Sinon l'action répond « n'existe pas sur le Bureau ».
6. **Le fichier `server.py` contient-il un `print("...")` sans `file=sys.stderr` ?** Supprimez-le.
7. **Avez-vous modifié `server.py` ou `opencode.json` pendant que OpenCode tournait ?** Quittez-le et relancez-le.
8. **Les noms sont-ils identiques partout ?** La permission doit s'appeler `actions_` suivi du nom exact de la fonction.
