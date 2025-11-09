from customtkinter import CTk, CTkToplevel, CTkFrame, CTkLabel, CTkImage, CTkEntry, CTkButton
from PIL import Image
import os, csv, requests, json
from threading import Thread, Lock
from signup.sign_up import SignUp
from datetime import datetime, date
import webbrowser
from tkinter import messagebox
import threading
import time

# ============================================================================
# CONFIGURATION
# ============================================================================

appdata = os.getenv('APPDATA')
quilla_folder = os.path.join(appdata, ".Quilla")

LOGIN_PATH = os.path.join(quilla_folder, "login_data.csv")
SIGN_PATH = os.path.join(quilla_folder, "signup_data.csv")
KEY_PATH = os.path.join(quilla_folder, 'qa.key')

#BASE_URL = "http://127.0.0.1:8000"
BASE_URL = "http://api.draftzero.in"
PAYMENT_API_URL = "http://localhost:5000"
INTERNAL_PATH = os.path.join(os.getcwd(), "assets")

# Plan configurations
PLANS = [
    {
        "name": "Free Trial",
        "price": "₹0",
        "duration": "15 Days | 25 Drafts",
        "credits": "25 Credits",
        "desc": "Perfect for new users to explore DraftZero.\nGenerate up to 25 drafts and\ntest all features for 15 days\n— no credit card required.",
        "color": "#F9E3E3",
        "inr": 0
    },
    {
        "name": "Essential Plan",
        "price": "₹99",
        "duration": "1 Month | 60 Drafts",
        "credits": "50 Credits",
        "desc": "Perfect for small creators and\nstartups. Includes 60 draft\ngenerations and email support.",
        "color": "#FCE7C8",
        "inr": 99
    },
    {
        "name": "Premium Plan",
        "price": "₹199",
        "duration": "1 Month | 150 Drafts",
        "credits": "150 Credits",
        "desc": "For professionals and teams.\nGet priority processing and\nSEO suggestions.",
        "color": "#E8EAF6",
        "inr": 199
    },
    {
        "name": "Unlimited Plan",
        "price": "₹399",
        "duration": "1 Month | Unlimited Drafts",
        "credits": "Unlimited Credits",
        "desc": "For agencies with high-volume\nneeds. Unlimited drafts &\n24/7 priority support.",
        "color": "#E6F7E9",
        "inr": 399
    }
]


# ============================================================================
# MAIN USER PROFILE CLASS
# ============================================================================

class UserProfile:
    def __init__(self, window):
        self.window = window
        self.profile_pth = os.path.join(INTERNAL_PATH, 'icons', 'profile.png')
        self.api_url = PAYMENT_API_URL
        self.current_order_id = None
        self.buy_buttons = {}
        
        # Thread synchronization
        self.status_lock = Lock()
        self.activation_checked = False
        self.current_activation_id = None
        self.subscription_status = None  # Store current status
        
        # Ensure quilla folder exists
        os.makedirs(quilla_folder, exist_ok=True)

    # ========================================================================
    # UI HELPER METHODS
    # ========================================================================

    def load_img(self, path, width, height):
        """Load and return a CTkImage from path."""
        try:
            img = Image.open(path)
            return CTkImage(dark_image=img, light_image=img, size=(width, height))
        except Exception as e:
            print(f"Error loading image {path}: {e}")
            return None

    def gui(self):
        """Initialize main GUI layout."""
        self.element_window = CTkFrame(master=self.window, fg_color="white")
        self.element_window.grid(column=1, row=0, sticky="nsew")

        self.window.grid_columnconfigure(0, weight=0)
        self.window.grid_columnconfigure(1, weight=1)
        self.window.grid_rowconfigure(0, weight=1)

        # --- User Info Frame ---
        self.create_user_info_frame()
        
        # Check if user is logged in and show appropriate plans
        if self.is_user_logged_in():
            self.show_signed_up_plans()
        else:
            self.show_guest_plans()
        
        # Start background thread for status monitoring
        Thread(target=self.monitor_user_status, daemon=True).start()

    def create_user_info_frame(self):
        """Create user information and activation frame."""
        self.sub_id_frame = CTkFrame(
            master=self.element_window, 
            fg_color="#F1F2F5", 
            corner_radius=25
        )
        self.sub_id_frame.place(relx=0.08, rely=0.05, relwidth=0.85, relheight=0.15)

        # Profile image
        profile_img = self.load_img(self.profile_pth, width=50, height=50)
        if profile_img:
            CTkLabel(
                master=self.sub_id_frame, 
                image=profile_img, 
                text=""
            ).place(relx=-0.2, rely=0.25, relwidth=0.50, relheight=0.50)

        # Username label
        self.username = CTkLabel(
            master=self.sub_id_frame, 
            text="Guest User", 
            font=("", 20, 'bold'), 
            text_color="black"
        )
        self.username.place(relx=0.09, rely=0.17)

        # Subscription status label
        self.valid_until = CTkLabel(
            master=self.sub_id_frame, 
            text="Free Trial", 
            font=("", 15), 
            text_color="#a1a0a0"
        )
        self.valid_until.place(relx=0.09, rely=0.5)

        # Activation frame
        activation_frame = CTkFrame(master=self.sub_id_frame, corner_radius=15)
        activation_frame.place(relx=0.35, rely=0.20, relwidth=0.55, relheight=0.55)

        self.key_id = CTkEntry(
            master=activation_frame, 
            placeholder_text="Enter your Product key", 
            corner_radius=10
        )
        self.key_id.place(relx=0.08, rely=0.2, relwidth=0.55, relheight=0.65)

        CTkButton(
            master=activation_frame, 
            text="Activate", 
            fg_color="black", 
            hover_color="#4C4C4D", 
            font=("", 14),
            command=self.th_activate_user
        ).place(relx=0.7, rely=0.2, relwidth=0.2, relheight=0.65)

    # ========================================================================
    # PLAN DISPLAY METHODS
    # ========================================================================

    def show_signed_up_plans(self):
        """Display plans for logged-in users (with buy buttons)."""
        self._render_plans(show_signup=False, show_buy=True)

    def show_guest_plans(self):
        """Display plans for guests (with signup buttons)."""
        self._render_plans(show_signup=True, show_buy=False)

    def _render_plans(self, show_signup=False, show_buy=False):
        """Render plan cards dynamically."""
        base_x = 0.05
        self.buy_buttons.clear()
        
        for i, plan in enumerate(PLANS):
            frame = CTkFrame(master=self.element_window, fg_color=plan["color"], corner_radius=25)
            frame.place(relx=base_x + (i * 0.23), rely=0.3, relwidth=0.2, relheight=0.60)

            # Container for padding
            container = CTkFrame(master=frame, fg_color="transparent")
            container.pack(expand=True, fill="both", padx=10, pady=10)

            # Plan details
            CTkLabel(container, text=plan["name"], font=("", 25, "bold")).pack(pady=(5, 5))

            CTkLabel(container, text=plan["price"], font=("", 45, "bold")).pack(pady=(5, 5))

            CTkLabel(container, text=plan["credits"], font=("", 18, "bold"), text_color="#2E2E2E").pack(pady=(5, 5))

            CTkLabel(container, text=plan["duration"], font=("", 16)).pack(pady=(5, 5))

            CTkLabel(container, text=plan["desc"], font=("", 14), justify="left", wraplength=150).pack(pady=(5, 5))

            # Buttons based on user status
            if show_signup:
                CTkButton(master=frame, text="Sign Up", text_color="white", font=('', 16),command=self.open_signup,fg_color="black", hover_color="#4C4C4D").place(relx=0.15, rely=0.82, relwidth=0.7, relheight=0.1)

            elif show_buy and plan["name"] != "Free Trial":
                buy_btn = CTkButton(master=frame, text="Buy Credits", text_color="black",fg_color="white", border_width=1, border_color="black",command=lambda price=plan["inr"]: self.buy_more_credits(price),font=('', 14), hover_color="#f2f2f2")
                buy_btn.place(relx=0.15, rely=0.75, relwidth=0.7, relheight=0.08)
                self.buy_buttons[plan["name"]] = buy_btn

    # ========================================================================
    # PAYMENT METHODS
    # ========================================================================

    def buy_more_credits(self, price):
        """Initiate payment process for buying credits."""
        # Disable all buy buttons
        for btn in self.buy_buttons.values():
            btn.configure(state='disabled', text='Please Wait...')
        
        print(f"Initiating payment for ₹{price}")
        Thread(target=self.initiate_payment, args=(price,), daemon=True).start()

    def initiate_payment(self, amount):
        """Create payment order and open browser."""
        try:
            if amount <= 0:
                self.show_error("Please select a valid plan")
                self._reset_buy_buttons()
                return
            
            # Get user details
            user_data = self.get_user_data()
            if not user_data:
                self.show_error("User data not found. Please login again.")
                self._reset_buy_buttons()
                return

            email = user_data.get('email', 'customer@example.com')
            phone = user_data.get('mobile', '9999999999')
            
            print(f"Payment email: {email}, phone: {phone}")
            
            # Create order via API
            response = requests.post(
                f"{self.api_url}/create-order", 
                json={'amount': amount, 'email': email},
                timeout=10
            )
            
            if response.status_code == 200:
                data = response.json()
                self.current_order_id = data['order_id']
                payment_url = data['payment_url']
                
                print(f"Order created: {self.current_order_id}")
                
                # Open payment page in browser
                webbrowser.open(payment_url)
                
                # Start polling for payment status
                Thread(target=self.poll_payment_status, daemon=True).start()
            else:
                error_msg = response.json().get('message', 'Failed to create order')
                print(f"Error:{error_msg}\n")
                #self.show_error(error_msg)
                self._reset_buy_buttons()
                
        except requests.RequestException as e:
            print(f"Payment initiation error: {e}")
            self.show_error("Unable to connect to payment server")
            self._reset_buy_buttons()
        except Exception as e:
            print(f"Unexpected error: {e}")
            self.show_error(f"Error: {str(e)}")
            self._reset_buy_buttons()

    def poll_payment_status(self):
        """Poll server for payment status updates."""
        max_attempts = 60  # 5 minutes
        attempt = 0
        
        while attempt < max_attempts and self.current_order_id:
            try:
                response = requests.get(
                    f"{self.api_url}/payment-status/{self.current_order_id}",
                    timeout=5
                )
                
                if response.status_code == 200:
                    data = response.json()
                    payment = data.get('payment', {})
                    status = payment.get('status')
                    
                    if status == 'success':
                        print("✓ Payment successful!")
                        print(f"Payment Data: {payment}")
                        
                        # Check for license
                        licence_uuid = payment.get('licence_uuid')
                        if licence_uuid:
                            print(f"License UUID: {licence_uuid}")
                            self._save_activation_key(licence_uuid)
                            
                            # Reset activation check to force refresh
                            with self.status_lock:
                                self.activation_checked = False
                                self.current_activation_id = licence_uuid
                            
                            self.window.after(0, lambda: self.key_id.delete(0, 'end'))
                            self.window.after(0, lambda: self.key_id.insert(0, licence_uuid))
                        
                        self.window.after(0, lambda: messagebox.showinfo(
                            "Success", 
                            "Payment completed successfully!\nYour license has been added."
                        ))
                        self._reset_buy_buttons()
                        break
                        
                    elif status == 'failed':
                        print("✗ Payment failed!")
                        self.window.after(0, lambda: messagebox.showerror(
                            "Failed", 
                            "Payment failed. Please try again."
                        ))
                        self._reset_buy_buttons()
                        break
                        
            except Exception as e:
                print(f"Polling error: {e}")
            
            time.sleep(5)  # Poll every 5 seconds
            attempt += 1
        
        # Timeout
        if attempt >= max_attempts:
            print("Payment polling timeout")
            self._reset_buy_buttons()

    def _reset_buy_buttons(self):
        """Reset all buy buttons to normal state."""
        for btn in self.buy_buttons.values():
            self.window.after(0, lambda b=btn: b.configure(state='normal', text='Buy Credits'))

    def _save_activation_key(self, key):
        """Save activation key to file."""
        try:
            with open(KEY_PATH, 'w') as f:
                f.write(key)
            print(f"Activation key saved: {key}")
        except Exception as e:
            print(f"Error saving activation key: {e}")

    # ========================================================================
    # USER DATA METHODS
    # ========================================================================

    def is_user_logged_in(self):
        """Check if user is logged in."""
        return os.path.exists(LOGIN_PATH) or os.path.exists(SIGN_PATH)

    def get_user_data(self):
        """Retrieve user data from CSV file."""
        if not self.is_user_logged_in():
            return None
        
        file_path = LOGIN_PATH if os.path.exists(LOGIN_PATH) else SIGN_PATH
        
        try:
            with open(file_path, 'r', newline='', encoding='utf-8') as file:
                reader = csv.DictReader(file)
                for row in reader:
                    return row
        except Exception as e:
            print(f"Error reading user data: {e}")
            return None

    def update_subscription_display(self, status_text):
        """Thread-safe method to update subscription status display."""
        with self.status_lock:
            if self.subscription_status != status_text:
                self.subscription_status = status_text
                self.window.after(0, lambda: self.valid_until.configure(text=status_text))
                print(f"Status updated: {status_text}")

    # ========================================================================
    # ACTIVATION METHODS
    # ========================================================================

    def th_activate_user(self):
        """Thread wrapper for activation."""
        Thread(target=self.activate_user, daemon=True).start()

    def activate_user(self):
        """Activate user with product key."""
        key = self.key_id.get().strip()
        
        if not key:
            self.show_error("Please enter an activation key")
            return
        
        try:
            # Check activation details
            response = requests.get(
                f'{BASE_URL}/activation_details/{key}',
                verify=False,
                timeout=10
            )
            
            if response.status_code != 200:
                self.show_error("Invalid activation key")
                return
            
            res_data = response.json()
            
            if res_data.get('already_active') == True:
                self.show_info("Already Activated", "This key is already in use.")
                return
            
            # Activate key
            activate_response = requests.post(
                f"{BASE_URL}/activate",
                json={'uuid': key},
                timeout=10
            )
            
            activate_data = activate_response.json()
            status = activate_data.get('status')
            
            if status == "success":
                self._save_activation_key(key)
                
                # Reset activation check
                with self.status_lock:
                    self.activation_checked = False
                    self.current_activation_id = key
                
                self.show_info(
                    "Success", 
                    "Your product is now activated!\nPlease restart the application."
                )
            elif status == 'used':
                self.show_info("Used", "This activation key has already been used.")
            else:
                self.show_error("Activation failed. UUID not found.")
                
        except requests.RequestException as e:
            print(f"Activation error: {e}")
            self.show_error("Unable to connect to activation server")
        except Exception as e:
            print(f"Unexpected activation error: {e}")
            self.show_error(f"Error: {str(e)}")

    def fetch_activation_details(self, activation_id):
        """Fetch and display activation details. Returns True if successful."""
        try:
            response = requests.get(
                f'{BASE_URL}/activation_details/{activation_id.strip()}',
                verify=False,
                timeout=10
            )
            
            if response.status_code == 200:
                res_data = response.json()
                if res_data.get('status') == "success":
                    expiry_date = res_data.get("expiry_date")
                    days = self.days_left(expiry_date)
                    
                    # Update display
                    status_text = f'Subscription: {days} days remaining'
                    self.update_subscription_display(status_text)
                    
                    print(f"Activation valid — {days} days remaining")
                    return True
                else:
                    print("Activation ID not found on server")
                    return False
            else:
                print(f"Request failed: {response.status_code}")
                return False
                
        except Exception as e:
            print(f"Error fetching activation details: {e}")
            return False

    # ========================================================================
    # UNIFIED MONITORING THREAD
    # ========================================================================

    def monitor_user_status(self):
        """Single unified thread to monitor user and activation status."""
        while True:
            try:
                if not self.is_user_logged_in():
                    time.sleep(2)
                    continue
                
                # Get user data
                user_data = self.get_user_data()
                if not user_data:
                    time.sleep(2)
                    continue
                
                # Update username
                username = user_data.get('username', 'Guest User')
                self.window.after(0, lambda u=username: self.username.configure(text=u))
                
                # Check for activation key
                if os.path.exists(KEY_PATH):
                    with open(KEY_PATH, 'r') as f:
                        activation_id = f.readline().strip()
                    
                    # Only check if not already checked or if it's a new key
                    with self.status_lock:
                        should_check = (
                            not self.activation_checked or 
                            self.current_activation_id != activation_id
                        )
                    
                    if should_check and activation_id:
                        print(f"Checking activation: {activation_id}")
                        success = self.fetch_activation_details(activation_id)
                        
                        with self.status_lock:
                            if success:
                                self.activation_checked = True
                                self.current_activation_id = activation_id
                    
                    # If already checked, just sleep longer
                    if self.activation_checked:
                        time.sleep(300)  # Check every 5 minutes
                    else:
                        time.sleep(10)  # Retry more frequently if failed
                
                else:
                    # No activation key - show free trial status
                    end_date = user_data.get('free_trial_end', '')
                    if end_date:
                        days = self.days_left(end_date)
                        if days == 0:
                            status_text = "Free Trial Ended"
                        else:
                            status_text = f"Free Trial: {days} days left"
                        
                        self.update_subscription_display(status_text)
                    
                    time.sleep(5)  # Check for activation key more frequently
                    
            except Exception as e:
                print(f"Monitor error: {e}")
                time.sleep(5)

    # ========================================================================
    # UTILITY METHODS
    # ========================================================================

    def days_left(self, end_date_str):
        """Calculate days left from today until end_date."""
        try:
            end_date = datetime.strptime(end_date_str[:10], "%Y-%m-%d").date()
            today = date.today()
            delta = (end_date - today).days
            return max(delta, 0)
        except Exception as e:
            print(f"Error calculating days left: {e}")
            return 0

    def open_signup(self):
        """Open signup window."""
        try:
            signup_window = CTkToplevel(self.window)
            SignUp(signup_window).gui()
        except Exception as e:
            print(f"Error opening signup: {e}")
            self.show_error("Unable to open signup window")

    def show_error(self, message):
        """Show error message."""
        self.window.after(0, lambda: messagebox.showerror("Error", message))

    def show_info(self, title, message):
        """Show info message."""
        self.window.after(0, lambda: messagebox.showinfo(title, message))


# ============================================================================
# MAIN APPLICATION
# ============================================================================

def main():
    """Initialize and run the application."""
    window = CTk()
    
    # Window configuration
    width, height = 1340, 730
    screen_width = window.winfo_screenwidth()
    screen_height = window.winfo_screenheight()
    position_top = int((screen_height / 2) - (height / 2))
    position_right = int((screen_width / 2) - (width / 2))
    
    window.geometry(f'{width}x{height}+{position_right}+{position_top}')
    window.title("DraftZero - Subscription Plans")
    
    # Initialize app
    app = UserProfile(window)
    app.gui()
    
    window.mainloop()


if __name__ == "__main__":
    main()