from customtkinter import CTk, CTkFrame, CTkLabel, CTkImage, CTkTextbox, CTkButton
from PIL import Image
import os
import requests
from datetime import datetime
from tkinter import messagebox
import csv
from typing import Optional


appdata = os.getenv('APPDATA')
quilla_folder = os.path.join(appdata, ".Quilla")

LOGIN_PATH = os.path.join(quilla_folder, "login_data.csv")
SIGN_PATH = os.path.join(quilla_folder, "signup_data.csv")

BASE_URL = "http://127.0.0.1:8000"
class FeedbackForm:
    """Feedback form window with responsive background image."""
    
    # Constants
    WINDOW_WIDTH = 1340
    WINDOW_HEIGHT = 730
    IMAGE_SCALE = 0.8
    RESIZE_DEBOUNCE_MS = 100
    MIN_WINDOW_SIZE = 100
    PLACEHOLDER_TEXT = (
        "✨ Share your thoughts with us...\n\n"
        "What did you love? What could be better?\n"
        "Your feedback helps us grow! 🌱\n\n"
        "Type your message here..."
    )
    
    def __init__(self, window):

        self.container = window
        self.bg_label: Optional[CTkLabel] = None
        self.bg_image_path = os.path.join('assets', 'images', 'feedback.png')
        self.original_image: Optional[Image.Image] = None
        self.resize_job: Optional[str] = None
        self.textbox: Optional[CTkTextbox] = None
        self.submit_button: Optional[CTkButton] = None
        self.placeholder_active = True
        self.is_submitting = False  # Prevent double submissions
        
        self.root_window = self._get_root_window()
        self._load_image()
    
    def _get_root_window(self):
        """Get the root Tk window from the container frame."""
        widget = self.container
        while widget.master is not None:
            widget = widget.master
        return widget
    
    def _load_image(self):
        """Load the background image with error handling."""
        try:
            if not os.path.exists(self.bg_image_path):
                raise FileNotFoundError(f"Image not found: {self.bg_image_path}")
            self.original_image = Image.open(self.bg_image_path)
        except Exception as e:
            print(f"Error loading image: {e}")
            self.original_image = Image.new('RGB', (800, 600), color='lightgray')
    
    def gui(self):
        """Initialize and display the GUI."""
    
        for widget in self.container.winfo_children():
            widget.destroy()
        
        element_window = CTkFrame(
            master=self.container,
            fg_color="white",
            corner_radius=10
        )
        element_window.place(relx=0, rely=0, relwidth=1, relheight=1)
        
        self.bg_label = CTkLabel(
            master=element_window,
            text="",
            corner_radius=10
        )
        self.bg_label.place(relx=0.5, rely=0.5, anchor="center")
        
        self.container.update_idletasks()
        initial_width = self.container.winfo_width()
        initial_height = self.container.winfo_height()
        
        if initial_width > 1 and initial_height > 1:
            self.update_background(initial_width, initial_height)
        else:
            self.update_background(1090, 730)
        
        self.root_window.bind("<Configure>", self.on_resize, add="+")

        form_frame = CTkFrame(
            master=element_window,
            fg_color="white",
            width=400,
            height=500,
            corner_radius=10
        )
        form_frame.place(relx=0.75, rely=0.5, anchor="center")
        form_frame.pack_propagate(False)

        self.textbox = CTkTextbox(
            master=form_frame,
            width=300,
            height=350,
            fg_color="#f0f0f0",
            text_color="gray"
        )
        self.textbox.place(relx=0.5, rely=0.42, anchor="center")
        self.textbox.insert("1.0", self.PLACEHOLDER_TEXT)
        self.textbox.bind("<FocusIn>", self._clear_placeholder)
        self.textbox.bind("<FocusOut>", self._restore_placeholder)
        
        self.submit_button = CTkButton(
            master=form_frame,
            text="Send Message",
            width=200,
            height=40,
            corner_radius=0,
            font=("Arial", 16),
            text_color="white",
            fg_color="black",
            hover_color="#4b4b4b",
            command=self.th_submit_feedback
        )
        self.submit_button.place(relx=0.85, rely=0.9, anchor="center")
    
    def _clear_placeholder(self, event):
        """Clear placeholder text when textbox is clicked."""
        if self.placeholder_active:
            self.textbox.delete("1.0", "end")
            self.textbox.configure(text_color="black")
            self.placeholder_active = False
    
    def _restore_placeholder(self, event):
        """Restore placeholder if textbox is empty."""
        if not self.textbox.get("1.0", "end-1c").strip():
            self.textbox.insert("1.0", self.PLACEHOLDER_TEXT)
            self.textbox.configure(text_color="gray")
            self.placeholder_active = True
    
    def th_submit_feedback(self):
        """Submit feedback in a separate thread to prevent UI blocking."""
        if self.is_submitting:
            return  # Prevent double submission
        
        import threading
        th = threading.Thread(target=self.submit_feedback, daemon=True)
        th.start()

    def _get_user_data(self):
        """Read user data from CSV file."""
        file_path = None
        if os.path.exists(LOGIN_PATH):
            file_path = LOGIN_PATH
        elif os.path.exists(SIGN_PATH):
            file_path = SIGN_PATH
        else:
            return None, None
        
        try:
            with open(file_path, 'r', newline='', encoding='utf-8') as file:
                reader = csv.DictReader(file)
                for row in reader:
                    # Return first row (assumes single user)
                    return row.get('username', ''), row.get('email', '')
        except Exception as e:
            print(f"Error reading user data: {e}")
            return None, None
        
        return None, None

    def submit_feedback(self):
        """Submit the feedback content."""
        if self.is_submitting:
            return
        
        self.is_submitting = True
        content = self.textbox.get("1.0", "end-1c")
        
        if self.placeholder_active or not content.strip():
            messagebox.showwarning(
                title="Empty Feedback",
                message="Please enter your feedback before submitting."
            )
            self.is_submitting = False
            return
        
        self.submit_button.configure(text='Submitting...', state='disabled')
        
        name, email = self._get_user_data()
        
        if not name or not email:
            messagebox.showinfo(
                title="No User Data",
                message="Please login first to submit feedback."
            )
            self.submit_button.configure(text='Send Message', state='normal')
            self.is_submitting = False
            return
        
        date_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        """{
            "name": "string",
            "timestamp": "2025-10-10T16:48:52.667Z",
            "email": "user@example.com",
            "feedback": "string"
            }"""
        
        
        payload = {
            'name': name,
            'timestamp': date_time,
            'email': email,
            'feedback': content
        }

        try:
            response = requests.post(
                url=BASE_URL + "/feedback",
                json=payload,
                timeout=10,
                verify=True
            )
            response.raise_for_status()
            
            if response.status_code == 200:
                messagebox.showinfo(
                    title="Thank You!",
                    message="Your feedback has been submitted successfully."
                )
                # Reset textbox
                self.textbox.delete("1.0", "end")
                self.textbox.insert("1.0", self.PLACEHOLDER_TEXT)
                self.textbox.configure(text_color="gray")
                self.placeholder_active = True
                
        except requests.exceptions.Timeout:
            messagebox.showerror(
                title="Submission Failed",
                message="Request timed out. Please check your connection and try again."
            )
        except requests.exceptions.RequestException as e:
            messagebox.showerror(
                title="Submission Failed",
                message=f"Error submitting feedback: {str(e)}"
            )
        finally:
            self.submit_button.configure(text='Send Message', state='normal')
            self.is_submitting = False
    
    def update_background(self, new_width, new_height):
        """Resize and update background image."""
        if self.original_image is None or self.bg_label is None:
            return
        
        img_w = int(new_width * self.IMAGE_SCALE)
        img_h = int(new_height * self.IMAGE_SCALE)
        
        if img_w <= 0 or img_h <= 0:
            return
        
        try:
            resized_image = self.original_image.resize(
                (img_w, img_h),
                Image.LANCZOS
            )
            ctk_img = CTkImage(
                light_image=resized_image,
                dark_image=resized_image,
                size=(img_w, img_h)
            )
            
            self.bg_label.configure(image=ctk_img)
            self.bg_label.image = ctk_img
        except Exception as e:
            print(f"Error updating background: {e}")
    
    def on_resize(self, event):
        """Handle window resize events with debouncing."""
        if event.widget != self.root_window:
            return
        
        if event.width <= self.MIN_WINDOW_SIZE or event.height <= self.MIN_WINDOW_SIZE:
            return
        
        if self.resize_job:
            self.root_window.after_cancel(self.resize_job)
        
        self.container.update_idletasks()
        container_width = self.container.winfo_width()
        container_height = self.container.winfo_height()
        
        self.resize_job = self.root_window.after(
            self.RESIZE_DEBOUNCE_MS,
            lambda: self.update_background(container_width, container_height)
        )
    
    def cleanup(self):
        """Clean up resources when closing."""
        if self.resize_job:
            self.root_window.after_cancel(self.resize_job)
        if self.original_image:
            self.original_image.close()


 #Example usage (uncomment to test)
def main():
    window = CTk()
    window.geometry(f"{FeedbackForm.WINDOW_WIDTH}x{FeedbackForm.WINDOW_HEIGHT}")
    app = FeedbackForm(window)
    app.gui()
    window.mainloop()
if __name__ == "__main__":
    main()