"""
GUI Module for Teveclub Bot
Provides a graphical interface for interacting with the bot
Styled to match Teveclub.hu website with rounded, brownish theme
Uses threading to prevent UI freezing during operations
"""
import tkinter as tk
from tkinter import ttk, messagebox
from pathlib import Path
import threading
from src.bot_core import TeveClub
from src.config import CREDENTIALS_FILE
from src.utils import load_credentials, save_credentials, get_icon_path


class RoundedButton(tk.Canvas):
    """Custom rounded button widget"""
    def __init__(self, parent, text, command, bg_color="#8B6F47", hover_color="#A0826B", 
                 text_color="white", width=200, height=45, **kwargs):
        super().__init__(parent, width=width, height=height, bg=parent.cget('bg'), 
                        highlightthickness=0, **kwargs)
        
        self.command = command
        self.bg_color = bg_color
        self.hover_color = hover_color
        self.text_color = text_color
        self.width = width
        self.height = height
        self._state = 'normal'  # normal or disabled
        self._disabled_color = "#9D8B7C"  # Grayed out color
        
        # Draw rounded rectangle
        self.rounded_rect = self.create_rounded_rectangle(
            2, 2, width-2, height-2, radius=22, fill=bg_color, outline=""
        )
        
        # Add text
        self.text_id = self.create_text(
            width//2, height//2, text=text, fill=text_color, 
            font=("Segoe UI", 11, "bold")
        )
        
        # Bind events
        self.bind("<Enter>", self.on_enter)
        self.bind("<Leave>", self.on_leave)
        self.bind("<Button-1>", self.on_click)
        
    def config(self, **kwargs):
        """Configure button properties"""
        if 'state' in kwargs:
            self._state = kwargs['state']
            if self._state == 'disabled':
                self.itemconfig(self.rounded_rect, fill=self._disabled_color)
                self.unbind("<Enter>")
                self.unbind("<Leave>")
                self.unbind("<Button-1>")
                self.config(cursor="")
            else:
                self.itemconfig(self.rounded_rect, fill=self.bg_color)
                self.bind("<Enter>", self.on_enter)
                self.bind("<Leave>", self.on_leave)
                self.bind("<Button-1>", self.on_click)
        
    def create_rounded_rectangle(self, x1, y1, x2, y2, radius=25, **kwargs):
        """Create a rounded rectangle"""
        points = [
            x1+radius, y1,
            x1+radius, y1,
            x2-radius, y1,
            x2-radius, y1,
            x2, y1,
            x2, y1+radius,
            x2, y1+radius,
            x2, y2-radius,
            x2, y2-radius,
            x2, y2,
            x2-radius, y2,
            x2-radius, y2,
            x1+radius, y2,
            x1+radius, y2,
            x1, y2,
            x1, y2-radius,
            x1, y2-radius,
            x1, y1+radius,
            x1, y1+radius,
            x1, y1
        ]
        return self.create_polygon(points, smooth=True, **kwargs)
    
    def on_enter(self, event):
        if self._state == 'normal':
            self.itemconfig(self.rounded_rect, fill=self.hover_color)
            self.config(cursor="hand2")
        
    def on_leave(self, event):
        if self._state == 'normal':
            self.itemconfig(self.rounded_rect, fill=self.bg_color)
            self.config(cursor="")
        
    def on_click(self, event):
        if self._state == 'normal' and self.command:
            self.command()


class RoundedEntry(tk.Frame):
    """Custom rounded entry widget"""
    def __init__(self, parent, placeholder="", show="", **kwargs):
        super().__init__(parent, bg="#F5E6D3", **kwargs)
        
        # Create canvas for rounded border
        self.canvas = tk.Canvas(self, height=40, bg=parent.cget('bg'), 
                               highlightthickness=0, width=280)
        self.canvas.pack()
        
        # Draw rounded rectangle background
        self.bg_rect = self.canvas.create_rounded_rectangle(
            0, 0, 280, 40, radius=20, fill="#F5E6D3", outline="#8B6F47", width=2
        )
        
        # Entry widget
        self.entry = tk.Entry(self.canvas, bg="#F5E6D3", fg="#4A3728", 
                            font=("Segoe UI", 10), relief="flat", 
                            bd=0, show=show, insertbackground="#8B6F47")
        self.entry_window = self.canvas.create_window(140, 20, window=self.entry, width=250)
        
        self.placeholder = placeholder
        self.show_placeholder = not show  # Don't show placeholder for password
        
        if self.show_placeholder and placeholder:
            self.entry.insert(0, placeholder)
            self.entry.config(fg="#9D8B7C")
            self.entry.bind("<FocusIn>", self.on_focus_in)
            self.entry.bind("<FocusOut>", self.on_focus_out)
    
    def on_focus_in(self, event):
        if self.entry.get() == self.placeholder:
            self.entry.delete(0, tk.END)
            self.entry.config(fg="#4A3728")
    
    def on_focus_out(self, event):
        if not self.entry.get():
            self.entry.insert(0, self.placeholder)
            self.entry.config(fg="#9D8B7C")
    
    def get(self):
        value = self.entry.get()
        if self.show_placeholder and value == self.placeholder:
            return ""
        return value
    
    def insert(self, index, string):
        if self.show_placeholder:
            self.entry.config(fg="#4A3728")
        self.entry.insert(index, string)


# Add method to Canvas for rounded rectangles
def create_rounded_rectangle(self, x1, y1, x2, y2, radius=25, **kwargs):
    points = [
        x1+radius, y1,
        x1+radius, y1,
        x2-radius, y1,
        x2-radius, y1,
        x2, y1,
        x2, y1+radius,
        x2, y1+radius,
        x2, y2-radius,
        x2, y2-radius,
        x2, y2,
        x2-radius, y2,
        x2-radius, y2,
        x1+radius, y2,
        x1+radius, y2,
        x1, y2,
        x1, y2-radius,
        x1, y2-radius,
        x1, y1+radius,
        x1, y1+radius,
        x1, y1
    ]
    return self.create_polygon(points, smooth=True, **kwargs)

tk.Canvas.create_rounded_rectangle = create_rounded_rectangle


class LoginApp:
    """Main application window for Teveclub bot with modern rounded UI"""
    
    # Color scheme matching Teveclub.hu
    BG_COLOR = "#E8D7C3"          # Light brownish background
    PANEL_BG = "#F5E6D3"          # Lighter panel background
    PRIMARY_COLOR = "#8B6F47"     # Brown primary
    SECONDARY_COLOR = "#A0826B"   # Lighter brown
    TEXT_COLOR = "#4A3728"        # Dark brown text
    ACCENT_COLOR = "#D4A574"      # Gold accent
    SUCCESS_COLOR = "#6B8E23"     # Olive green
    ERROR_COLOR = "#A0522D"       # Sienna red
    
    def __init__(self, root):
        """
        Initialize the application
        
        Args:
            root: The tkinter root window
        """
        self.root = root
        self.root.title("🐪 Teveclub Bot")
        self.root.geometry("450x550")
        self.root.resizable(False, False)
        self.root.configure(bg=self.BG_COLOR)
        
        self.username = ""
        self.password = ""
        self.teve = None  # Store the bot instance
        self._operation_running = False  # Track if operation is in progress
        
        self.setup_icon()
        self.show_login_panel()
    
    def run_in_thread(self, target, *args):
        """
        Run a function in a separate thread to prevent UI freezing
        
        Args:
            target: Function to run
            *args: Arguments to pass to the function
        """
        if self._operation_running:
            messagebox.showwarning("Operation in Progress", 
                                  "Please wait for the current operation to complete.")
            return
        
        self._operation_running = True
        # Disable buttons during operation if on main panel
        if hasattr(self, 'action_buttons'):
            for btn in self.action_buttons:
                btn.config(state='disabled')
        
        thread = threading.Thread(target=target, args=args, daemon=True)
        thread.start()
    
    def _operation_complete(self):
        """Mark operation as complete and re-enable buttons"""
        self._operation_running = False
        if hasattr(self, 'action_buttons'):
            for btn in self.action_buttons:
                btn.config(state='normal')
    
    def safe_ui_update(self, callback):
        """
        Safely update UI from a thread
        
        Args:
            callback: Function to call on the main thread
        """
        self.root.after(0, callback)
        
    def setup_icon(self):
        """Safe icon loading with multiple attempts"""
        icon_path = get_icon_path()
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
        """Display the login interface with modern rounded design"""
        self.clear_window()
        
        # Main container
        container = tk.Frame(self.root, bg=self.BG_COLOR)
        container.pack(expand=True, fill="both", padx=30, pady=30)
        
        # Logo/Title area with camel emoji
        title_frame = tk.Frame(container, bg=self.PANEL_BG, relief="flat")
        title_frame.pack(pady=(0, 20), fill="x")
        
        # Add subtle shadow effect with canvas
        shadow_canvas = tk.Canvas(title_frame, height=100, bg=self.PANEL_BG, 
                                 highlightthickness=0)
        shadow_canvas.pack(fill="x")
        shadow_canvas.create_rounded_rectangle(10, 10, 380, 90, radius=20, 
                                              fill=self.PANEL_BG, outline=self.PRIMARY_COLOR, width=2)
        
        # Title with emoji
        title_label = tk.Label(shadow_canvas, text="🐪 Teveclub", 
                              font=("Segoe UI", 24, "bold"), 
                              fg=self.PRIMARY_COLOR, bg=self.PANEL_BG)
        shadow_canvas.create_window(195, 35, window=title_label)
        
        subtitle_label = tk.Label(shadow_canvas, text="Bot Login", 
                                 font=("Segoe UI", 11), 
                                 fg=self.TEXT_COLOR, bg=self.PANEL_BG)
        shadow_canvas.create_window(195, 65, window=subtitle_label)
        
        # Username section
        username_frame = tk.Frame(container, bg=self.BG_COLOR)
        username_frame.pack(pady=(10, 5))
        
        username_label = tk.Label(username_frame, text="👤 Username", 
                                 font=("Segoe UI", 10, "bold"),
                                 fg=self.TEXT_COLOR, bg=self.BG_COLOR)
        username_label.pack(anchor="w", pady=(0, 5))
        
        self.username_entry = RoundedEntry(username_frame, placeholder="Enter your username")
        self.username_entry.pack()
        
        # Password section
        password_frame = tk.Frame(container, bg=self.BG_COLOR)
        password_frame.pack(pady=(15, 5))
        
        password_label = tk.Label(password_frame, text="🔒 Password", 
                                 font=("Segoe UI", 10, "bold"),
                                 fg=self.TEXT_COLOR, bg=self.BG_COLOR)
        password_label.pack(anchor="w", pady=(0, 5))
        
        self.password_entry = RoundedEntry(password_frame, show="●")
        self.password_entry.pack()
        
        # Try to load saved credentials
        credentials = load_credentials(CREDENTIALS_FILE)
        if credentials:
            username = credentials.get("username", "")
            password = credentials.get("password", "")
            if username:
                self.username_entry.entry.delete(0, tk.END)
                self.username_entry.entry.insert(0, username)
                self.username_entry.entry.config(fg=self.TEXT_COLOR)
            if password:
                self.password_entry.entry.insert(0, password)
            
        # Login Button
        button_frame = tk.Frame(container, bg=self.BG_COLOR)
        button_frame.pack(pady=(25, 10))
        
        login_button = RoundedButton(button_frame, "🚀 Login", 
                                    command=self.on_login_click,
                                    bg_color=self.PRIMARY_COLOR,
                                    hover_color=self.SECONDARY_COLOR,
                                    width=280, height=50)
        login_button.pack()
        
        # Status area
        self.login_status = tk.Label(container, text="", 
                                    font=("Segoe UI", 9),
                                    fg=self.TEXT_COLOR, 
                                    bg=self.BG_COLOR, 
                                    wraplength=350)
        self.login_status.pack(pady=15, fill="x")
    
    def show_main_panel(self):
        """Display the main interface after successful login with rounded modern design"""
        self.clear_window()
        
        # Main container
        container = tk.Frame(self.root, bg=self.BG_COLOR)
        container.pack(expand=True, fill="both", padx=30, pady=20)
        
        # Welcome section
        welcome_canvas = tk.Canvas(container, height=80, bg=self.BG_COLOR, 
                                  highlightthickness=0)
        welcome_canvas.pack(fill="x", pady=(0, 20))
        welcome_canvas.create_rounded_rectangle(5, 5, 385, 75, radius=20,
                                               fill=self.PANEL_BG, outline=self.ACCENT_COLOR, width=2)
        
        welcome_label = tk.Label(welcome_canvas, text=f"Welcome, {self.username}! 🐪", 
                               font=("Segoe UI", 16, "bold"),
                               fg=self.PRIMARY_COLOR, bg=self.PANEL_BG)
        welcome_canvas.create_window(195, 30, window=welcome_label)
        
        status_label = tk.Label(welcome_canvas, text="Ready to manage your Teve", 
                              font=("Segoe UI", 9),
                              fg=self.TEXT_COLOR, bg=self.PANEL_BG)
        welcome_canvas.create_window(195, 55, window=status_label)
        
        # Action buttons with icons
        buttons_frame = tk.Frame(container, bg=self.BG_COLOR)
        buttons_frame.pack(pady=10)
        
        # Store button references for enabling/disabling
        self.action_buttons = []
        
        # Feed button
        feed_btn = RoundedButton(buttons_frame, "🍖 Feed Pet", 
                                command=self.feed_pet,
                                bg_color=self.PRIMARY_COLOR,
                                hover_color=self.SECONDARY_COLOR,
                                width=320, height=55)
        feed_btn.pack(pady=8)
        self.action_buttons.append(feed_btn)
        
        # Learn button
        learn_btn = RoundedButton(buttons_frame, "📚 Learn Tricks", 
                                 command=self.learn,
                                 bg_color=self.PRIMARY_COLOR,
                                 hover_color=self.SECONDARY_COLOR,
                                 width=320, height=55)
        learn_btn.pack(pady=8)
        self.action_buttons.append(learn_btn)
        
        # Guess button
        guess_btn = RoundedButton(buttons_frame, "🎲 Guess Game", 
                                 command=self.guess_game,
                                 bg_color=self.PRIMARY_COLOR,
                                 hover_color=self.SECONDARY_COLOR,
                                 width=320, height=55)
        guess_btn.pack(pady=8)
        self.action_buttons.append(guess_btn)
        
        # Exit button (different color)
        exit_btn = RoundedButton(buttons_frame, "🚪 Exit", 
                                command=self.exit_app,
                                bg_color="#6B5845",
                                hover_color="#7D6A57",
                                width=320, height=50)
        exit_btn.pack(pady=(15, 8))
        # Don't add exit button to action_buttons list
        
        # Status area with rounded container
        status_container = tk.Frame(container, bg=self.BG_COLOR)
        status_container.pack(pady=(15, 0), fill="x")
        
        status_canvas = tk.Canvas(status_container, height=70, bg=self.BG_COLOR,
                                 highlightthickness=0)
        status_canvas.pack(fill="x")
        status_canvas.create_rounded_rectangle(5, 5, 385, 65, radius=15,
                                              fill="#FFF8F0", outline=self.ACCENT_COLOR, width=1)
        
        status_title = tk.Label(status_canvas, text="📊 Status:", 
                              font=("Segoe UI", 9, "bold"),
                              fg=self.TEXT_COLOR, bg="#FFF8F0")
        status_canvas.create_window(50, 20, window=status_title)
        
        self.status_text = tk.Label(status_canvas, text="Ready", 
                                   font=("Segoe UI", 9),
                                   fg=self.SUCCESS_COLOR, 
                                   bg="#FFF8F0",
                                   wraplength=350, justify="left")
        status_canvas.create_window(195, 45, window=self.status_text)
    
    def update_status(self, message, color="black"):
        """
        Update the status text with a message and color
        
        Args:
            message (str): Status message to display
            color (str): Color for the text ("green", "blue", "orange", "red")
        """
        # Map color names to theme colors
        color_map = {
            "green": self.SUCCESS_COLOR,
            "blue": self.PRIMARY_COLOR,
            "orange": "#D4A574",
            "red": self.ERROR_COLOR,
            "black": self.TEXT_COLOR
        }
        actual_color = color_map.get(color, color)
        self.status_text.config(text=message, fg=actual_color)

    def on_login_click(self):
        """Handle login button click"""
        self.username = self.username_entry.get().strip()
        self.password = self.password_entry.get().strip()
        
        if not self.username or not self.password:
            self.login_status.config(text="⚠️ Please enter both username and password", fg=self.ERROR_COLOR)
        else:
            # Run login in separate thread
            self.run_in_thread(self._do_login)
    
    def _do_login(self):
        """Perform login operation in background thread"""
        # Update status on main thread
        self.safe_ui_update(lambda: self.login_status.config(
            text="🔄 Logging in...", fg=self.PRIMARY_COLOR))
        
        try:
            self.teve = TeveClub(self.username, self.password)
            if self.teve.login():
                # Success
                self.safe_ui_update(lambda: self.login_status.config(
                    text="✅ Login successful!", fg=self.SUCCESS_COLOR))
                
                # Save credentials
                save_credentials(CREDENTIALS_FILE, self.username, self.password)
                
                # Switch to main panel after delay
                self.safe_ui_update(lambda: self.root.after(1000, self.show_main_panel))
            else:
                # Failed
                self.safe_ui_update(lambda: self.login_status.config(
                    text="❌ Login failed! Check your credentials.", fg=self.ERROR_COLOR))
        except Exception as e:
            self.safe_ui_update(lambda: self.login_status.config(
                text=f"❌ Error: {str(e)}", fg=self.ERROR_COLOR))
        finally:
            self.safe_ui_update(self._operation_complete)

    def feed_pet(self):
        """Handle the feed action"""
        if not self.teve:
            self.update_status("❌ Not logged in. Please login again.", "red")
            return
        
        # Run in separate thread
        self.run_in_thread(self._do_feed)
    
    def _do_feed(self):
        """Perform feed operation in background thread"""
        try:
            # Update status on main thread
            self.safe_ui_update(lambda: self.update_status("🔄 Feeding your pet...", "blue"))
            
            success = self.teve.feed()
            
            if success:
                self.safe_ui_update(lambda: self.update_status(
                    "✅ Your pet has been fed successfully! 🍖", "green"))
            else:
                self.safe_ui_update(lambda: self.update_status(
                    "⚠️ Pet is already full or feeding not available.", "orange"))
        except Exception as e:
            self.safe_ui_update(lambda: self.update_status(
                f"❌ Feeding failed: {str(e)}", "red"))
        finally:
            self.safe_ui_update(self._operation_complete)

    def learn(self):
        """Handle the learn action"""
        if not self.teve:
            self.update_status("❌ Not logged in. Please login again.", "red")
            return
        
        # Run in separate thread
        self.run_in_thread(self._do_learn)
    
    def _do_learn(self):
        """Perform learn operation in background thread"""
        try:
            # Update status on main thread
            self.safe_ui_update(lambda: self.update_status("🔄 Learning in progress...", "blue"))
            
            success = self.teve.learn()
            
            if success:
                self.safe_ui_update(lambda: self.update_status(
                    "✅ Learning completed successfully! 📚", "green"))
            else:
                self.safe_ui_update(lambda: self.update_status(
                    "⚠️ No more tricks to learn!", "orange"))
        except Exception as e:
            self.safe_ui_update(lambda: self.update_status(
                f"❌ Learning failed: {str(e)}", "red"))
        finally:
            self.safe_ui_update(self._operation_complete)

    def guess_game(self):
        """Handle the guess game action"""
        if not self.teve:
            self.update_status("❌ Not logged in. Please login again.", "red")
            return
        
        # Run in separate thread
        self.run_in_thread(self._do_guess)
    
    def _do_guess(self):
        """Perform guess game operation in background thread"""
        try:
            # Update status on main thread
            self.safe_ui_update(lambda: self.update_status("🔄 Playing guess game...", "blue"))
            
            success = self.teve.guess()
            
            if success:
                self.safe_ui_update(lambda: self.update_status(
                    "✅ Guess game completed successfully! 🎲", "green"))
            else:
                self.safe_ui_update(lambda: self.update_status(
                    "⚠️ Guess game failed!", "orange"))
        except Exception as e:
            self.safe_ui_update(lambda: self.update_status(
                f"❌ Guess game failed: {str(e)}", "red"))
        finally:
            self.safe_ui_update(self._operation_complete)

    def exit_app(self):
        """Exit the application"""
        self.root.quit()


def run_gui():
    """Run the GUI application"""
    root = tk.Tk()
    app = LoginApp(root)
    root.mainloop()


if __name__ == "__main__":
    run_gui()
