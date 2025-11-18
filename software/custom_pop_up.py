from customtkinter import CTkToplevel, CTkLabel, CTkEntry, CTkButton, CTkFrame
from tkinter import messagebox


class CustomInputPopup:
    def __init__(self, parent, input_type, callback):
        """
        Create a popup window for custom input
        
        Args:
            parent: Parent window
            input_type: Type of input ("Language", "Tone", or "Platform")
            callback: Function to call with the custom value
        """
        self.callback = callback
        self.input_type = input_type
        self.custom_value = None
        
        # Create toplevel window
        self.popup = CTkToplevel(parent)
        self.popup.title(f"Custom {input_type}")
        self.popup.geometry("400x250")
        self.popup.resizable(False, False)
        
        # Make it modal
        self.popup.transient(parent)
        self.popup.grab_set()
        
        # Center the window
        self.center_window()
        
        # Create UI
        self.create_ui()
        
    def center_window(self):
        """Center the popup window on screen"""
        self.popup.update_idletasks()
        width = self.popup.winfo_width()
        height = self.popup.winfo_height()
        x = (self.popup.winfo_screenwidth() // 2) - (width // 2)
        y = (self.popup.winfo_screenheight() // 2) - (height // 2)
        self.popup.geometry(f'{width}x{height}+{x}+{y}')
        
    def create_ui(self):
        """Create the popup UI elements"""
        # Main frame
        main_frame = CTkFrame(master=self.popup, fg_color="white")
        main_frame.pack(fill="both", expand=True, padx=20, pady=20)
        
        # Title
        title = CTkLabel(
            master=main_frame,
            text=f"Enter Custom {self.input_type}",
            font=("", 20, "bold")
        )
        title.pack(pady=(10, 5))
        
        # Description based on input type
        descriptions = {
            "Language": "Enter the language you want the script to be written in\n(e.g., Spanish, French, German, Tamil)",
            "Tone": "Enter the tone style for your script\n(e.g., Casual, Serious, Educational, Dramatic)",
            "Platform": "Enter the platform or format\n(e.g., TikTok, LinkedIn, Podcast, Twitter)"
        }
        
        description = CTkLabel(
            master=main_frame,
            text=descriptions.get(self.input_type, "Enter your custom value"),
            font=("", 12),
            text_color="#6b6b6b",
            justify="center"
        )
        description.pack(pady=(0, 20))
        
        # Input entry
        self.entry = CTkEntry(
            master=main_frame,
            width=320,
            height=40,
            corner_radius=10,
            placeholder_text=f"Enter custom {self.input_type.lower()}...",
            font=("", 13)
        )
        self.entry.pack(pady=10)
        self.entry.focus()
        
        # Bind Enter key to submit
        self.entry.bind("<Return>", lambda e: self.submit())
        
        # Button frame
        button_frame = CTkFrame(master=main_frame, fg_color="white")
        button_frame.pack(pady=20)
        
        # Cancel button
        cancel_btn = CTkButton(
            master=button_frame,
            text="Cancel",
            font=("", 13, "bold"),
            width=120,
            height=35,
            corner_radius=10,
            fg_color="#e0e0e0",
            text_color="#333333",
            hover_color="#d0d0d0",
            command=self.cancel
        )
        cancel_btn.pack(side="left", padx=5)
        
        # Submit button
        submit_btn = CTkButton(
            master=button_frame,
            text="Apply",
            font=("", 13, "bold"),
            width=120,
            height=35,
            corner_radius=10,
            fg_color="#007bff",
            text_color="white",
            hover_color="#0157b3",
            command=self.submit
        )
        submit_btn.pack(side="left", padx=5)
        
    def submit(self):
        """Handle submit action"""
        value = self.entry.get().strip()
        
        if not value:
            messagebox.showwarning(
                title="Empty Input",
                message=f"Please enter a custom {self.input_type.lower()}."
            )
            return
        
        self.custom_value = value
        self.callback(value)
        self.popup.destroy()
        
    def cancel(self):
        """Handle cancel action"""
        self.custom_value = None
        self.popup.destroy()


# Example usage in your main script:
"""
def handle_custom_language(value):
    print(f"Custom language selected: {value}")
    # Update your UI or store the value
    
# When "Custom" is selected from dropdown:
popup = CustomInputPopup(
    parent=self.window,
    input_type="Language",  # or "Tone" or "Platform"
    callback=handle_custom_language
)
"""