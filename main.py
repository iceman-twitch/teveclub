import tkinter as tk
from tkinter import messagebox
from teveclub import teveclub
from icon import icon
import json
import os
from pathlib import Path


class LoginApp:
    def __init__(self, root):
        self.root = root
        # Create main window
        self.root.title("Teveclub")
        self.root.geometry("300x200")
        self.root.resizable(False, False)
        self.credentials = "credentials.json"
        self.username = ""
        self.password = ""
        
        self.setup_icon()
        
        self.setup_ui()
        
    def get_icon(self):
        """Enhanced icon path resolution with multiple fallbacks"""
        # Try development location first
        dev_icon = Path("icon.ico")
        if dev_icon.exists():
            return str(dev_icon)

        # PyInstaller bundle locations
        if getattr(sys, 'frozen', False):
            # 1. MEIPASS (onefile mode)
            meipass_icon = Path(getattr(sys, '_MEIPASS', '')) / "icon.ico"
            if meipass_icon.exists():
                return str(meipass_icon)
            
            # 2. Executable directory (onedir mode)
            exe_dir_icon = Path(sys.executable).parent / "icon.ico"
            if exe_dir_icon.exists():
                return str(exe_dir_icon)

        # cx_Freeze bundle location
        if hasattr(sys, 'frozen') and not getattr(sys, 'frozen', False):
            lib_icon = Path(sys.executable).parent / "lib" / "icon.ico"
            if lib_icon.exists():
                return str(lib_icon)

        # Final fallback to original behavior
        return "icon.ico" if not getattr(sys, 'frozen', False) else os.path.join(getattr(sys, '_MEIPASS', ''), "icon.ico")

    def setup_icon(self):
        """Safe icon loading with multiple attempts"""
        icon_path = self.get_icon()
        if not Path(icon_path).exists():
            return  # Skip if icon doesn't exist
            
        try:
            self.root.iconbitmap(icon_path)
        except:
            try:
                # Alternative Linux/Mac approach
                img = tk.PhotoImage(file=icon_path)
                self.root.tk.call('wm', 'iconphoto', self.root._w, img)
            except:
                pass  # Complete silent fallback
                
    def setup_ui(self):
        # Try to load saved credentials
        credentials = self.load_credentials()

        # Username Label and Entry
        username_label = tk.Label(self.root, text="Username:")
        username_label.pack(pady=(20, 0))

        self.username_entry = tk.Entry(self.root, width=30)
        self.username_entry.pack(pady=5)
        if credentials:
            self.username_entry.insert(0, credentials.get("username", ""))
            
        # Password Label and Entry
        password_label = tk.Label(self.root, text="Password:")
        password_label.pack()

        self.password_entry = tk.Entry(self.root, width=30, show="*")  # show="*" makes it display asterisks
        self.password_entry.pack(pady=5)
        if credentials:
            self.password_entry.insert(0, credentials.get("password", ""))

        # Start Button
        start_button = tk.Button(self.root, text="Start", command=self.on_start_click)
        start_button.pack(pady=10)
    
    def load_credentials(self):
        """Load saved credentials from JSON file if it exists"""
        if os.path.exists(self.credentials):
            try:
                with open(self.credentials, 'r') as f:
                    return json.load(f)
            except (json.JSONDecodeError, PermissionError):
                return None
        return None

    def save_credentials(self):
        """Save credentials to JSON file"""
        try:
            with open(self.credentials, 'w') as f:
                json.dump({"username": self.username, "password": self.password}, f)
            return True
        except (PermissionError, TypeError):
            return False

    def on_start_click(self):
        self.username = self.username_entry.get()
        self.password = self.password_entry.get()
        
        if not self.username or not self.password:
            messagebox.showwarning("Warning", "Please enter both username and password")
        else:
            # messagebox.showinfo("Success", f"Login successful!\nUsername: {self.username}\nPassword: {'*' * len(self.password)}")
            #CONSTRAINTS
            USER = str(self.username)
            PASSW = str(self.password)
            
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
                    if self.save_credentials():
                        pass
                    else:
                        messagebox.showerror("Error", "Could not save credentials")
                except:
                    messagebox.showinfo("Failed", "Guess Game failed!!")
            else:
                messagebox.showinfo("Failed", f"Login failed!\nUsername: {self.username}\nPassword: {'*' * len(self.password)}")



if __name__ == "__main__":
    root = tk.Tk()
    app = LoginApp(root)
    # Run the application
    root.mainloop()