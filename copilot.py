import tkinter as tk
from tkinter import messagebox, filedialog, scrolledtext
import speech_recognition as sr
import pyttsx3
import os
import mysql.connector
from datetime import datetime
import psutil
import platform

 
engine = pyttsx3.init()
engine.setProperty('rate', 150)
voices = engine.getProperty('voices')
engine.setProperty('voice', voices[0].id)

microphone_state = True
dark_mode = False

 
def speak(text):
    status_bar.config(text=f"Speaking: {text}")
    engine.say(text)
    engine.runAndWait()
    status_bar.config(text="Ready")

 
def create_table_if_not_exists():
    try:
        conn = mysql.connector.connect(
            host="localhost", user="root", password="2304", database="demo"
        )
        cursor = conn.cursor()
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS command_logs (
                id INT AUTO_INCREMENT PRIMARY KEY,
                command VARCHAR(255),
                status VARCHAR(100),
                timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
            )
        """)
        conn.commit()
        cursor.close()
        conn.close()
    except Exception as e:
        print("DB Error:", e)


def log_command(command, status):
    try:
        conn = mysql.connector.connect(
            host="localhost", user="root", password="2304", database="demo"
        )
        cursor = conn.cursor()
        cursor.execute(
            "INSERT INTO command_logs (command, status) VALUES (%s, %s)",
            (command, status),
        )
        conn.commit()
        cursor.close()
        conn.close()
    except:
        pass


 
def listen():
    if not microphone_state:
        speak("Microphone is off")
        return ""

    r = sr.Recognizer()
    with sr.Microphone() as source:
        status_bar.config(text="Listening...")
        r.adjust_for_ambient_noise(source, duration=1)

        try:
            audio = r.listen(source, timeout=5, phrase_time_limit=8)
            command = r.recognize_google(audio)
            return command.lower()
        except:
            speak("I didn't understand")
            return ""


 
def open_app():
    speak("Which app should I open?")
    app = listen()
    if app:
        os.system(f"start {app}")
        log_command(f"Open App: {app}", "Success")
        update_command_history(f"Opened {app}")


def run_multimedia():
    path = filedialog.askopenfilename(
        filetypes=[("Media Files", "*.mp3 *.mp4 *.wav *.avi")]
    )
    if path:
        os.startfile(path)
        speak("Playing media")
        update_command_history("Media Played")
        log_command("Play Media", "Success")


def install_app():
    speak("Which app should I install?")
    app = listen()
    if app:
        os.system(f"winget install {app}")
        speak(f"Installing {app}")
        update_command_history(f"Installed {app}")
        log_command("Install App", "Success")


def change_setting():
    speak("Which setting?")
    setting = listen()

    if "wifi" in setting:
        os.system("start ms-settings:network-wifi")
    elif "bluetooth" in setting:
        os.system("start ms-settings:bluetooth")
    elif "display" in setting:
        os.system("start ms-settings:display")
    else:
        os.system("control")

    update_command_history("Opened system settings")
    log_command("Settings Changed", "Success")


def photo_editing():
    os.system("start mspaint")
    speak("Opening photo editor")
    update_command_history("Photo editor opened")
    log_command("Photo Editor", "Success")


 
def show_system_monitor():
    cpu = psutil.cpu_percent(interval=1)
    ram = psutil.virtual_memory().percent
    battery = psutil.sensors_battery()

    battery_status = f"{battery.percent}%" if battery else "Not Available"

    info = f"""
System Info

CPU Usage: {cpu}%
RAM Usage: {ram}%
Battery: {battery_status}
OS: {platform.system()} {platform.release()}
"""

    messagebox.showinfo("System Monitor", info)
    update_command_history("Viewed System Monitor")
    log_command("System Monitor", "Success")


 
def power_options():
    choice = messagebox.askquestion(
        "Power Options",
        "YES → Shutdown\nNO → Restart\nCANCEL → Sleep"
    )

    if choice == "yes":
        os.system("shutdown /s /t 1")
        action = "Shutdown"
    elif choice == "no":
        os.system("shutdown /r /t 1")
        action = "Restart"
    else:
        os.system("rundll32.exe powrprof.dll,SetSuspendState 0,1,0")
        action = "Sleep"

    update_command_history(action)
    log_command(action, "Success")


 
def toggle_theme():
    global dark_mode
    dark_mode = not dark_mode

    bg = "#1e1e1e" if dark_mode else "#f0f8ff"
    fg = "white" if dark_mode else "black"

    root.configure(bg=bg)
    main_frame.configure(bg=bg)
    history_frame.configure(bg=bg)
    button_frame.configure(bg=bg)
    bottom_frame.configure(bg=bg)

    command_history.configure(bg="#2b2b2b" if dark_mode else "white", fg=fg)

    speak("Dark mode enabled" if dark_mode else "Light mode enabled")
    update_command_history("Theme Changed")

 
def toggle_microphone():
    global microphone_state
    microphone_state = not microphone_state

    mic_button.config(
        text="Microphone: ON" if microphone_state else "Microphone: OFF",
        bg="lightgreen" if microphone_state else "lightcoral"
    )


 
def update_command_history(text):
    time = datetime.now().strftime("%H:%M:%S")
    command_history.insert(tk.END, f"[{time}] {text}\n")
    command_history.see(tk.END)


 
root = tk.Tk()
root.title("Computer Copilot Pro")
root.geometry("750x800")
root.configure(bg="#f0f8ff")

header = tk.Label(root, text="COMPUTER COPILOT", font=("Arial", 24, "bold"),
                  bg="#4682b4", fg="white")
header.pack(fill="x")

main_frame = tk.Frame(root, bg="#f0f8ff")
main_frame.pack(expand=True, fill="both")

history_frame = tk.LabelFrame(main_frame, text="Command History", font=("Arial", 14))
history_frame.pack(fill="both", expand=True, padx=10, pady=10)

command_history = scrolledtext.ScrolledText(history_frame, height=12)
command_history.pack(fill="both", expand=True)

button_frame = tk.Frame(main_frame, bg="#f0f8ff")
button_frame.pack(pady=10)

btn = {"font": ("Arial", 12), "width": 22, "pady": 6}

tk.Button(button_frame, text="Open App", command=open_app, **btn).grid(row=0, column=0)
tk.Button(button_frame, text="Play Media", command=run_multimedia, **btn).grid(row=0, column=1)
tk.Button(button_frame, text="Install App", command=install_app, **btn).grid(row=1, column=0)
tk.Button(button_frame, text="System Settings", command=change_setting, **btn).grid(row=1, column=1)
tk.Button(button_frame, text="Photo Editor", command=photo_editing, **btn).grid(row=2, column=0)
tk.Button(button_frame, text="System Monitor", command=show_system_monitor, **btn).grid(row=2, column=1)
tk.Button(button_frame, text="Dark / Light Mode", command=toggle_theme, **btn).grid(row=3, column=0)
tk.Button(button_frame, text="Power Options", command=power_options, **btn).grid(row=3, column=1)

mic_button = tk.Button(button_frame, text="Microphone: ON", bg="lightgreen",
                       command=toggle_microphone, **btn)
mic_button.grid(row=4, column=0, columnspan=2)

bottom_frame = tk.Frame(root, bg="#f0f8ff")
bottom_frame.pack(fill="x")

status_bar = tk.Label(root, text="Ready", relief=tk.SUNKEN, anchor=tk.W)
status_bar.pack(fill="x")

 
create_table_if_not_exists()
speak("Computer Copilot is ready")
update_command_history("System Started")
log_command("Application Started", "Success")

root.mainloop()
