import tkinter as tk
from tkinter import messagebox
from teveclub import teveclub
from icon import icon
import json
import os

CREDENTIALS_FILE = "credentials.json"

def load_credentials():
    """Load saved credentials from JSON file if it exists"""
    if os.path.exists(CREDENTIALS_FILE):
        try:
            with open(CREDENTIALS_FILE, 'r') as f:
                return json.load(f)
        except (json.JSONDecodeError, PermissionError):
            return None
    return None

def save_credentials(username, password):
    """Save credentials to JSON file"""
    try:
        with open(CREDENTIALS_FILE, 'w') as f:
            json.dump({"username": username, "password": password}, f)
        return True
    except (PermissionError, TypeError):
        return False

def on_start_click():
    username = username_entry.get()
    password = password_entry.get()
    
    if not username or not password:
        messagebox.showwarning("Warning", "Please enter both username and password")
    else:
        # messagebox.showinfo("Success", f"Login successful!\nUsername: {username}\nPassword: {'*' * len(password)}")
        #CONSTRAINTS
        USER = str(username)
        PASSW = str(password)
        
        #STARTBOTCLASS
        teve = teveclub(USER, PASSW)
        if teve.Login():
            try:
                teve.Food()
            except:
                messagebox.showinfo("Failed", "Feeding failed!!!")
            try:
                teve.Learn()
            except:
                messagebox.showinfo("Failed", "Learning failed!!!")
            try:
                teve.Guess()
                messagebox.showinfo("Success", "Your pet done all works for today!!")
                if save_credentials(username, password):
                    pass
                else:
                    messagebox.showerror("Error", "Could not save credentials")
            except:
                messagebox.showinfo("Failed", "Guess Game failed!!")
        else:
            messagebox.showinfo("Failed", f"Login failed!\nUsername: {username}\nPassword: {'*' * len(password)}")

# Create main window
root = tk.Tk()
root.title("Teveclub")
root.geometry("300x200")
root.resizable(False, False)  # <--- THIS LINE PREVENTS RESIZING

# Set window icon (replace 'icon.ico' with your actual icon file)
try:
    # For Windows
    root.iconbitmap('icon.ico')
except:
    try:
        # For Linux (requires converting to .xbm format)
        icon = tk.PhotoImage(file='icon.png')
        root.tk.call('wm', 'iconphoto', root._w, icon)
    except:
        print("Could not load icon file")

# Try to load saved credentials
credentials = load_credentials()

# Username Label and Entry
username_label = tk.Label(root, text="Username:")
username_label.pack(pady=(20, 0))

username_entry = tk.Entry(root, width=30)
username_entry.pack(pady=5)
if credentials:
    username_entry.insert(0, credentials.get("username", ""))
    
# Password Label and Entry
password_label = tk.Label(root, text="Password:")
password_label.pack()

password_entry = tk.Entry(root, width=30, show="*")  # show="*" makes it display asterisks
password_entry.pack(pady=5)
if credentials:
    password_entry.insert(0, credentials.get("password", ""))

# Start Button
start_button = tk.Button(root, text="Start", command=on_start_click)
start_button.pack(pady=10)

# Run the application
root.mainloop()