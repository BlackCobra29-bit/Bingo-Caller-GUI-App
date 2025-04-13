import tkinter as tk
from tkinter import messagebox
import ttkbootstrap as ttk
from ttkbootstrap.constants import *
import random
from datetime import datetime
import pyttsx3
import threading
import time

class BingoCaller:
    def __init__(self, root):
        self.root = root
        self.root.title("Bingo Caller")
        self.root.geometry("1000x800")
        
        # Initialize wallet balance
        self.wallet_balance = 0.0

        # Initialize text-to-speech engine
        self.engine = pyttsx3.init()
        self.engine.setProperty('rate', 150)  # Speed of speech
        self.engine.setProperty('volume', 1.0)  # Volume (0.0 to 1.0)
        
        # Auto-caller state
        self.is_auto_calling = False
        self.auto_caller_thread = None
        self.call_interval = 3  # Default interval in seconds
        
        # Set theme
        style = ttk.Style()
        style.configure('TButton', font=('Helvetica', 10))
        style.configure('TLabel', font=('Helvetica', 10))
        
        # Game state
        self.called_numbers = []
        self.available_numbers = list(range(1, 76))
        self.current_number = None
        self.is_game_over = False
        self.start_time = None

        # Create main frame with padding
        self.main_frame = ttk.Frame(root, padding="20")
        self.main_frame.pack(fill=tk.BOTH, expand=True)

        # Header frame
        self.header_frame = ttk.Frame(self.main_frame)
        self.header_frame.pack(fill=tk.X, pady=20)

        # Left side of header (title)
        self.header = ttk.Label(
            self.header_frame,
            text="BINGO CALLER",
            font=("Helvetica", 20, "bold"),
            bootstyle="dark"
        )
        self.header.pack(side=tk.LEFT, padx=20)

        # Add wallet balance display
        self.wallet_frame = ttk.Frame(self.header_frame)
        self.wallet_frame.pack(side=tk.LEFT, padx=20)
        
        self.wallet_label = ttk.Label(
            self.wallet_frame,
            text=f"Balance: {self.format_currency(self.wallet_balance)} Birr",
            font=("Helvetica", 12),
            bootstyle="dark"
        )
        self.wallet_label.pack(side=tk.LEFT, padx=5)

        self.add_wallet_btn = ttk.Button(
            self.wallet_frame,
            text="Add Wallet",
            command=self.show_wallet_dialog,
            bootstyle="success",
            width=10
        )
        self.add_wallet_btn.pack(side=tk.LEFT, padx=5)

        # Control buttons in header (right side)
        self.button_frame = ttk.Frame(self.header_frame)
        self.button_frame.pack(side=tk.RIGHT, padx=20)

        self.start_button = ttk.Button(
            self.button_frame,
            text="Start Game",
            command=self.start_game,
            bootstyle="success",
            width=12,
            state=tk.DISABLED  # Start disabled by default
        )
        self.start_button.pack(side=tk.LEFT, padx=5)

        self.call_button = ttk.Button(
            self.button_frame,
            text="Call Number",
            command=self.call_number,
            bootstyle="primary",
            width=12,
            state=tk.DISABLED
        )
        self.call_button.pack(side=tk.LEFT, padx=5)

        self.auto_call_button = ttk.Button(
            self.button_frame,
            text="Auto Call",
            command=self.toggle_auto_call,
            bootstyle="warning",
            width=12,
            state=tk.DISABLED
        )
        self.auto_call_button.pack(side=tk.LEFT, padx=5)

        self.reset_button = ttk.Button(
            self.button_frame,
            text="Reset Game",
            command=self.reset_game,
            bootstyle="danger",
            width=12
        )
        self.reset_button.pack(side=tk.LEFT, padx=5)

        # Called numbers display with modern card appearance
        self.called_numbers_frame = ttk.LabelFrame(
            self.main_frame,
            text="Called Numbers",
            bootstyle="dark",
            padding="20"
        )
        self.called_numbers_frame.pack(fill=tk.X, padx=20, pady=20)

        # Create a frame for the number grid with dark background
        self.numbers_grid_frame = ttk.Frame(self.called_numbers_frame, bootstyle="dark")
        self.numbers_grid_frame.pack(fill=tk.X)

        # Configure dark background
        style = ttk.Style()
        style.configure('Bingo.TLabel', 
                       font=("Helvetica", 18, "bold"),
                       foreground='red', 
                       background='#1e1e1e')
        style.configure('Number.TButton', 
            font=("Helvetica", 14),
                       foreground='#666666', 
                       background='#1e1e1e',
                       borderwidth=0,
                       relief="flat")
        style.configure('Called.TButton', 
                       font=("Helvetica", 14, "bold"),
                       foreground='white', 
                       background='#1e1e1e',
                       borderwidth=0,
                       relief="flat")

        # Create left side frame for BINGO letters
        self.letters_frame = ttk.Frame(self.numbers_grid_frame, bootstyle="dark")
        self.letters_frame.pack(side=tk.LEFT, padx=(0, 10))

        # Create BINGO letters vertically
        bingo_letters = ['B', 'I', 'N', 'G', 'O']
        for row, letter in enumerate(bingo_letters):
            letter_frame = ttk.Frame(self.letters_frame, bootstyle="dark")
            letter_frame.pack(fill=tk.BOTH, expand=True)
            
            letter_label = ttk.Label(
                letter_frame,
                text=letter,
                style='Bingo.TLabel',
                anchor="center",
                width=2
            )
            letter_label.pack(fill=tk.BOTH, expand=True)

        # Create numbers grid frame
        self.grid_frame = ttk.Frame(self.numbers_grid_frame, bootstyle="dark")
        self.grid_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        # Configure row and column weights for equal sizing
        for i in range(5):  # 5 rows
            self.grid_frame.rowconfigure(i, weight=1)
        for i in range(15):  # 15 columns
            self.grid_frame.columnconfigure(i, weight=1)

        # Create a dictionary to store all number buttons
        self.number_buttons = {}
        
        # Create 5 rows and 15 columns for numbers
        for row in range(5):  # 5 rows for B,I,N,G,O
            for col in range(15):  # 15 numbers per row
                number = row * 15 + col + 1
                number_frame = ttk.Frame(self.grid_frame, bootstyle="dark")
                number_frame.grid(row=row, column=col, sticky="nsew", padx=1, pady=1)
                
                btn = ttk.Label(
                    number_frame,
                    text=str(number),
                    style='Number.TButton',
                    anchor="center"
                )
                btn.pack(fill=tk.BOTH, expand=True)
                self.number_buttons[number] = btn

        # Create scrollable frame for the number display only
        self.controls_canvas = tk.Canvas(self.main_frame)
        self.controls_canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, pady=(0, 20))
        
        # Add scrollbar for controls
        self.controls_scrollbar = ttk.Scrollbar(
            self.main_frame,
            orient="vertical",
            command=self.controls_canvas.yview,
            bootstyle="dark-round"
        )
        self.controls_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        # Configure the canvas
        self.controls_canvas.configure(yscrollcommand=self.controls_scrollbar.set)
        
        # Create frame for controls inside canvas
        self.controls_frame = ttk.Frame(self.controls_canvas)
        self.controls_canvas.create_window((0, 0), window=self.controls_frame, anchor="nw", width=self.controls_canvas.winfo_width())
        
        # Current number display with card-like appearance
        self.number_frame = ttk.Frame(self.controls_frame)
        self.number_frame.pack(pady=20, fill=tk.X)
        
        self.number_display = ttk.Label(
            self.number_frame,
            text="Ready to Start",
            font=("Helvetica", 80, "bold"),
            bootstyle="dark",
            state="readonly"
        )
        self.number_display.pack(pady=20)

        # Timer display with modern styling
        self.timer_frame = ttk.Frame(self.controls_frame)
        self.timer_frame.pack(pady=20)

        self.timer_label = ttk.Label(
            self.timer_frame,
            text="Time: 00:00",
            font=("Helvetica", 16),
            bootstyle="dark"
        )
        self.timer_label.pack()

        # Status bar
        self.status_bar = ttk.Label(
            self.controls_frame,
            text="Ready",
            bootstyle="dark",
            font=("Helvetica", 8)
        )
        self.status_bar.pack(side=tk.BOTTOM, fill=tk.X, pady=10)

        # Bind the controls frame to update scroll region
        self.controls_frame.bind('<Configure>', self._configure_scroll_region)

        # Create a frame for called numbers history
        self.history_frame = ttk.Frame(self.called_numbers_frame, bootstyle="dark")
        self.history_frame.pack(fill=tk.X, pady=(20, 0))

        # Configure styles for the colored circles
        style.configure('Circle.B.TLabel',
                       font=("Helvetica", 12, "bold"),
                       foreground='black',
                       background='#FFB800')  # Yellow for B
        style.configure('Circle.I.TLabel',
                       font=("Helvetica", 12, "bold"),
                       foreground='white',
                       background='#FF0000')  # Red for I
        style.configure('Circle.N.TLabel',
                       font=("Helvetica", 12, "bold"),
                       foreground='white',
                       background='#0000FF')  # Blue for N
        style.configure('Circle.G.TLabel',
                       font=("Helvetica", 12, "bold"),
                       foreground='white',
                       background='#008000')  # Green for G
        style.configure('Circle.O.TLabel',
                       font=("Helvetica", 12, "bold"),
                       foreground='white',
                       background='#008000')  # Green for O

        # Frame to hold the circles
        self.circles_frame = ttk.Frame(self.history_frame, bootstyle="dark")
        self.circles_frame.pack(fill=tk.X, pady=10)

        # List to keep track of circle labels
        self.history_circles = []

    def update_interval(self, value):
        self.call_interval = float(value)
        self.interval_value.config(text=f"{int(float(value))}")

    def auto_call_loop(self):
        while self.is_auto_calling and not self.is_game_over:
            self.call_number()
            time.sleep(self.call_interval)

    def toggle_auto_call(self):
        if not self.is_auto_calling:
            self.is_auto_calling = True
            self.auto_call_button.config(text="Stop Auto", bootstyle="danger")
            self.call_button.config(state=tk.DISABLED)
            self.auto_caller_thread = threading.Thread(target=self.auto_call_loop)
            self.auto_caller_thread.start()
            self.status_bar.config(text="Auto-calling numbers...")
        else:
            self.is_auto_calling = False
            self.auto_call_button.config(text="Auto Call", bootstyle="warning")
            self.call_button.config(state=tk.NORMAL)
            self.status_bar.config(text="Auto-calling stopped")

    def update_voice_rate(self, value):
        self.engine.setProperty('rate', int(float(value)))

    def update_voice_volume(self, value):
        self.engine.setProperty('volume', float(value) / 100)

    def speak_number(self, number):
        def speak():
            # Calculate the letter based on the number
            letter = 'B' if number <= 15 else 'I' if number <= 30 else 'N' if number <= 45 else 'G' if number <= 60 else 'O'
            self.engine.say(f"{letter} {number}")
            self.engine.runAndWait()
        
        # Run speech in a separate thread to avoid freezing the GUI
        threading.Thread(target=speak).start()

    def start_game(self):
        if self.wallet_balance <= 0:
            messagebox.showerror(
                "Insufficient Balance",
                "Please add money to your wallet first!\n\nClick the 'Add Wallet' button to add funds."
            )
            return

        self.start_time = datetime.now()
        self.start_button.config(state=tk.DISABLED)
        self.call_button.config(state=tk.NORMAL)
        self.auto_call_button.config(state=tk.NORMAL)
        self.number_display.config(text="Click 'Call Number' to start")
        self.update_timer()
        self.status_bar.config(text="Game Started")
        self.speak_number("Game started")

    def call_number(self):
        if not self.available_numbers:
            messagebox.showinfo("Game Over", "All numbers have been called!")
            self.is_game_over = True
            self.call_button.config(state=tk.DISABLED)
            self.auto_call_button.config(state=tk.DISABLED)
            self.status_bar.config(text="Game Over - All numbers called")
            self.speak_number("Game over")
            return

        # Call a random number
        number = random.choice(self.available_numbers)
        self.available_numbers.remove(number)
        self.called_numbers.append(number)
        self.current_number = number

        # Update display with animation effect
        self.number_display.config(text=str(number))
        self.update_called_numbers()
        self.status_bar.config(text=f"Number {number} called")
        
        # Announce the number
        self.speak_number(number)

        # Check if game is over
        if not self.available_numbers:
            messagebox.showinfo("Game Over", "All numbers have been called!")
            self.is_game_over = True
            self.call_button.config(state=tk.DISABLED)
            self.auto_call_button.config(state=tk.DISABLED)
            self.status_bar.config(text="Game Over - All numbers called")
            self.speak_number("Game over")

    def reset_game(self):
        # Show warning message
        response = messagebox.askquestion(
            "Reset Game",
            "Are you sure you want to reset the game?\n\nThis will:\n• Clear all called numbers\n• Stop auto-calling\n• Reset the timer\n• Reset wallet balance",
            icon='warning'
        )
        
        if response == 'yes':
            # Stop auto-calling if active
            if self.is_auto_calling:
                self.is_auto_calling = False
                self.auto_call_button.config(text="Auto Call", bootstyle="warning")
        
        self.called_numbers = []
        self.available_numbers = list(range(1, 76))
        self.current_number = None
        self.is_game_over = False
        self.start_time = None
            
        # Reset wallet balance
        self.wallet_balance = 0.0
        self.wallet_label.config(text=f"Balance: {self.format_currency(self.wallet_balance)} Birr")
        self.add_wallet_btn.config(state=tk.NORMAL)  # Re-enable the Add Wallet button

        # Reset all number buttons to uncalled state
        for number in self.number_buttons:
            self.number_buttons[number].configure(
                style='Number.TButton'
            )

        self.number_display.config(text="Ready to Start")
        self.timer_label.config(text="Time: 00:00")
        
        self.start_button.config(state=tk.DISABLED)  # Disable start button since wallet is empty
        self.call_button.config(state=tk.DISABLED)
        self.auto_call_button.config(state=tk.DISABLED)
        self.status_bar.config(text="Game Reset - Ready to Start")
        self.speak_number("Game reset")

    def update_called_numbers(self):
        # Update the appearance of called numbers in the grid
        for number in self.called_numbers:
            if number in self.number_buttons:
                self.number_buttons[number].configure(
                    style='Called.TButton'
                )

        # Update the history circles
        # First, remove all existing circles
        for circle in self.history_circles:
            circle.destroy()
        self.history_circles.clear()

        # Create new circles for each called number
        for number in reversed(self.called_numbers[-5:]):  # Show last 5 numbers
            # Determine the letter and style
            if number <= 15:
                letter = 'B'
            elif number <= 30:
                letter = 'I'
            elif number <= 45:
                letter = 'N'
            elif number <= 60:
                letter = 'G'
            else:
                letter = 'O'

            # Create circle frame
            circle_label = ttk.Label(
                self.circles_frame,
                text=f"{letter}{number}",
                style=f'Circle.{letter}.TLabel',
                anchor="center",
                width=4
            )
            circle_label.pack(side=tk.LEFT, padx=5)
            self.history_circles.append(circle_label)

        # Update status bar
        if self.called_numbers:
            last_number = self.called_numbers[-1]
            letter = 'B' if last_number <= 15 else 'I' if last_number <= 30 else 'N' if last_number <= 45 else 'G' if last_number <= 60 else 'O'
            self.status_bar.config(text=f"Number {letter}{last_number} called")

    def update_timer(self):
        if self.start_time and not self.is_game_over:
            elapsed = datetime.now() - self.start_time
            minutes = elapsed.seconds // 60
            seconds = elapsed.seconds % 60
            self.timer_label.config(text=f"Time: {minutes:02d}:{seconds:02d}")
            self.root.after(1000, self.update_timer)

    def _configure_scroll_region(self, event):
        self.controls_canvas.configure(scrollregion=self.controls_canvas.bbox("all"))
        # Update the width of the window to match the canvas
        if event.widget == self.controls_frame:
            self.controls_canvas.itemconfig(
                self.controls_canvas.find_withtag("all")[0],
                width=self.controls_canvas.winfo_width()
            )

    def format_currency(self, amount):
        """Format amount with thousand separators and 2 decimal places"""
        return "{:,.2f}".format(amount)

    def show_wallet_dialog(self):
        # If wallet already has money, show error and return
        if self.wallet_balance > 0:
            messagebox.showerror(
                "Error",
                "Wallet can only be loaded once per game.\nPlease reset the game to add new funds."
            )
            return

        # Create a custom dialog
        dialog = tk.Toplevel(self.root)
        dialog.title("Add to Wallet")
        dialog.geometry("300x1")  # Set minimal height, will auto-adjust
        dialog.resizable(False, False)  # Make dialog non-resizable
        dialog.transient(self.root)  # Make dialog modal
        dialog.grab_set()  # Make dialog modal
        
        # Add content to dialog
        content_frame = ttk.Frame(dialog, padding="20")
        content_frame.pack(fill=tk.BOTH, expand=True)

        # Amount label and entry
        amount_label = ttk.Label(
            content_frame,
            text="Enter amount in Birr:",
            font=("Helvetica", 10)
        )
        amount_label.pack(pady=(0, 5))

        amount_var = tk.StringVar()
        amount_entry = ttk.Entry(
            content_frame,
            textvariable=amount_var,
            width=20
        )
        amount_entry.pack(pady=(0, 10))
        amount_entry.focus()  # Set focus to entry

        def add_amount():
            try:
                amount = float(amount_var.get())
                if amount > 0:
                    self.wallet_balance += amount
                    self.wallet_label.config(text=f"Balance: {self.format_currency(self.wallet_balance)} Birr")
                    dialog.destroy()
                    messagebox.showinfo("Success", f"{self.format_currency(amount)} Birr added to wallet successfully!")
                    # Enable start button if balance is added
                    if self.wallet_balance > 0:
                        self.start_button.config(state=tk.NORMAL)
                else:
                    messagebox.showerror("Error", "Please enter a positive amount")
            except ValueError:
                messagebox.showerror("Error", "Please enter a valid number")

        # Add button
        add_button = ttk.Button(
            content_frame,
            text="Add",
            command=add_amount,
            bootstyle="success",
            width=10
        )
        add_button.pack(pady=5)

        # Bind Enter key to add_amount function
        dialog.bind('<Return>', lambda e: add_amount())

        # Update dialog size to fit content
        dialog.update_idletasks()
        
        # Get the required height
        required_height = content_frame.winfo_reqheight() + 40  # Add some padding
        
        # Set the final size and position
        width = 300
        height = required_height
        x = (dialog.winfo_screenwidth() // 2) - (width // 2)
        y = (dialog.winfo_screenheight() // 2) - (height // 2)
        dialog.geometry(f"{width}x{height}+{x}+{y}")

        # Make dialog modal
        dialog.focus_set()
        dialog.wait_window()

def main():
    root = ttk.Window(themename="lumen")  # Using lumen theme
    app = BingoCaller(root)
    root.mainloop()

if __name__ == "__main__":
    main()