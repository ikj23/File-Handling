import os
import time
import json
import threading
from pathlib import Path
from shutil import move
from datetime import datetime
from tkinter import (
    Tk, filedialog, messagebox, IntVar, Entry, Label, Button,
    Checkbutton, Frame, Listbox, Scrollbar, END
)
from flask import Flask, request, jsonify
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler
import schedule

app = Flask(__name__)

WATCHED_FOLDER = None
SETTINGS_PATH = None
USER_SETTINGS_PATH = None
LOG_FILE = None

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

TARGET_DIRS = {}
USER_SETTINGS = {}

def choose_folder():
    folder_picker = Tk()
    folder_picker.withdraw()
    folder = filedialog.askdirectory(title="📁 Choose folder to watch")
    folder_picker.destroy()
    
    if not folder:
        messagebox.showwarning("No folder", "No folder selected. Exiting.")
        exit()
    return Path(folder)

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

def launch_gui():
    def refresh_listbox():
        listbox.delete(0, END)
        for folder, extensions in TARGET_DIRS.items():
            listbox.insert(END, f"{folder}: {', '.join(extensions)}")

    def add_category():
        folder = folder_entry.get().strip()
        exts = [e.strip() for e in ext_entry.get().split(",") if e.strip()]
        if folder and exts:
            TARGET_DIRS[folder] = exts
            refresh_listbox()
            folder_entry.delete(0, END)
            ext_entry.delete(0, END)

    def remove_category():
        selection = listbox.curselection()
        if selection:
            key = listbox.get(selection[0]).split(":")[0]
            TARGET_DIRS.pop(key, None)
            refresh_listbox()

    def save_and_close():
        save_rules(TARGET_DIRS)
        USER_SETTINGS["scheduler_enabled"] = bool(scheduler_var.get())
        USER_SETTINGS["scheduler_interval_hours"] = int(scheduler_entry.get())
        USER_SETTINGS["auto_delete_enabled"] = bool(delete_var.get())
        USER_SETTINGS["delete_after_days"] = int(delete_entry.get())
        save_user_settings(USER_SETTINGS)

        messagebox.showinfo(
            "Organizer Running",
            "✅ Organizer is now running.\n\n📌 You can minimize this window.\n🛑 To stop: press Ctrl+C in the terminal."
        )
        gui.destroy()

    gui = Tk()
    gui.title("File Organizer Setup")
    gui.attributes("-topmost", True)  # 👈 Make window stay on top
    gui.after(500, lambda: gui.attributes("-topmost", False))  # 👈 Revert after it's shown


    Label(gui, text="📁 Folder").grid(row=0, column=0)
    folder_entry = Entry(gui)
    folder_entry.grid(row=0, column=1)

    Label(gui, text="Extensions (.pdf, .jpg)").grid(row=1, column=0)
    ext_entry = Entry(gui)
    ext_entry.grid(row=1, column=1)

    Button(gui, text="Add / Update", command=add_category).grid(row=2, column=0, columnspan=2)

    list_frame = Frame(gui)
    list_frame.grid(row=3, column=0, columnspan=2)
    scrollbar = Scrollbar(list_frame)
    listbox = Listbox(list_frame, height=10, width=50, yscrollcommand=scrollbar.set)
    scrollbar.config(command=listbox.yview)
    scrollbar.pack(side="right", fill="y")
    listbox.pack()

    refresh_listbox()

    Button(gui, text="Remove Selected", command=remove_category).grid(row=4, column=0, columnspan=2, pady=5)

    scheduler_var = IntVar(value=int(USER_SETTINGS["scheduler_enabled"]))
    delete_var = IntVar(value=int(USER_SETTINGS["auto_delete_enabled"]))

    Label(gui, text="Scheduler Enabled").grid(row=5, column=0)
    Checkbutton(gui, variable=scheduler_var).grid(row=5, column=1)

    Label(gui, text="Interval (hours)").grid(row=6, column=0)
    scheduler_entry = Entry(gui)
    scheduler_entry.insert(0, str(USER_SETTINGS["scheduler_interval_hours"]))
    scheduler_entry.grid(row=6, column=1)

    Label(gui, text="Auto-Delete Enabled").grid(row=7, column=0)
    Checkbutton(gui, variable=delete_var).grid(row=7, column=1)

    Label(gui, text="Delete after (days)").grid(row=8, column=0)
    delete_entry = Entry(gui)
    delete_entry.insert(0, str(USER_SETTINGS["delete_after_days"]))
    delete_entry.grid(row=8, column=1)

    Button(gui, text="✅ Save & Start", command=save_and_close).grid(row=9, column=0, columnspan=2, pady=10)
    gui.mainloop()

class FileOrganizerHandler(FileSystemEventHandler):
    def on_modified(self, event):
        for file in WATCHED_FOLDER.iterdir():
            if file.is_file():
                for folder, extensions in TARGET_DIRS.items():
                    if file.suffix.lower() in extensions:
                        target_dir = WATCHED_FOLDER / folder
                        target_dir.mkdir(exist_ok=True)
                        target_path = target_dir / file.name

                        counter = 1
                        while target_path.exists():
                            target_path = target_dir / f"{file.stem}({counter}){file.suffix}"
                            counter += 1

                        move(str(file), str(target_path))
                        log_action(f"Moved {file.name} → {folder}")
                        break

def log_action(text):
    with open(LOG_FILE, "a", encoding="utf-8") as log:
        log.write(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] {text}\n")


def delete_old_files():
    days = USER_SETTINGS["delete_after_days"]
    cutoff = time.time() - days * 86400
    for folder in WATCHED_FOLDER.iterdir():
        if folder.is_dir():
            for file in folder.iterdir():
                if file.is_file() and file.stat().st_mtime < cutoff:
                    log_action(f"Auto-deleted: {file}")
                    file.unlink()

def run_scheduled_tasks():
    while True:
        if USER_SETTINGS["scheduler_enabled"]:
            schedule.run_pending()
        time.sleep(1)

def start_scheduler():
    schedule.every(USER_SETTINGS["scheduler_interval_hours"]).hours.do(initial_sort)
    if USER_SETTINGS["auto_delete_enabled"]:
        schedule.every(USER_SETTINGS["scheduler_interval_hours"]).hours.do(delete_old_files)
    threading.Thread(target=run_scheduled_tasks, daemon=True).start()

def ensure_folders_exist():
    for folder in TARGET_DIRS.keys():
        (WATCHED_FOLDER / folder).mkdir(exist_ok=True)

def initial_sort():
    ensure_folders_exist()
    for file in WATCHED_FOLDER.iterdir():
        if file.is_file():
            for folder, extensions in TARGET_DIRS.items():
                if file.suffix.lower() in extensions:
                    target_dir = WATCHED_FOLDER / folder
                    target_dir.mkdir(exist_ok=True)
                    target_path = target_dir / file.name
                    counter = 1
                    while target_path.exists():
                        target_path = target_dir / f"{file.stem}({counter}){file.suffix}"
                        counter += 1
                    move(str(file), str(target_path))
                    log_action(f"Initial Sort: {file.name} → {folder}")
                    break

observer = None

@app.route("/settings", methods=["GET"])
def get_settings():
    return jsonify(load_rules())

@app.route("/settings", methods=["POST"])
def update_settings():
    new_rules = request.get_json()
    save_rules(new_rules)
    return jsonify({"status": "updated"})

@app.route("/user-settings", methods=["GET"])
def get_user_settings():
    return jsonify(load_user_settings())

@app.route("/user-settings", methods=["POST"])
def update_user_settings_api():
    settings = request.get_json()
    save_user_settings(settings)
    return jsonify({"status": "updated"})

@app.route("/log", methods=["GET"])
def get_log():
    try:
        with open(LOG_FILE, "r") as f:
            lines = f.readlines()[-100:]
        return jsonify({"log": "".join(lines)})
    except Exception as e:
        return jsonify({"error": str(e)})

@app.route("/start", methods=["POST"])
def start_watching():
    global observer
    if observer is None or not observer.is_alive():
        observer = Observer()
        observer.schedule(FileOrganizerHandler(), str(WATCHED_FOLDER), recursive=False)
        observer.start()
        return jsonify({"status": "started"})
    else:
        return jsonify({"status": "already running"})

@app.route("/stop", methods=["POST"])
def stop_watching():
    global observer
    if observer:
        observer.stop()
        observer.join()
        observer = None
    return jsonify({"status": "stopped"})

if __name__ == "__main__":
    WATCHED_FOLDER = choose_folder()
    SETTINGS_PATH = WATCHED_FOLDER / "settings.json"
    USER_SETTINGS_PATH = WATCHED_FOLDER / "user_settings.json"
    LOG_FILE = WATCHED_FOLDER / "file_organizer_log.txt"

    TARGET_DIRS = load_rules()
    USER_SETTINGS = load_user_settings()

    launch_gui()
    ensure_folders_exist()
    initial_sort()
    start_scheduler()

    observer = Observer()
    observer.schedule(FileOrganizerHandler(), str(WATCHED_FOLDER), recursive=False)
    observer.start()

    threading.Thread(target=lambda: app.run(port=5000), daemon=True).start()

    print("\n✅ Organizer is running in the background...")
    print(f"👀 Watching: {WATCHED_FOLDER}")
    print("🌐 Flask API running at: http://localhost:5000")
    print("🛑 Press Ctrl+C in this terminal to stop.\n")

    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        observer.stop()
        print("Stopped watching.")
    observer.join()
