import os
import time
import json
import logging
import schedule
import threading
from pathlib import Path
from shutil import move
from datetime import datetime
from tkinter import (
    Tk, filedialog, messagebox, IntVar, Entry, Label, Button,
    Checkbutton, Frame, Listbox, Scrollbar, SINGLE, END
)
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler

# -------------------- File and Config Paths --------------------
def choose_folder():
    root = Tk()
    root.withdraw()
    folder = filedialog.askdirectory(title="Choose folder to watch")
    if not folder:
        messagebox.showwarning("No folder", "No folder selected. Exiting.")
        exit()
    return Path(folder)

WATCHED_FOLDER = choose_folder()
SETTINGS_PATH = WATCHED_FOLDER / "settings.json"
USER_SETTINGS_PATH = WATCHED_FOLDER / "user_settings.json"
LOG_FILE = WATCHED_FOLDER / "file_organizer_log.txt"

# -------------------- Default Settings --------------------
DEFAULT_TARGET_DIRS = {
    "PDFs": [".pdf"],
    "Images": [".jpg", ".jpeg", ".png", ".gif"],
    "Videos": [".mp4", ".mkv", ".avi"],
    "Word": [".docx", ".pptx"],
    "Data": [".csv"]
}
DEFAULT_USER_SETTINGS = {
    "scheduler_enabled": True,
    "scheduler_interval_hours": 6,
    "auto_delete_enabled": True,
    "delete_after_days": 30
}

# -------------------- Settings Load/Save --------------------
def load_rules():
    if not SETTINGS_PATH.exists():
        with open(SETTINGS_PATH, "w") as f:
            json.dump(DEFAULT_TARGET_DIRS, f, indent=4)
    with open(SETTINGS_PATH, "r") as f:
        return json.load(f)

def save_rules(rules):
    with open(SETTINGS_PATH, "w") as f:
        json.dump(rules, f, indent=4)

def load_user_settings():
    if not USER_SETTINGS_PATH.exists():
        with open(USER_SETTINGS_PATH, "w") as f:
            json.dump(DEFAULT_USER_SETTINGS, f, indent=4)
    with open(USER_SETTINGS_PATH, "r") as f:
        return json.load(f)

def save_user_settings(settings):
    with open(USER_SETTINGS_PATH, "w") as f:
        json.dump(settings, f, indent=4)

# -------------------- Unified GUI --------------------
def launch_unified_gui(rules, user_settings):
    def refresh_listbox():
        listbox.delete(0, END)
        for folder, extensions in rules.items():
            ext_string = ", ".join(extensions)
            listbox.insert(END, f"{folder}: {ext_string}")

    def add_category():
        folder = folder_entry.get().strip()
        exts = [e.strip() for e in ext_entry.get().split(",") if e.strip()]
        if folder and exts:
            rules[folder] = exts
            refresh_listbox()
            folder_entry.delete(0, END)
            ext_entry.delete(0, END)

    def remove_category():
        selection = listbox.curselection()
        if selection:
            key = listbox.get(selection[0]).split(":")[0]
            rules.pop(key, None)
            refresh_listbox()

    def save_and_close():
        save_rules(rules)
        user_settings["scheduler_enabled"] = bool(scheduler_var.get())
        user_settings["scheduler_interval_hours"] = int(scheduler_entry.get())
        user_settings["auto_delete_enabled"] = bool(delete_var.get())
        user_settings["delete_after_days"] = int(delete_entry.get())
        save_user_settings(user_settings)

        messagebox.showinfo(
            "Organizer Running",
            "✅ File Organizer is now running in the background.\n\nYou can minimize this terminal.\nPress Ctrl+C to stop."
        )
        print("✔ Organizer is now running in the background.")
        gui.destroy()

    gui = Tk()
    gui.title("File Organizer Setup")

    # Folder rule section
    Label(gui, text="📁 Folder Name").grid(row=0, column=0, sticky="w", padx=5, pady=2)
    folder_entry = Entry(gui)
    folder_entry.grid(row=0, column=1, padx=5, pady=2)

    Label(gui, text="➕ Extensions (.pdf, .jpg, ...)").grid(row=1, column=0, sticky="w", padx=5, pady=2)
    ext_entry = Entry(gui)
    ext_entry.grid(row=1, column=1, padx=5, pady=2)

    Button(gui, text="Add / Update", command=add_category).grid(row=2, column=0, columnspan=2, pady=5)

    list_frame = Frame(gui)
    list_frame.grid(row=3, column=0, columnspan=2, padx=5, pady=5)
    scrollbar = Scrollbar(list_frame)
    listbox = Listbox(list_frame, width=50, height=6, yscrollcommand=scrollbar.set, selectmode=SINGLE)
    scrollbar.config(command=listbox.yview)
    scrollbar.pack(side="right", fill="y")
    listbox.pack()

    refresh_listbox()

    Button(gui, text="❌ Remove Selected", command=remove_category).grid(row=4, column=0, pady=5)
    
    # Scheduler and auto-delete options
    scheduler_var = IntVar(value=int(user_settings["scheduler_enabled"]))
    delete_var = IntVar(value=int(user_settings["auto_delete_enabled"]))

    Label(gui, text="⏱ Scheduler Enabled").grid(row=5, column=0, sticky="w", padx=5)
    Checkbutton(gui, variable=scheduler_var).grid(row=5, column=1)

    Label(gui, text="Interval (hours)").grid(row=6, column=0, sticky="w", padx=5)
    scheduler_entry = Entry(gui)
    scheduler_entry.insert(0, str(user_settings["scheduler_interval_hours"]))
    scheduler_entry.grid(row=6, column=1, padx=5, pady=2)

    Label(gui, text="🧹 Auto-Delete Enabled").grid(row=7, column=0, sticky="w", padx=5)
    Checkbutton(gui, variable=delete_var).grid(row=7, column=1)

    Label(gui, text="Delete after (days)").grid(row=8, column=0, sticky="w", padx=5)
    delete_entry = Entry(gui)
    delete_entry.insert(0, str(user_settings["delete_after_days"]))
    delete_entry.grid(row=8, column=1, padx=5, pady=2)

    Button(gui, text="✅ Save & Start Organizer", command=save_and_close).grid(row=9, column=0, columnspan=2, pady=10)
    gui.mainloop()

# -------------------- File Handling Logic --------------------
logging.basicConfig(
    filename=LOG_FILE,
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s"
)

def ensure_folders_exist():
    for folder in TARGET_DIRS.keys():
        (WATCHED_FOLDER / folder).mkdir(exist_ok=True)

def get_unique_filename(dest_path: Path) -> Path:
    if not dest_path.exists():
        return dest_path
    base = dest_path.stem
    ext = dest_path.suffix
    counter = 1
    while True:
        new_path = dest_path.parent / f"{base}({counter}){ext}"
        if not new_path.exists():
            return new_path
        counter += 1

def move_file(file_path: Path):
    extension = file_path.suffix.lower()
    for folder, extensions in TARGET_DIRS.items():
        if extension in extensions:
            dest_folder = WATCHED_FOLDER / folder
            dest_path = get_unique_filename(dest_folder / file_path.name)
            move(str(file_path), str(dest_path))
            logging.info(f"Moved '{file_path.name}' to '{dest_folder.name}'")
            return
    logging.info(f"Left '{file_path.name}' (no matching rule)")

def clean_old_files(days_old):
    cutoff = time.time() - (days_old * 86400)
    for folder in WATCHED_FOLDER.iterdir():
        if folder.is_dir():
            for file in folder.iterdir():
                if file.is_file() and file.stat().st_mtime < cutoff:
                    try:
                        logging.info(f"[AUTO-DELETE] Deleting: {file.name} (last modified: {datetime.fromtimestamp(file.stat().st_mtime)})")
                        file.unlink()
                    except Exception as e:
                        logging.error(f"Failed to delete {file.name}: {e}")

def initial_sort():
    for item in WATCHED_FOLDER.iterdir():
        if item.is_file() and item.name != LOG_FILE.name:
            move_file(item)

class FileOrganizerHandler(FileSystemEventHandler):
    def on_created(self, event):
        if not event.is_directory:
            move_file(Path(event.src_path))

def run_scheduled_tasks():
    settings = load_user_settings()
    if not settings["scheduler_enabled"]:
        logging.info("Scheduler is disabled by user.")
        return

    logging.info(f"Scheduler enabled: Every {settings['scheduler_interval_hours']} hours")

    if settings["auto_delete_enabled"]:
        schedule.every(settings["scheduler_interval_hours"]).hours.do(
            clean_old_files, days_old=settings["delete_after_days"]
        )
        logging.info(f"Auto-delete enabled: Files older than {settings['delete_after_days']} days")
    else:
        logging.info("Auto-delete is disabled by user.")

    while True:
        schedule.run_pending()
        time.sleep(10)

# -------------------- MAIN --------------------
if __name__ == "__main__":
    rules = load_rules()
    user_settings = load_user_settings()
    launch_unified_gui(rules, user_settings)

    TARGET_DIRS = load_rules()
    ensure_folders_exist()
    initial_sort()

    threading.Thread(target=run_scheduled_tasks, daemon=True).start()

    observer = Observer()
    observer.schedule(FileOrganizerHandler(), str(WATCHED_FOLDER), recursive=False)
    observer.start()

    try:
        print(f"Watching {WATCHED_FOLDER}... Press Ctrl+C to stop.")
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        observer.stop()
        print("Stopped watching.")
    observer.join()
#python 1.py