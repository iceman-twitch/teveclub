import tkinter as tk
from tkinter import messagebox
from teveclub import teveclub
import json
import os
from pathlib import Path
import sys

class LoginApp:
    def __init__(self, root):
        self.root = root
        # Create main window
        self.root.title("Teveclub")
        self.root.geometry("400x400")  # Increased height to accommodate status area
        self.root.resizable(False, False)
        self.credentials = "credentials.json"
        self.username = ""
        self.password = ""
        self.teve = None  # Store the session object
        
        self.setup_icon()
        self.show_login_panel()
        
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
                
    def clear_window(self):
        """Remove all widgets from the window"""
        for widget in self.root.winfo_children():
            widget.destroy()
    
    def show_login_panel(self):
        """Display the login interface"""
        self.clear_window()
        
        # Title
        title_label = tk.Label(self.root, text="Teveclub Login", font=("Arial", 16, "bold"))
        title_label.pack(pady=(20, 10))
        
        # Username Label and Entry
        username_label = tk.Label(self.root, text="Username:")
        username_label.pack(pady=(20, 0))

        self.username_entry = tk.Entry(self.root, width=30)
        self.username_entry.pack(pady=5)
        
        # Password Label and Entry
        password_label = tk.Label(self.root, text="Password:")
        password_label.pack()

        self.password_entry = tk.Entry(self.root, width=30, show="*")
        self.password_entry.pack(pady=5)
        
        # Try to load saved credentials
        credentials = self.load_credentials()
        if credentials:
            self.username_entry.insert(0, credentials.get("username", ""))
            self.password_entry.insert(0, credentials.get("password", ""))
            
        # Login Button
        login_button = tk.Button(self.root, text="Login", command=self.on_login_click, width=15)
        login_button.pack(pady=10)
        
        # Status area for login panel
        self.login_status = tk.Label(self.root, text="", fg="blue", wraplength=350)
        self.login_status.pack(pady=10, fill="x")
    
    def show_main_panel(self):
        """Display the main interface after successful login"""
        self.clear_window()
        
        # Welcome message
        welcome_label = tk.Label(self.root, text=f"Welcome, {self.username}!", font=("Arial", 14))
        welcome_label.pack(pady=(20, 10))
        
        # Action buttons
        eat_button = tk.Button(self.root, text="Feed Pet", command=self.feed_pet, width=20, height=2)
        eat_button.pack(pady=10)
        
        learn_button = tk.Button(self.root, text="Learn", command=self.learn, width=20, height=2)
        learn_button.pack(pady=10)
        
        guess_button = tk.Button(self.root, text="Guess Game", command=self.guess_game, width=20, height=2)
        guess_button.pack(pady=10)
        
        # Exit button
        exit_button = tk.Button(self.root, text="Exit", command=self.exit_app, width=20, height=2)
        exit_button.pack(pady=10)
        
        # Status area for main panel
        self.status_frame = tk.Frame(self.root)
        self.status_frame.pack(pady=10, fill="x", padx=20)
        
        status_label = tk.Label(self.status_frame, text="Status:", font=("Arial", 10, "bold"))
        status_label.pack(anchor="w")
        
        self.status_text = tk.Label(self.status_frame, text="Ready", fg="green", wraplength=350, justify="left")
        self.status_text.pack(anchor="w", fill="x")
    
    def update_status(self, message, color="black"):
        """Update the status text with a message and color"""
        self.status_text.config(text=message, fg=color)
    
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

    def on_login_click(self):
        self.username = self.username_entry.get()
        self.password = self.password_entry.get()
        
        if not self.username or not self.password:
            self.login_status.config(text="Please enter both username and password", fg="red")
        else:
            # Try to login
            self.login_status.config(text="Logging in...", fg="blue")
            self.root.update()  # Update the UI to show the status
            
            self.teve = teveclub(self.username, self.password)
            if self.teve.Login():
                self.login_status.config(text="Login successful!", fg="green")
                # Save credentials if login was successful
                if self.save_credentials():
                    pass
                else:
                    self.login_status.config(text="Login successful but could not save credentials", fg="orange")
                
                # Wait a moment before switching panels
                self.root.after(1000, self.show_main_panel)
            else:
                self.login_status.config(text="Login failed! Please check your credentials.", fg="red")

    def feed_pet(self):
        """Handle the feed action"""
        if self.teve:
            self.update_status("Feeding your pet...", "blue")
            try:
                success = self.teve.Food()
                if success:
                    self.update_status("Your pet has been fed successfully!", "green")
                else:
                    self.update_status("Feeding failed! Your pet may have already been fed today.", "orange")
            except Exception as e:
                self.update_status(f"Feeding failed with error: {str(e)}", "red")
        else:
            self.update_status("Not logged in. Please login again.", "red")

    def learn(self):
        """Handle the learn action"""
        if self.teve:
            self.update_status("Learning in progress...", "blue")
            try:
                success = self.teve.Learn()
                if success:
                    self.update_status("Learning completed successfully!", "green")
                else:
                    self.update_status("Learning failed! Your pet may have already learned today.", "orange")
            except Exception as e:
                self.update_status(f"Learning failed with error: {str(e)}", "red")
        else:
            self.update_status("Not logged in. Please login again.", "red")

    def guess_game(self):
        """Handle the guess game action"""
        if self.teve:
            self.update_status("Playing guess game...", "blue")
            try:
                success = self.teve.Guess()
                if success:
                    self.update_status("Guess game completed successfully!", "green")
                else:
                    self.update_status("Guess game failed! You may have already played today.", "orange")
            except Exception as e:
                self.update_status(f"Guess game failed with error: {str(e)}", "red")
        else:
            self.update_status("Not logged in. Please login again.", "red")

    def exit_app(self):
        """Exit the application"""
        self.root.quit()


if __name__ == "__main__":
    root = tk.Tk()
    app = LoginApp(root)
    # Run the application
    root.mainloop()