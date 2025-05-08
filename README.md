# 🕵️‍♂️ SteamSniperz

> Un utilitaire minimaliste pour surveiller les mises à jour Steam et copier automatiquement les dossiers de jeux modifiés vers un autre emplacement.

---



SteamSniperz est un petit script conçu pour détecter les jeux Steam dont les fichiers viennent d’être mis à jour.  
Dès qu’une mise à jour est repérée dans le dossier `Steam/steamapps`, le jeu concerné est copié dans un répertoire de destination** spécifié.



---

## ⚙️ Fonctionnement

1. Le script surveille le dossier `steamapps` (ou un autre répertoire défini).
2. Lorsqu'un jeu est mis à jour (nouveaux fichiers, fichiers modifiés), il est détecté.
3. Le dossier du jeu est copié dans un répertoire de sauvegarde / d’analyse / de modding, etc.

---

## 🧰 Outils et dépendances

- Langage : Python 3
- Librairies :
  - `os`, `shutil` – manipulation des fichiers
  - `time` – pour la boucle de surveillance
  - `logging` – log des actions (facultatif)
  - `watchdog` *(recommandé)* – pour un suivi en temps réel plus propre

---

## 🚀 Lancer le script

1. Clone le dépôt :
   ```bash
   git clone https://github.com/swyftos/steamsniperz.git
   cd steamsniperz
2
Modifie les chemins source/destination dans le script :

SOURCE_DIR = "C:/Program Files (x86)/Steam/steamapps/common"
DEST_DIR = "D:/SteamBackups/"

3
Lance le script :

python main.py



