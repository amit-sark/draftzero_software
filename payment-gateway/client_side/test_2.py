import tkinter as tk
from tkinter import ttk, messagebox
import requests
import webbrowser
import time
import threading
import psutil
import platform

class PaymentApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Payment Gateway - DraftZero")
        self.root.geometry("500x400")
        self.root.resizable(False, False)
        
        self.api_url = "http://localhost:5000"
        self.current_order_id = None
        self.browser_process = None
        self.polling_active = False
        
        self.setup_ui()
        
    def setup_ui(self):
        # Main frame
        main_frame = ttk.Frame(self.root, padding="20")
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # Title
        title = ttk.Label(main_frame, text="Razorpay Payment Gateway", 
                         font=("Arial", 18, "bold"))
        title.pack(pady=(0, 20))
        
        # Amount frame
        amount_frame = ttk.LabelFrame(main_frame, text="Payment Details", padding="15")
        amount_frame.pack(fill=tk.BOTH, pady=10)
        
        ttk.Label(amount_frame, text="Amount (₹):", font=("Arial", 12)).grid(
            row=0, column=0, sticky=tk.W, pady=5
        )
        self.amount_var = tk.StringVar(value="100")
        amount_entry = ttk.Entry(amount_frame, textvariable=self.amount_var, 
                                font=("Arial", 12), width=20)
        amount_entry.grid(row=0, column=1, pady=5, padx=10)
        
        ttk.Label(amount_frame, text="Email:", font=("Arial", 12)).grid(
            row=1, column=0, sticky=tk.W, pady=5
        )
        self.email_var = tk.StringVar(value="customer@example.com")
        email_entry = ttk.Entry(amount_frame, textvariable=self.email_var, 
                               font=("Arial", 12), width=20)
        email_entry.grid(row=1, column=1, pady=5, padx=10)
        
        ttk.Label(amount_frame, text="Phone:", font=("Arial", 12)).grid(
            row=2, column=0, sticky=tk.W, pady=5
        )
        self.phone_var = tk.StringVar(value="9999999999")
        phone_entry = ttk.Entry(amount_frame, textvariable=self.phone_var, 
                               font=("Arial", 12), width=20)
        phone_entry.grid(row=2, column=1, pady=5, padx=10)
        
        # Pay button
        self.pay_btn = ttk.Button(main_frame, text="Pay Now", command=self.initiate_payment,
                            style="Accent.TButton")
        self.pay_btn.pack(pady=20)
        
        # Status frame
        status_frame = ttk.LabelFrame(main_frame, text="Payment Status", padding="15")
        status_frame.pack(fill=tk.BOTH, expand=True)
        
        self.status_text = tk.Text(status_frame, height=8, font=("Arial", 10), 
                                   state=tk.DISABLED, wrap=tk.WORD)
        self.status_text.pack(fill=tk.BOTH, expand=True)
        
        # Style
        style = ttk.Style()
        style.configure("Accent.TButton", font=("Arial", 12, "bold"))
        
    def log_status(self, message):
        self.status_text.config(state=tk.NORMAL)
        self.status_text.insert(tk.END, f"{message}\n")
        self.status_text.see(tk.END)
        self.status_text.config(state=tk.DISABLED)
        
    def close_browser_tabs(self):
        """Attempt to close browser tabs/windows"""
        try:
            system = platform.system()
            
            # This is a basic approach - closes all browser windows
            # More sophisticated approaches would require browser-specific extensions
            if system == "Windows":
                # Try to close Chrome/Edge tabs
                for proc in psutil.process_iter(['name']):
                    try:
                        proc_name = proc.info['name'].lower()
                        if 'chrome' in proc_name or 'msedge' in proc_name or 'firefox' in proc_name:
                            # This will close the entire browser
                            # For tab-specific closing, you'd need browser automation
                            pass  # We'll use a gentler approach below
                    except (psutil.NoSuchProcess, psutil.AccessDenied):
                        pass
            
            self.log_status("⚠ Please close the payment browser tab manually")
            
        except Exception as e:
            self.log_status(f"Could not auto-close browser: {str(e)}")
    
    def initiate_payment(self):
        # Prevent multiple simultaneous payments
        if self.polling_active:
            messagebox.showwarning("Payment in Progress", "Please wait for the current payment to complete")
            return
            
        try:
            amount = float(self.amount_var.get())
            if amount <= 0:
                messagebox.showerror("Error", "Please enter a valid amount")
                return
            
            email = self.email_var.get()
            phone = self.phone_var.get()
            
            # Validate email
            if not email or '@' not in email:
                messagebox.showerror("Error", "Please enter a valid email")
                return
            
            self.log_status(f"Initiating payment of ₹{amount}...")
            
            # Disable pay button during processing
            self.pay_btn.config(state=tk.DISABLED)
            
            # Create order
            response = requests.post(f"{self.api_url}/create-order", json={
                'amount': amount,
                'email': email,
                'phone': phone
            })
            
            if response.status_code == 200:
                data = response.json()
                self.current_order_id = data['order_id']
                payment_url = data['payment_url']
                
                self.log_status(f"Order created: {self.current_order_id}")
                self.log_status("Opening payment page in browser...")
                
                # Open payment page in browser
                webbrowser.open(payment_url)
                
                # Start polling for payment status
                self.polling_active = True
                threading.Thread(target=self.poll_payment_status, daemon=True).start()
            else:
                self.log_status(f"Error: {response.json().get('message', 'Unknown error')}")
                messagebox.showerror("Error", "Failed to create order")
                self.pay_btn.config(state=tk.NORMAL)
                
        except ValueError:
            messagebox.showerror("Error", "Please enter a valid amount")
            self.pay_btn.config(state=tk.NORMAL)
        except Exception as e:
            self.log_status(f"Error: {str(e)}")
            messagebox.showerror("Error", str(e))
            self.pay_btn.config(state=tk.NORMAL)
    
    def poll_payment_status(self):
        """Poll the server for payment status updates"""
        max_attempts = 60  # Poll for 5 minutes
        attempt = 0
        order_id = self.current_order_id
        
        while attempt < max_attempts and self.polling_active:
            try:
                response = requests.get(
                    f"{self.api_url}/payment-status/{order_id}"
                )
                
                if response.status_code == 200:
                    data = response.json()
                    payment = data['payment']
                    status = payment['status']
                    
                    if status == 'success':
                        self.log_status("✓ Payment Successful!")
                        print("Payment successful!")
                        print(f"Payment Data: {payment}")
                        
                        # License will be in payment['licence_uuid'] if stored in DB
                        if payment.get('licence_uuid'):
                            print(f"License: {payment['licence_uuid']}")
                            self.log_status(f"License: {payment['licence_uuid']}")
                        
                        # Stop polling
                        self.polling_active = False
                        self.current_order_id = None
                        
                        # Re-enable pay button
                        self.root.after(0, lambda: self.pay_btn.config(state=tk.NORMAL))
                        
                        # Show success message
                        self.root.after(0, lambda: messagebox.showinfo(
                            "Success", 
                            "Payment completed successfully!"
                        ))
                        return
                        
                    elif status == 'failed':
                        self.log_status("✗ Payment Failed")
                        print("Payment failed!")
                        print(f"Payment Data: {payment}")
                        
                        # Stop polling
                        self.polling_active = False
                        self.current_order_id = None
                        
                        # Close browser tab
                        self.close_browser_tabs()
                        
                        # Show retry dialog
                        def show_retry_dialog():
                            retry = messagebox.askretrycancel(
                                "Payment Failed",
                                "Your payment has failed.\n\n"
                                "Please close the payment browser tab and cooperate.\n\n"
                                "Would you like to retry the payment?",
                                icon='error'
                            )
                            
                            if retry:
                                self.log_status("Retrying payment...")
                                self.initiate_payment()
                            else:
                                self.log_status("Payment cancelled by user")
                                self.pay_btn.config(state=tk.NORMAL)
                        
                        self.root.after(0, show_retry_dialog)
                        return
                        
            except Exception as e:
                self.log_status(f"Polling error: {str(e)}")
            
            time.sleep(3)  # Poll every 3 seconds
            attempt += 1
        
        # Timeout or stopped
        if attempt >= max_attempts:
            self.log_status("⚠ Payment status check timed out")
            self.polling_active = False
            self.current_order_id = None
            self.root.after(0, lambda: self.pay_btn.config(state=tk.NORMAL))


if __name__ == "__main__":
    root = tk.Tk()
    app = PaymentApp(root)
    root.mainloop()