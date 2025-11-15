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
import os
from src.bot_core import TeveClub
from src.config import CREDENTIALS_FILE
from src.utils import load_credentials, save_credentials, get_icon_path, get_writable_path


class RoundedButton(tk.Canvas):
    """Custom rounded button widget"""
    def __init__(self, parent, text, command, bg_color="#3A7ABD", hover_color="#4A8ACD", 
                 text_color="white", width=200, height=45, border_color=None, border_width=0, 
                 gradient=False, **kwargs):
        super().__init__(parent, width=width, height=height, bg=parent.cget('bg'), 
                        highlightthickness=0, **kwargs)
        
        self.command = command
        self.bg_color = bg_color
        self.hover_color = hover_color
        self.text_color = text_color
        self.border_color = border_color or bg_color
        self.border_width = border_width
        self.width = width
        self.height = height
        self.gradient = gradient
        self._state = 'normal'  # normal or disabled
        self._disabled_color = "#9D8B7C"  # Grayed out color
        
        # For blue buttons (login/exit) - use solid color with border
        if gradient and bg_color == "#3A7ABD":
            self.bg_color = "#2E6BA6"  # Solid darker blue
            self.hover_color = "#3A7ABD"  # Lighter on hover
            self.border_color = "#154573"
            self.border_width = 3
        
        # Draw rounded rectangle with border
        if border_width > 0:
            # Draw border
            self.border_rect = self.create_rounded_rectangle(
                2, 2, width-2, height-2, radius=22, fill=self.border_color, outline=""
            )
            # Draw inner fill (no gradient, just solid color)
            inset = border_width
            self.rounded_rect = self.create_rounded_rectangle(
                2+inset, 2+inset, width-2-inset, height-2-inset, radius=20, fill=self.bg_color, outline=""
            )
        else:
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
                if hasattr(self, 'border_rect'):
                    self.itemconfig(self.border_rect, fill=self._disabled_color)
                self.unbind("<Enter>")
                self.unbind("<Leave>")
                self.unbind("<Button-1>")
                self.config(cursor="")
            else:
                self.itemconfig(self.rounded_rect, fill=self.bg_color)
                if hasattr(self, 'border_rect'):
                    self.itemconfig(self.border_rect, fill=self.border_color)
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
        super().__init__(parent, bg="#FFF9E6", **kwargs)
        
        # Create canvas for rounded border
        self.canvas = tk.Canvas(self, height=40, bg=parent.cget('bg'), 
                               highlightthickness=0, width=280)
        self.canvas.pack()
        
        # Draw rounded rectangle background
        self.bg_rect = self.canvas.create_rounded_rectangle(
            0, 0, 280, 40, radius=20, fill="#FFF9E6", outline="#8B6914", width=2
        )
        
        # Entry widget
        self.entry = tk.Entry(self.canvas, bg="#FFF9E6", fg="#8B4513", 
                            font=("Segoe UI", 10), relief="flat", 
                            bd=0, show=show, insertbackground="#3A7ABD")
        self.entry_window = self.canvas.create_window(140, 20, window=self.entry, width=250)
        
        self.placeholder = placeholder
        self.show_placeholder = not show  # Don't show placeholder for password
        
        if self.show_placeholder and placeholder:
            self.entry.insert(0, placeholder)
            self.entry.config(fg="#A0826B")
            self.entry.bind("<FocusIn>", self.on_focus_in)
            self.entry.bind("<FocusOut>", self.on_focus_out)
    
    def on_focus_in(self, event):
        if self.entry.get() == self.placeholder:
            self.entry.delete(0, tk.END)
            self.entry.config(fg="#8B4513")
    
    def on_focus_out(self, event):
        if not self.entry.get():
            self.entry.insert(0, self.placeholder)
            self.entry.config(fg="#A0826B")
    
    def get(self):
        value = self.entry.get()
        if self.show_placeholder and value == self.placeholder:
            return ""
        return value
    
    def insert(self, index, string):
        if self.show_placeholder:
            self.entry.config(fg="#8B4513")
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


class CustomDropdown(tk.Frame):
    """Custom dropdown widget matching webapp style"""
    def __init__(self, parent, items, on_select, bg_color="#E8D4A0", **kwargs):
        super().__init__(parent, bg=bg_color, **kwargs)
        
        self.items = items
        self.on_select = on_select
        self.bg_color = bg_color
        self.is_open = False
        
        # Main button
        self.button = RoundedButton(
            self, 
            items[0] if items else "Select...",
            command=self.toggle_dropdown,
            bg_color=bg_color,
            hover_color="#E8C090",
            text_color="#4A3820",
            border_color="#8B6914",
            border_width=3,
            width=300,
            height=45
        )
        self.button.pack()
        
        # Dropdown list (hidden by default)
        self.list_frame = tk.Frame(self, bg="#8B6914", bd=2, relief="solid")
        self.list_canvas = tk.Canvas(self.list_frame, bg="#FFF9E6", 
                                     highlightthickness=0, width=280, height=150)
        
        # Custom scrollbar for dropdown
        scrollbar_style = ttk.Style()
        scrollbar_style.configure("Dropdown.Vertical.TScrollbar",
                                 background="#D4A574",
                                 troughcolor="#FFF9E6",
                                 bordercolor="#8B6914",
                                 arrowcolor="#8B4513",
                                 relief="flat")
        scrollbar_style.map("Dropdown.Vertical.TScrollbar",
                           background=[('active', '#E8C090'), ('pressed', '#C09060')])
        
        self.list_scrollbar = ttk.Scrollbar(self.list_frame, orient="vertical", 
                                           command=self.list_canvas.yview,
                                           style="Dropdown.Vertical.TScrollbar")
        self.list_content = tk.Frame(self.list_canvas, bg="#FFF9E6")
        
        self.list_content.bind(
            "<Configure>",
            lambda e: self.list_canvas.configure(scrollregion=self.list_canvas.bbox("all"))
        )
        
        self.list_canvas.create_window((0, 0), window=self.list_content, anchor="nw")
        self.list_canvas.configure(yscrollcommand=self.list_scrollbar.set)
        
        self.list_canvas.pack(side="left", fill="both", expand=True)
        self.list_scrollbar.pack(side="right", fill="y")
        
        # Create list items
        for item in items:
            item_btn = tk.Button(
                self.list_content,
                text=item,
                bg="#FFF9E6",
                fg="#8B4513",
                activebackground="#E8D4A0",
                activeforeground="#8B4513",
                font=("Segoe UI", 9),
                relief="flat",
                anchor="center",
                padx=0,
                pady=8,
                width=35,
                command=lambda i=item: self.select_item(i)
            )
            item_btn.pack(fill="x", expand=True)
            item_btn.bind("<Enter>", lambda e, b=item_btn: b.config(bg="#E8D4A0"))
            item_btn.bind("<Leave>", lambda e, b=item_btn: b.config(bg="#FFF9E6"))
    
    def toggle_dropdown(self):
        if self.is_open:
            self.list_frame.pack_forget()
            self.is_open = False
        else:
            self.list_frame.pack(pady=(5, 0))
            self.is_open = True
    
    def select_item(self, item):
        # Update button text (truncate if too long)
        display_text = item if len(item) <= 30 else item[:27] + "..."
        self.button.itemconfig(self.button.text_id, text=display_text)
        self.list_frame.pack_forget()
        self.is_open = False
        if self.on_select:
            self.on_select(item)
    
    def set_selection(self, item):
        """Set the selected item without triggering callback"""
        if item in self.items:
            display_text = item if len(item) <= 30 else item[:27] + "..."
            self.button.itemconfig(self.button.text_id, text=display_text)


class LoginApp:
    """Main application window for Teveclub bot with modern rounded UI"""
    
    # Color scheme matching Teveclub.hu webapp exactly
    BG_COLOR = "#E8D4A0"          # Tan/sandy background from webapp
    PANEL_BG = "#FFF9E6"          # Light cream panel background
    BUTTON_BLUE_COLOR = "#3A7ABD" # Blue for login/exit buttons
    PRIMARY_COLOR = "#8B4513"     # Brown for primary text/titles (SaddleBrown)
    SECONDARY_COLOR = "#4A8ACD"   # Light blue gradient for button hover
    ACTION_BTN_COLOR = "#D4A574"  # Light brown fill for action buttons
    ACTION_BTN_BORDER = "#8B6914" # Dark brown border for action buttons
    ACTION_BTN_HOVER = "#E8C090"  # Lighter brown hover
    TEXT_COLOR = "#8B4513"        # Brown text (SaddleBrown)
    ACCENT_COLOR = "#8B6914"      # Dark golden brown border
    SUCCESS_COLOR = "#228B22"     # Forest green
    ERROR_COLOR = "#CD5C5C"       # Indian red
    
    def __init__(self, root):
        """
        Initialize the application
        
        Args:
            root: The tkinter root window
        """
        self.root = root
        self.root.title("🐪 Teveclub Bot")
        # Geometry set by run_gui()
        self.root.resizable(False, False)
        self.root.configure(bg=self.BG_COLOR)
        
        # Keep normal Windows title bar, just add a draggable bar inside
        
        # Draggable bar at top
        self.title_bar = tk.Frame(self.root, bg="#8B6914", relief="flat", bd=0, height=40)
        self.title_bar.pack(fill="x", side="top")
        self.title_bar.pack_propagate(False)
        
        # Title text
        self.title_label = tk.Label(self.title_bar, text="🐪 Teveclub Bot Manager", 
                                   bg="#8B6914", fg="#FFF9E6",
                                   font=("Segoe UI", 11, "bold"))
        self.title_label.pack(side="left", padx=15, pady=8)
        
        # Make bar draggable
        self.title_bar.bind("<Button-1>", self.start_move)
        self.title_bar.bind("<B1-Motion>", self.do_move)
        self.title_label.bind("<Button-1>", self.start_move)
        self.title_label.bind("<B1-Motion>", self.do_move)
        
        self.use_custom_titlebar = False
        
        self.username = ""
        self.password = ""
        self.teve = None  # Store the bot instance
        self._operation_running = False  # Track if operation is in progress
        
        # Get writable path for credentials
        self.credentials_path = get_writable_path(CREDENTIALS_FILE)
        
        self.setup_icon()
        self.show_login_panel()
    
    def minimize_window(self):
        """Minimize the window"""
        self.root.iconify()
    
    def start_move(self, event):
        """Start moving the window"""
        self.x = event.x
        self.y = event.y
    
    def do_move(self, event):
        """Move the window"""
        deltax = event.x - self.x
        deltay = event.y - self.y
        x = self.root.winfo_x() + deltax
        y = self.root.winfo_y() + deltay
        self.root.geometry(f"+{x}+{y}")
    
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
        
        # Main background container
        bg_container = tk.Frame(self.root, bg=self.BG_COLOR)
        bg_container.pack(expand=True, fill="both", padx=20, pady=20)
        
        # Island panel with shadow effect (kept inside window)
        panel_canvas = tk.Canvas(bg_container, bg=self.BG_COLOR, highlightthickness=0)
        panel_canvas.pack(expand=True, fill="both")
        
        # Get canvas size after packing
        self.root.update_idletasks()
        canvas_width = panel_canvas.winfo_width()
        canvas_height = panel_canvas.winfo_height()
        
        # Calculate panel size (leave margin)
        panel_width = min(400, canvas_width - 20)
        panel_height = min(600, canvas_height - 20)
        
        # Center the panel
        x_offset = (canvas_width - panel_width) // 2
        y_offset = (canvas_height - panel_height) // 2
        
        # Draw shadow with multiple layers for semi-transparent effect
        # Each layer slightly darker than background to create blur effect
        for i in range(3):
            shadow_offset = 8 - i * 2
            shadow_colors = ["#C5B080", "#AFA070", "#8A7A50"]
            panel_canvas.create_rounded_rectangle(
                x_offset + shadow_offset, y_offset + shadow_offset,
                x_offset + panel_width + shadow_offset, y_offset + panel_height + shadow_offset,
                radius=15, fill=shadow_colors[i], outline=""
            )
        
        # Draw main panel island with border on ALL sides
        panel_canvas.create_rounded_rectangle(
            x_offset, y_offset,
            x_offset + panel_width, y_offset + panel_height,
            radius=15, fill=self.PANEL_BG, outline="#8B6914", width=3
        )
        
        # Container for content inside the island
        container = tk.Frame(panel_canvas, bg=self.PANEL_BG)
        panel_canvas.create_window(
            x_offset + panel_width // 2, 
            y_offset + panel_height // 2, 
            window=container, 
            width=panel_width - 60, 
            height=panel_height - 60
        )
        
        # Logo/Title area with camel emoji
        title_frame = tk.Frame(container, bg=self.PANEL_BG)
        title_frame.pack(pady=(20, 30))
        
        # Title with emoji
        title_label = tk.Label(title_frame, text="🐪 Teveclub", 
                              font=("Segoe UI", 28, "bold"), 
                              fg=self.PRIMARY_COLOR, bg=self.PANEL_BG)
        title_label.pack()
        
        subtitle_label = tk.Label(title_frame, text="Bot Login", 
                                 font=("Segoe UI", 12), 
                                 fg=self.TEXT_COLOR, bg=self.PANEL_BG)
        subtitle_label.pack(pady=(5, 0))
        
        # Username section
        username_frame = tk.Frame(container, bg=self.PANEL_BG)
        username_frame.pack(pady=(10, 5))
        
        username_label = tk.Label(username_frame, text="👤 Username", 
                                 font=("Segoe UI", 10, "bold"),
                                 fg=self.TEXT_COLOR, bg=self.PANEL_BG)
        username_label.pack(anchor="w", pady=(0, 5))
        
        self.username_entry = RoundedEntry(username_frame, placeholder="Enter your username")
        self.username_entry.pack()
        
        # Password section
        password_frame = tk.Frame(container, bg=self.PANEL_BG)
        password_frame.pack(pady=(15, 5))
        
        password_label = tk.Label(password_frame, text="🔒 Password", 
                                 font=("Segoe UI", 10, "bold"),
                                 fg=self.TEXT_COLOR, bg=self.PANEL_BG)
        password_label.pack(anchor="w", pady=(0, 5))
        
        self.password_entry = RoundedEntry(password_frame, show="●")
        self.password_entry.pack()
        
        # Try to load saved credentials
        credentials = load_credentials(self.credentials_path)
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
        button_frame = tk.Frame(container, bg=self.PANEL_BG)
        button_frame.pack(pady=(25, 10))
        
        login_button = RoundedButton(button_frame, "🚀 Login", 
                                    command=self.on_login_click,
                                    bg_color=self.BUTTON_BLUE_COLOR,
                                    hover_color=self.SECONDARY_COLOR,
                                    width=280, height=50,
                                    gradient=True)
        login_button.pack()
        
        # Status area
        self.login_status = tk.Label(container, text="", 
                                    font=("Segoe UI", 9),
                                    fg=self.TEXT_COLOR, 
                                    bg=self.PANEL_BG, 
                                    wraplength=350)
        self.login_status.pack(pady=15, fill="x")
    
    def show_main_panel(self):
        """Display the main interface after successful login with rounded modern design"""
        self.clear_window()
        
        # Main background container
        bg_container = tk.Frame(self.root, bg=self.BG_COLOR)
        bg_container.pack(expand=True, fill="both", padx=20, pady=20)
        
        # Island panel with shadow
        panel_canvas = tk.Canvas(bg_container, bg=self.BG_COLOR, highlightthickness=0)
        panel_canvas.pack(expand=True, fill="both")
        
        # Get canvas size
        self.root.update_idletasks()
        canvas_width = panel_canvas.winfo_width()
        canvas_height = panel_canvas.winfo_height()
        
        # Calculate panel size
        panel_width = min(390, canvas_width - 20)
        panel_height = min(640, canvas_height - 20)
        
        # Center the panel
        x_offset = (canvas_width - panel_width) // 2
        y_offset = (canvas_height - panel_height) // 2
        
        # Draw shadow with multiple layers for semi-transparent effect
        for i in range(3):
            shadow_offset = 8 - i * 2
            shadow_colors = ["#C5B080", "#AFA070", "#8A7A50"]
            panel_canvas.create_rounded_rectangle(
                x_offset + shadow_offset, y_offset + shadow_offset,
                x_offset + panel_width + shadow_offset, y_offset + panel_height + shadow_offset,
                radius=15, fill=shadow_colors[i], outline=""
            )
        
        # Draw panel island with border on ALL sides
        panel_canvas.create_rounded_rectangle(
            x_offset, y_offset,
            x_offset + panel_width, y_offset + panel_height,
            radius=15, fill=self.PANEL_BG, outline="#8B6914", width=3
        )
        
        # Wrapper for content + scrollbar (scrollbar outside the island)
        wrapper_frame = tk.Frame(panel_canvas, bg=self.BG_COLOR)
        panel_canvas.create_window(
            x_offset + panel_width // 2,
            y_offset + panel_height // 2,
            window=wrapper_frame
        )
        
        # Main container inside island (no scrollbar here)
        main_container = tk.Frame(wrapper_frame, bg=self.PANEL_BG)
        main_container.pack(side="left")
        
        # Canvas for scrolling inside island
        canvas = tk.Canvas(main_container, bg=self.PANEL_BG, highlightthickness=0, 
                          width=panel_width - 40, height=panel_height - 40)
        canvas.pack()
        
        # Scrollbar OUTSIDE island, to the right
        # Custom scrollbar style
        style = ttk.Style()
        style.theme_use('default')
        style.configure("Custom.Vertical.TScrollbar",
                       background="#D4A574",
                       troughcolor="#E8D4A0",
                       bordercolor="#8B6914",
                       arrowcolor="#8B4513",
                       relief="flat",
                       width=20)
        style.map("Custom.Vertical.TScrollbar",
                 background=[('active', '#E8C090'), ('pressed', '#C09060')])
        
        scrollbar = ttk.Scrollbar(wrapper_frame, orient="vertical", command=canvas.yview,
                                 style="Custom.Vertical.TScrollbar")
        scrollbar.pack(side="right", fill="y")
        
        scrollable_frame = tk.Frame(canvas, bg=self.PANEL_BG)
        
        scrollable_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )
        
        canvas.create_window((0, 0), window=scrollable_frame, anchor="nw", width=panel_width - 60)
        canvas.configure(yscrollcommand=scrollbar.set)
        
        # Enable mouse wheel scrolling
        def _on_mousewheel(event):
            canvas.yview_scroll(int(-1*(event.delta/120)), "units")
        
        # Bind mouse wheel to canvas and all child widgets
        canvas.bind_all("<MouseWheel>", _on_mousewheel)
        
        # Enable keyboard scrolling when window has focus
        def _on_key_press(event):
            if event.keysym == 'Down':
                canvas.yview_scroll(1, "units")
            elif event.keysym == 'Up':
                canvas.yview_scroll(-1, "units")
            elif event.keysym == 'Page_Down':
                canvas.yview_scroll(1, "pages")
            elif event.keysym == 'Page_Up':
                canvas.yview_scroll(-1, "pages")
        
        self.root.bind("<Down>", _on_key_press)
        self.root.bind("<Up>", _on_key_press)
        self.root.bind("<Prior>", _on_key_press)  # Page Up
        self.root.bind("<Next>", _on_key_press)   # Page Down
        
        # Welcome section
        welcome_canvas = tk.Canvas(scrollable_frame, height=80, bg=self.PANEL_BG, 
                                  highlightthickness=0, width=320)
        welcome_canvas.pack(pady=(10, 15))
        welcome_canvas.create_rounded_rectangle(5, 5, 315, 75, radius=20,
                                               fill="#FFF8F0", outline=self.ACCENT_COLOR, width=2)
        
        welcome_label = tk.Label(welcome_canvas, text=f"Welcome, {self.username}! 🐪", 
                               font=("Segoe UI", 16, "bold"),
                               fg=self.PRIMARY_COLOR, bg="#FFF8F0")
        welcome_canvas.create_window(160, 30, window=welcome_label)
        
        status_label = tk.Label(welcome_canvas, text="Ready to manage your Camel", 
                              font=("Segoe UI", 9),
                              fg=self.TEXT_COLOR, bg="#FFF8F0")
        welcome_canvas.create_window(160, 55, window=status_label)
        
        # Current State Section
        state_frame = tk.Frame(scrollable_frame, bg=self.PANEL_BG)
        state_frame.pack(fill="x", pady=(0, 15))
        
        state_canvas = tk.Canvas(state_frame, height=120, bg=self.PANEL_BG, 
                                highlightthickness=0, width=320)
        state_canvas.pack()
        state_canvas.create_rounded_rectangle(5, 5, 315, 115, radius=15,
                                             fill="#FFF8F0", outline=self.PRIMARY_COLOR, width=2)
        
        state_title = tk.Label(state_canvas, text="📊 Current Status", 
                             font=("Segoe UI", 11, "bold"),
                             fg=self.PRIMARY_COLOR, bg="#FFF8F0")
        state_canvas.create_window(160, 20, window=state_title)
        
        # Current food/drink/trick labels
        self.current_food_label = tk.Label(state_canvas, text="🍖 Food: Loading...", 
                                          font=("Segoe UI", 9),
                                          fg=self.TEXT_COLOR, bg="#FFF8F0")
        state_canvas.create_window(160, 50, window=self.current_food_label)
        
        self.current_drink_label = tk.Label(state_canvas, text="🥤 Drink: Loading...", 
                                           font=("Segoe UI", 9),
                                           fg=self.TEXT_COLOR, bg=self.PANEL_BG)
        state_canvas.create_window(160, 70, window=self.current_drink_label)
        
        self.current_trick_label = tk.Label(state_canvas, text="✨ Trick: Loading...", 
                                           font=("Segoe UI", 9),
                                           fg=self.TEXT_COLOR, bg=self.PANEL_BG, wraplength=300)
        state_canvas.create_window(160, 95, window=self.current_trick_label)
        
        # Food/Drink Selection Section
        selection_frame = tk.Frame(scrollable_frame, bg=self.PANEL_BG)
        selection_frame.pack(fill="x", pady=(0, 15))
        
        # Import config for food/drink lists
        from src.config import FREE_FOOD, FREE_DRINK
        
        # Store food/drink mappings
        self.food_map = {name: id for id, name in FREE_FOOD}
        self.drink_map = {name: id for id, name in FREE_DRINK}
        
        # Food selection
        food_label = tk.Label(selection_frame, text="🍖 Set Food:", 
                            font=("Segoe UI", 10, "bold"),
                            fg=self.TEXT_COLOR, bg=self.PANEL_BG)
        food_label.pack(pady=(0, 8))
        
        self.food_items = [name for id, name in FREE_FOOD]
        self.food_dropdown = CustomDropdown(
            selection_frame,
            self.food_items,
            self.on_food_selected,
            bg_color=self.PANEL_BG
        )
        self.food_dropdown.pack(pady=(0, 15))
        
        # Drink selection
        drink_label = tk.Label(selection_frame, text="🥤 Set Drink:", 
                             font=("Segoe UI", 10, "bold"),
                             fg=self.TEXT_COLOR, bg=self.PANEL_BG)
        drink_label.pack(pady=(0, 8))
        
        self.drink_items = [name for id, name in FREE_DRINK]
        self.drink_dropdown = CustomDropdown(
            selection_frame,
            self.drink_items,
            self.on_drink_selected,
            bg_color=self.PANEL_BG
        )
        self.drink_dropdown.pack(pady=(0, 10))
        
        # Action buttons with icons
        buttons_frame = tk.Frame(scrollable_frame, bg=self.PANEL_BG)
        buttons_frame.pack(pady=10)
        
        # Store button references for enabling/disabling
        self.action_buttons = []
        
        # Feed button
        feed_btn = RoundedButton(buttons_frame, "🍖 Feed Pet", 
                                command=self.feed_pet,
                                bg_color=self.PANEL_BG,
                                hover_color="#E8C090",
                                text_color="#4A3820",
                                border_color=self.ACTION_BTN_BORDER,
                                border_width=3,
                                width=320, height=55)
        feed_btn.pack(pady=8)
        self.action_buttons.append(feed_btn)
        
        # Learn button
        learn_btn = RoundedButton(buttons_frame, "📚 Learn Tricks", 
                                 command=self.learn,
                                 bg_color=self.PANEL_BG,
                                 hover_color="#E8C090",
                                 text_color="#4A3820",
                                 border_color=self.ACTION_BTN_BORDER,
                                 border_width=3,
                                 width=320, height=55)
        learn_btn.pack(pady=8)
        self.action_buttons.append(learn_btn)
        
        # Guess button
        guess_btn = RoundedButton(buttons_frame, "🎲 Guess Game", 
                                 command=self.guess_game,
                                 bg_color=self.PANEL_BG,
                                 hover_color="#E8C090",
                                 text_color="#4A3820",
                                 border_color=self.ACTION_BTN_BORDER,
                                 border_width=3,
                                 width=320, height=55)
        guess_btn.pack(pady=8)
        self.action_buttons.append(guess_btn)
        
        # Exit button (blue gradient like login)
        exit_btn = RoundedButton(buttons_frame, "🚪 Exit", 
                                command=self.exit_app,
                                bg_color=self.BUTTON_BLUE_COLOR,
                                hover_color=self.SECONDARY_COLOR,
                                width=320, height=50,
                                gradient=True)
        exit_btn.pack(pady=(15, 8))
        # Don't add exit button to action_buttons list
        
        # Status area with rounded container
        status_container = tk.Frame(scrollable_frame, bg=self.PANEL_BG)
        status_container.pack(pady=(15, 0), fill="x")
        
        status_canvas = tk.Canvas(status_container, height=70, bg=self.PANEL_BG,
                                 highlightthickness=0, width=320)
        status_canvas.pack()
        status_canvas.create_rounded_rectangle(5, 5, 315, 65, radius=15,
                                              fill=self.PANEL_BG, outline=self.ACCENT_COLOR, width=1)
        
        status_title = tk.Label(status_canvas, text="📊 Status:", 
                              font=("Segoe UI", 9, "bold"),
                              fg=self.TEXT_COLOR, bg=self.PANEL_BG)
        status_canvas.create_window(45, 20, window=status_title)
        
        self.status_text = tk.Label(status_canvas, text="Ready", 
                                   font=("Segoe UI", 9),
                                   fg=self.SUCCESS_COLOR, 
                                   bg=self.PANEL_BG,
                                   wraplength=280, justify="left")
        status_canvas.create_window(160, 45, window=self.status_text)
        
        # Load current state in background
        self.run_in_thread(self._load_current_state)
    
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
            "blue": self.BUTTON_BLUE_COLOR,
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
                
                # Save credentials with better error handling
                success, error_msg = save_credentials(self.credentials_path, self.username, self.password)
                if not success:
                    # Show warning but don't block - login was successful
                    print(f"Warning: Could not save credentials: {error_msg}")
                    self.safe_ui_update(lambda: messagebox.showwarning(
                        "Credentials Not Saved",
                        f"Login successful, but credentials could not be saved:\n\n{error_msg}\n\n"
                        "You'll need to enter your password next time.\n\n"
                        "Tip: Try running as Administrator or check file permissions."
                    ))
                
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
    
    def on_food_selected(self, selection):
        """Handle food selection from custom dropdown"""
        if not self.teve:
            return
        
        # Get food ID from name
        food_id = self.food_map.get(selection)
        if food_id is None:
            return
        
        # Run in thread
        self.run_in_thread(self._do_set_food, food_id)
    
    def _do_set_food(self, food_id):
        """Set food in background thread"""
        try:
            self.safe_ui_update(lambda: self.update_status(f"🔄 Setting food to ID {food_id}...", "blue"))
            
            success = self.teve.set_food(food_id)
            
            if success:
                self.safe_ui_update(lambda: self.update_status(
                    f"✅ Food set successfully! 🍖", "green"))
                # Reload current state
                self.run_in_thread(self._load_current_state)
            else:
                self.safe_ui_update(lambda: self.update_status(
                    "❌ Failed to set food", "red"))
        except Exception as e:
            self.safe_ui_update(lambda: self.update_status(
                f"❌ Set food failed: {str(e)}", "red"))
        finally:
            self.safe_ui_update(self._operation_complete)
    
    def on_drink_selected(self, selection):
        """Handle drink selection from custom dropdown"""
        if not self.teve:
            return
        
        # Get drink ID from name
        drink_id = self.drink_map.get(selection)
        if drink_id is None:
            return
        
        # Run in thread
        self.run_in_thread(self._do_set_drink, drink_id)
    
    def _do_set_drink(self, drink_id):
        """Set drink in background thread"""
        try:
            self.safe_ui_update(lambda: self.update_status(f"🔄 Setting drink to ID {drink_id}...", "blue"))
            
            success = self.teve.set_drink(drink_id)
            
            if success:
                self.safe_ui_update(lambda: self.update_status(
                    f"✅ Drink set successfully! 🥤", "green"))
                # Reload current state
                self.run_in_thread(self._load_current_state)
            else:
                self.safe_ui_update(lambda: self.update_status(
                    "❌ Failed to set drink", "red"))
        except Exception as e:
            self.safe_ui_update(lambda: self.update_status(
                f"❌ Set drink failed: {str(e)}", "red"))
        finally:
            self.safe_ui_update(self._operation_complete)
    
    def _load_current_state(self):
        """Load and display current food/drink/trick in background thread"""
        try:
            from src.config import FREE_FOOD, FREE_DRINK
            
            # Get current food/drink
            current = self.teve.get_current_food_drink()
            if current:
                food_id = current.get('food_id')
                drink_id = current.get('drink_id')
                
                # Find names
                food_name = next((name for id, name in FREE_FOOD if id == food_id), f"ID:{food_id}")
                drink_name = next((name for id, name in FREE_DRINK if id == drink_id), f"ID:{drink_id}")
                
                self.safe_ui_update(lambda: self.current_food_label.config(
                    text=f"🍖 Food: {food_name}" if food_id is not None else "🍖 Food: Unknown"))
                self.safe_ui_update(lambda: self.current_drink_label.config(
                    text=f"🥤 Drink: {drink_name}" if drink_id is not None else "🥤 Drink: Unknown"))
                
                # Set dropdown selections to current food/drink
                if hasattr(self, 'food_dropdown') and food_name in self.food_items:
                    self.safe_ui_update(lambda: self.food_dropdown.set_selection(food_name))
                if hasattr(self, 'drink_dropdown') and drink_name in self.drink_items:
                    self.safe_ui_update(lambda: self.drink_dropdown.set_selection(drink_name))
            
            # Get current trick
            trick = self.teve.get_current_trick()
            if trick:
                self.safe_ui_update(lambda: self.current_trick_label.config(
                    text=f"✨ Trick: {trick}"))
            else:
                self.safe_ui_update(lambda: self.current_trick_label.config(
                    text="✨ Trick: No trick learned"))
                
        except Exception as e:
            print(f"Failed to load current state: {e}")
        finally:
            self.safe_ui_update(self._operation_complete)

    def exit_app(self):
        """Exit the application"""
        self.root.quit()


def run_gui():
    """Run the GUI application"""
    root = tk.Tk()
    
    # Center the window on screen
    window_width = 450
    window_height = 700
    screen_width = root.winfo_screenwidth()
    screen_height = root.winfo_screenheight()
    x = (screen_width - window_width) // 2
    y = (screen_height - window_height) // 2
    root.geometry(f"{window_width}x{window_height}+{x}+{y}")
    
    try:
        app = LoginApp(root)
        root.mainloop()
    except Exception as e:
        print(f"Error starting GUI: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    run_gui()
