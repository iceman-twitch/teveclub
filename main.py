import tkinter as tk
from tkinter import messagebox
from teveclub import teveclub
from icon import icon
import json
import os


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
        """Get the correct path for the icon, whether in dev or PyInstaller bundle."""
        if getattr(sys, 'frozen', False):
            # PyInstaller bundle mode
            return os.path.join(sys._MEIPASS, "icon.ico")
        else:
            # Normal development mode
            return "icon.ico"
            
    def setup_icon(self):
        try:
            self.root.iconbitmap(self.get_icon())
        except:
            pass  # Silently fail if icon missing
        
    def setup_ui(self):
        # Try to load saved credentials
        credentials = self.load_credentials()

        # Username Label and Entry
        username_label = tk.Label(self.root, text="Username:")
        username_label.pack(pady=(20, 0))

        username_entry = tk.Entry(self.root, width=30)
        username_entry.pack(pady=5)
        if credentials:
            username_entry.insert(0, credentials.get("username", ""))
            
        # Password Label and Entry
        password_label = tk.Label(self.root, text="Password:")
        password_label.pack()

        password_entry = tk.Entry(self.root, width=30, show="*")  # show="*" makes it display asterisks
        password_entry.pack(pady=5)
        if credentials:
            password_entry.insert(0, credentials.get("password", ""))

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
        self.username = username_entry.get()
        self.password = password_entry.get()
        
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
                    if self.save_credentials():
                        pass
                    else:
                        messagebox.showerror("Error", "Could not save credentials")
                except:
                    messagebox.showinfo("Failed", "Guess Game failed!!")
            else:
                messagebox.showinfo("Failed", f"Login failed!\nUsername: {username}\nPassword: {'*' * len(password)}")



if __name__ == "__main__":
    root = tk.Tk()
    app = LoginApp(root)
    # Run the application
    root.mainloop()