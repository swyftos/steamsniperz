import time, shutil, os
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler

steam_downloading_path = r"C:\Program Files (x86)\Steam\steamapps\downloading"
home = os.path.expanduser("~")
backup_path = os.path.join(home, "Documents", "SteamFileBackup")
os.makedirs(backup_path, exist_ok=True)
log_file = os.path.join(backup_path, "log.txt")

class FileInterceptor(FileSystemEventHandler):
    def on_created(self, event):    self._handle(event.src_path)
    def on_modified(self, event):   self._handle(event.src_path)
    def on_moved(self, event):      self._handle(event.dest_path)

    def _handle(self, path):
        if event := getattr(self, 'event', None): pass
        if os.path.isdir(path): return
        rel = os.path.relpath(path, steam_downloading_path)
        dst = os.path.join(backup_path, rel)
        os.makedirs(os.path.dirname(dst), exist_ok=True)

        # Si le fichier a déjà disparu ou chemin invalide, on ignore
        if not os.path.exists(path):
            return

        # Tenter de copier avec retry en cas de fichier verrouillé
        for attempt in range(5):
            try:
                shutil.copy2(path, dst)
                with open(log_file, "a", encoding="utf-8") as log:
                    log.write(f"[{time.ctime()}] Copié: {rel}\n")
                print(f"Copié : {rel}")
                break
            except PermissionError as e:
                # WinError 32 : fichier utilisé par un autre processus
                if getattr(e, 'winerror', None) == 32 and attempt < 4:
                    time.sleep(0.1)
                    continue
                print(f"Erreur de copie : {e}")
                break
            except FileNotFoundError:
                # WinError 2 ou 3 : fichier ou dossier introuvable, on abandonne
                break

if __name__ == "__main__":
    print("🔍 Surveillance du dossier Steam… (Ctrl+C pour stopper)")
    observer = Observer()
    observer.schedule(FileInterceptor(), steam_downloading_path, recursive=True)
    observer.start()
    try:
        while True: time.sleep(1)
    except KeyboardInterrupt:
        observer.stop()
    observer.join()
