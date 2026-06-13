"""Publication du site sur un serveur.

Trois voies :
  - Netlify : un jeton d'accès personnel suffit ; le site est créé au
    premier envoi, puis déployé par zip via l'API.
  - Serveur SSH : rsync vers une destination `user@hôte:/chemin/`,
    authentification par clé uniquement (BatchMode), jamais de mot de passe.
  - FTP / FTPS : hôte, utilisateur et mot de passe — l'identifiant naturel
    des hébergements mutualisés classiques ; FTPS (TLS) par défaut.

Dans tous les cas, le site publié est l'export habituel (design-system.css
+ pages), complété d'un index.html : copie de la page d'accueil du projet.
"""

import ftplib
import io
import json
import subprocess
import tempfile
import urllib.request
import zipfile
from pathlib import Path

NETLIFY_API = "https://api.netlify.com/api/v1"
_HEADERS = {"User-Agent": "Themo (https://github.com/mobile-michel/themo)"}


def site_files(project):
    """Tous les fichiers du site à publier (CSS, pages, index, favicon,
    robots, sitemap) — construits par le projet."""
    return project.web_files()


# -- Netlify -----------------------------------------------------------------

def _netlify(token, path, data, ctype):
    req = urllib.request.Request(
        NETLIFY_API + path, data=data, method="POST",
        headers={**_HEADERS, "Authorization": f"Bearer {token}",
                 "Content-Type": ctype})
    with urllib.request.urlopen(req, timeout=60) as resp:
        return json.load(resp)


def netlify_create_site(token):
    """Crée un site (nom auto-généré) ; renvoie le JSON du site (id, url…)."""
    return _netlify(token, "/sites", b"{}", "application/json")


def zip_site(files):
    buf = io.BytesIO()
    with zipfile.ZipFile(buf, "w", zipfile.ZIP_DEFLATED) as archive:
        for name, content in files.items():
            archive.writestr(name, content)
    return buf.getvalue()


def netlify_deploy(token, site_id, files):
    """Déploie le site par zip ; renvoie le JSON du déploiement."""
    return _netlify(token, f"/sites/{site_id}/deploys",
                    zip_site(files), "application/zip")


# -- Serveur SSH (rsync) ------------------------------------------------------

def rsync(dest, files):
    """Synchronise les fichiers vers `dest` ; renvoie (succès, message).

    Pas de --delete : on n'efface jamais rien chez l'utilisateur.
    """
    if not dest.endswith("/"):
        dest += "/"
    with tempfile.TemporaryDirectory(prefix="themo-publish-") as tmp:
        for name, content in files.items():
            Path(tmp, name).write_text(content, encoding="utf-8")
        try:
            proc = subprocess.run(
                ["rsync", "-az", "--timeout=30",
                 "-e", "ssh -o BatchMode=yes", tmp + "/", dest],
                capture_output=True, text=True, timeout=180)
        except FileNotFoundError:
            return False, "rsync introuvable — installez le paquet rsync"
        except subprocess.TimeoutExpired:
            return False, "délai dépassé"
    if proc.returncode != 0:
        return False, (proc.stderr or proc.stdout).strip().splitlines()[-1]
    return True, dest


# -- FTP / FTPS ---------------------------------------------------------------

def ftp_upload(host, user, password, path, files, secure=True):
    """Téléverse les fichiers par FTP(S) ; renvoie (succès, message).

    Hôte au format `serveur` ou `serveur:port`. FTPS (TLS) par défaut, avec
    chiffrement du canal de données ; `secure=False` pour du FTP simple.
    Les segments manquants du dossier distant sont créés. Pas de
    suppression : on n'efface jamais rien chez l'utilisateur.
    """
    port = 21
    if host.count(":") == 1 and host.rsplit(":", 1)[1].isdigit():
        host, port = host.rsplit(":", 1)
        port = int(port)
    ftp = ftplib.FTP_TLS() if secure else ftplib.FTP()
    try:
        ftp.connect(host, port, timeout=30)
        ftp.login(user, password)
        if secure:
            ftp.prot_p()  # chiffrer aussi le canal de données
        # CWD segment par segment, relatif au dossier d'accueil — comme les
        # URL FTP (navigateurs, Dolphin). Un « / » initial est ignoré : l'accès
        # FTP est presque toujours enfermé dans le compte de l'utilisateur,
        # un chemin absolu depuis la racine du serveur n'aurait pas de sens.
        for segment in path.strip("/").split("/"):
            if not segment:
                continue
            try:
                ftp.cwd(segment)
            except ftplib.error_perm:
                # segment absent : le créer puis y entrer
                try:
                    ftp.mkd(segment)
                    ftp.cwd(segment)
                except ftplib.error_perm as exc:
                    return False, (f"dossier « {segment} » absent et "
                                   f"impossible à créer : {exc}")
        for name, content in files.items():
            ftp.storbinary("STOR " + name,
                           io.BytesIO(content.encode("utf-8")))
    except ftplib.error_perm as exc:
        if str(exc).startswith("530"):
            return False, "identifiants refusés (utilisateur ou mot de passe)"
        return False, str(exc)
    except ftplib.all_errors as exc:
        return False, str(exc) or "connexion impossible"
    finally:
        # nettoyage : quit() lève AttributeError si connect() a échoué
        try:
            ftp.quit()
        except Exception:
            pass
        try:
            ftp.close()
        except Exception:
            pass
    return True, path or "/"
