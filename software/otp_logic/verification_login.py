from customtkinter import CTk, CTkFrame, CTkButton, CTkLabel, CTkEntry, CTkImage, set_appearance_mode
from tkinter import messagebox
from threading import Thread
from PIL import Image
import requests, os, csv,json
from datetime import datetime,date

from serverId import quilla_Server
set_appearance_mode('light')

URL = quilla_Server()

class VerifyScreen:
    appdata_path = os.getenv('APPDATA')

    def __init__(self, main, email,username,plan_details,loginbtn ):
        self.window = main
        self.email_id = email.strip()
        self.username= username
        self.plan_details = plan_details
        self.loginbtn = loginbtn
     
        print(f'Email: {self.email_id}\n')

        # Preload image
        lady_img_path = os.path.join(os.getcwd(), "assets", "images", "email.png")
        img = Image.open(lady_img_path)
        self.lady_img_tk = CTkImage(dark_image=img, light_image=img, size=(510, 600))

    # ------------------------ Network ------------------------
    def netcheck(self):
        try:
            re = requests.get('https://www.google.com', timeout=10)
            if re.status_code == 200:
                return True
            else:
                messagebox.showerror("Connection Error", "Please check your internet connection",parent=self.window)
                return False
        except Exception as e:
            messagebox.showerror("Connection Error", f"Network check failed:\n{str(e)}",parent=self.window)
            return False

    def send_otp(self):
        if not self.netcheck():
            return
        data = {"email": self.email_id}
        try:
            re = requests.post(url=f"{URL}/send-otp", json=data, timeout=10)
            if re.status_code == 200:
                messagebox.showinfo("OTP Sent", "Kindly check your email!",parent=self.window)
            else:
                messagebox.showerror("Server Error", "Please try again later.",parent=self.window)
        except Exception as e:
            messagebox.showerror("Network Error", str(e),parent=self.window)

    def th_send_otp(self):
        Thread(target=self.send_otp, daemon=True).start()

    # ------------------------ Signup ------------------------
    def signup(self):
        email_val = self.email_id.strip()

        data = {"email": email_val,"mobile":"1236547890"}
        res = requests.post(url=f"{URL}/login", json=data, timeout=10)
        if res.status_code == 200:
            response_data = res.json()  # your JSON like {"sl": 0, "username": "...", ...}
            print(f"login contain: {response_data}")
            #messagebox.showinfo("Success", "Account created successfully!")
            # === Store data in CSV ===
            appdata = os.getenv('APPDATA')
            quilla_folder= os.path.join(appdata,'.Quilla')
            csv_file = os.path.join(quilla_folder,"login_data.csv")
            file_exists = os.path.isfile(csv_file)
            with open(csv_file, mode="w", newline="", encoding="utf-8") as file:
                writer = csv.writer(file)
                writer.writerow([
                        "sl", "username", "email", "mobile",
                        "free_trial_active", "free_trial_start", "free_trial_end", "stored_at"
                    ])
                writer.writerow([
                    response_data.get("sl"),
                    response_data.get("username"),
                    response_data.get("email"),
                    response_data.get("mobile"),
                    response_data.get("free_trial_active"),
                    response_data.get("free_trial_start"),
                    response_data.get("free_trial_end"),
                    datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                ])
            print("User data stored successfully in login_data.csv")
            expiry = response_data.get("free_trial_end")
            username = response_data.get("username")

            days = self.days_left(expiry)
            print(f"days: {days}\n")
            print(username)
            self.username.configure(text=username)
            print("username ...")
            self.loginbtn.destroy()
            print("login destroy....")
            if days==0:
                self.plan_details.configure(text="Free Trail End")
            else: 
                self.plan_details.configure(text=f"Free Trial: {days} days left")
            
            self.window.destroy()
        else:
            messagebox.showwarning("login Failed", "Unable to create account.",parent=self.window)
            print("Response:", res.text)

       

    def days_left(self, end_date_str):
        """Calculate days left from today until end_date."""
        try:
            end_date = datetime.strptime(end_date_str[:10], "%Y-%m-%d").date()
            today = date.today()
            delta = (end_date - today).days
            return max(delta, 0)
        except Exception as e:
            print(f"Error calculating days left: {e}")
            return None
    # ------------------------ OTP Verification ------------------------
    def on_otp_key(self, event, index):
        key = event.char
        if key.isdigit():
            self.otp_entries[index].delete(0, "end")
            self.otp_entries[index].insert(0, key)
            if index < 5:
                self.otp_entries[index + 1].focus()
        elif event.keysym in ("BackSpace", "Delete"):
            if self.otp_entries[index].get() == "" and index > 0:
                self.otp_entries[index - 1].focus()
        else:
            self.otp_entries[index].delete(0, "end")

    def verify_otp(self):
        otp = "".join(entry.get() for entry in self.otp_entries)
        if len(otp) != 6 or not otp.isdigit():
            messagebox.showwarning("Invalid OTP", "Please enter your 6-digit OTP",parent=self.window)
            return

        # Disable entries and button while verifying
        for e in self.otp_entries:
            e.configure(state='disabled')
        self.verify_button.configure(state='disabled', text="Verifying...")

        def verify_thread():
            try:
                data = {"email": self.email_id, "otp": otp}
                print(f"Verification: {self.email_id}\t{otp}\n")
                re = requests.post(url=f"{URL}/verify-otp", json=data, timeout=10)
                if re.status_code == 200:
                    print("Verification Successful!")
                    self.signup()
                else:
                    messagebox.showerror("Invalid OTP", "Enter your OTP wisely",parent=self.window)
            except Exception as e:
                #messagebox.showerror("Network Error", str(e),parent=self.window)
                print(e)
            finally:
                for e in self.otp_entries:
                    e.configure(state='normal')
                self.verify_button.configure(state='normal', text="Verify your account")

        Thread(target=verify_thread, daemon=True).start()

    # ------------------------ GUI ------------------------
    def gui(self):
        
        for widget in self.window.winfo_children():
            widget.destroy()

        self.element_window = CTkFrame(master=self.window, width=1020, height=600, fg_color="white")
        self.element_window.place(relx=0, rely=0)

        # Right frame (image)
        right_frame = CTkFrame(master=self.element_window, width=510, height=600, fg_color="white", corner_radius=0)
        right_frame.place(relx=0.5, rely=0)

        # Left frame (OTP & info)
        left_frame = CTkFrame(master=self.element_window, width=510, height=400, fg_color="white", corner_radius=0)
        left_frame.place(relx=0, rely=0)

        # Centered content frame
        content_frame = CTkFrame(master=left_frame, fg_color="transparent", corner_radius=0)
        content_frame.place(relx=0.5, rely=0.5, anchor="center")

        # Title
        CTkLabel(content_frame, text="Confirm Your Email", font=("", 18, "bold"), text_color="black").pack(anchor="center")
        self.email_info = CTkLabel(content_frame, text=f"We sent a code to {self.email_id}", font=("", 12), wraplength=400, justify="center", text_color="#969696")
        self.email_info.pack(anchor="center", pady=(5, 15))

        # OTP Entries
        otp_frame = CTkFrame(master=content_frame, fg_color="transparent", corner_radius=0)
        otp_frame.pack(anchor="center", pady=(10, 20))

        self.otp_entries = []
        for i in range(6):
            entry = CTkEntry(master=otp_frame, width=45, height=50, font=("Arial", 20), corner_radius=8, justify="center")
            entry.pack(side="left", padx=6)
            entry.bind("<KeyRelease>", lambda event, idx=i: self.on_otp_key(event, idx))
            self.otp_entries.append(entry)

        # Verify button
        self.verify_button = CTkButton(content_frame, text="Verify your account", width=250, height=45, font=("Arial", 16), corner_radius=10, fg_color="black", text_color="white", hover_color="#4b4b4b", command=self.verify_otp)
        self.verify_button.pack(anchor="center", pady=(15, 0))

        # Resend frame
        resend_frame = CTkFrame(master=self.window, width=510, height=200, fg_color="white", corner_radius=0)
        resend_frame.place(relx=0.0, rely=0.665)
        CTkLabel(resend_frame, text="Didn't get a code?", font=("Arial", 12), text_color="gray").place(relx=0.31, rely=0.5)
        self.resend_button = CTkButton(resend_frame, text="Resend Code", font=("Arial", 12, "bold"), fg_color="transparent", text_color="black", width=10, command=self.th_send_otp)
        self.resend_button.place(relx=0.495, rely=0.5)

        # Image
        CTkLabel(master=right_frame, image=self.lady_img_tk, text="").place(relx=0, rely=0)


'''# ------------------------ Run ------------------------
if __name__ == "__main__":
    window = CTk()
    app = VerifyScreen(main=window, email="amitsarkar@gmail.com", name="Amit Sarkar", mobile="9876543210")
    app.gui()
    window.mainloop()
'''