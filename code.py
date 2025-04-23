import time
import shutil
import os
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler

# Modifie ce chemin selon ton installation Steam
steam_downloading_path = r"C:\Program Files (x86)\Steam\steamapps\downloading"
backup_path = r"C:\Users\TonNom\Documents\SteamFileBackup"

if not os.path.exists(backup_path):
    os.makedirs(backup_path)

log_file = os.path.join(backup_path, "log.txt")

class FileInterceptor(FileSystemEventHandler):
    def on_created(self, event):
        if not event.is_directory:
            self.copy_file(event.src_path)

    def on_modified(self, event):
        if not event.is_directory:
            self.copy_file(event.src_path)

    def copy_file(self, src_path):
        rel_path = os.path.relpath(src_path, steam_downloading_path)
        dst_path = os.path.join(backup_path, rel_path)

        dst_dir = os.path.dirname(dst_path)
        if not os.path.exists(dst_dir):
            os.makedirs(dst_dir)

        try:
            shutil.copy2(src_path, dst_path)
            with open(log_file, "a", encoding="utf-8") as log:
                log.write(f"[{time.ctime()}] Copié: {rel_path}\n")
            print(f"Copié : {rel_path}")
        except Exception as e:
            print(f"Erreur de copie : {e}")

if __name__ == "__main__":
    print("🔍 Surveillance du dossier Steam en cours... (Ctrl+C pour arrêter)")
    observer = Observer()
    event_handler = FileInterceptor()
    observer.schedule(event_handler, steam_downloading_path, recursive=True)
    observer.start()

    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        observer.stop()
    observer.join()
