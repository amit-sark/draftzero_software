from customtkinter import CTkToplevel, CTkEntry, CTkButton, CTkLabel, CTkFrame, CTkImage
from PIL import Image
import os
import requests
from tkinter import messagebox
import re
from threading import Thread

from otp_logic.verification import VerifyScreen
from serverId import quilla_Server

BASE_URL = quilla_Server()

class SignUp:
    def __init__(self, window,username,plan,loginBtn):
        self.window = window
        
        self.username = username
        self.plan = plan
        self.loginBtn= loginBtn
        


    def login(self):

        from login.login import LoginScreen

        app = LoginScreen(main=self.window,usernname=self.username,plan_details=self.plan,loginbtn=self.loginBtn)
        app.gui()

    # ---------------- Validation ----------------
    def is_valid_email(self, email):
        return re.match(r"[^@]+@[^@]+\.[^@]+", email)

    def is_valid_phone(self, phone):
        return phone.isdigit() and len(phone) == 10

    # ---------------- Network Calls ----------------
    def user_check(self, name, email, phone):
        try:
            data = {"username": name, "email": email, "mobile": phone}
            res = requests.post(url=f"{BASE_URL}/user_check", json=data, timeout=10)

            res_data = res.json()
            status = res_data.get('status')
            detail = res_data.get('detail')

            print(f"\n_____________Signup_______________\nStatus: {status}\nDetails: {detail}\n")
            return status
        except Exception as e:
            messagebox.showerror("Network Error", f"User check failed:\n{str(e)}",parent=self.window)
            return False

    def send_otp(self, email):
        try:
            data = {"email": email}
            res = requests.post(url=f"{BASE_URL}/send-otp", json=data, timeout=10)
            if res.status_code == 200:
                print("OTP Sent: ", "Kindly check your email!")
            else:
                messagebox.showerror("Server Error", "Failed to send OTP. Try again.",parent=self.window)
        except Exception as e:
            messagebox.showerror("Network Error", str(e),parent=self.window)

    def threaded_send_otp(self, email):
        Thread(target=self.send_otp, args=(email,), daemon=True).start()

    # ---------------- Signup Flow ----------------
    def signup(self):
        name_val = self.name.get().strip()
        email_val = self.email.get().strip()
        phone_val = self.phone.get().strip()

        if not name_val or not email_val:
            messagebox.showwarning("Error", "Email and Name is required!",parent=self.window)
            return
        if not self.is_valid_email(email_val):
            messagebox.showwarning("Error", "Invalid email address!",parent=self.window)
            return
        if not self.is_valid_phone(phone_val):
            phone_val = "1236547890"
        self.signupbtn.configure(text="Wait a moment...", state="disabled")

        if self.user_check(name_val, email_val, phone_val)=="invalid user":
            # Send OTP in a separate thread
            self.threaded_send_otp(email_val)
            # Open VerifyScreen
            app = VerifyScreen(main=self.window, name=name_val, mobile=phone_val, email=email_val,username=self.username,plan=self.plan,loginBtn=self.loginBtn)
            app.gui()
        else:
            messagebox.showwarning("User Exists", "User already exists!",parent=self.window)
            self.signupbtn.configure(text="Sign up", state="normal")

    # ---------------- GUI ----------------

    def on_close(self):
        messagebox.showinfo("Info", "Please SignUp",parent=self.window)

    def gui(self):
        icon_pth = os.path.join(os.getcwd(), "assets", "images", "icon.ico")
        print("Window Icon load Successfully")
        self.window.iconbitmap(icon_pth)
        self.window.attributes('-topmost', True)
        self.window.resizable(False,False)
        #self.window.protocol("WM_DELETE_WINDOW",self.on_close)

        self.window.title("DraftZero")

        width, height = 1020, 600
        screen_width = self.window.winfo_screenwidth()
        screen_height = self.window.winfo_screenheight()
        pos_top = int((screen_height - height) / 2)
        pos_right = int((screen_width - width) / 2)
        self.window.geometry(f"{width}x{height}+{pos_right}+{pos_top}")

        # Frames
        element_frame = CTkFrame(master=self.window, width=1020, height=600, fg_color="white")
        element_frame.place(relx=0, rely=0)

        left_frame = CTkFrame(master=element_frame, width=510, height=600, fg_color="white")
        left_frame.place(relx=0, rely=0)

        right_frame = CTkFrame(master=element_frame, width=510, height=600, fg_color="white")
        right_frame.place(relx=0.5, rely=0)

        # Left Side - Form
        CTkLabel(left_frame, text="Sign up", font=("", 35, "bold")).place(relx=0.15, rely=0.1)
        CTkLabel(left_frame, text="Let’s Create Magic with DraftZero.", font=("", 15), text_color="#c6c7c6").place(relx=0.15, rely=0.2)

        CTkLabel(left_frame, text="Name", font=("", 15, "bold")).place(relx=0.15, rely=0.28)
        self.name = CTkEntry(left_frame, placeholder_text="Enter Your Name", width=230, height=40, corner_radius=20)
        self.name.place(relx=0.15, rely=0.35)

        CTkLabel(left_frame, text="Email", font=("", 15, "bold")).place(relx=0.15, rely=0.45)
        self.email = CTkEntry(left_frame, placeholder_text="Enter Your Email", width=230, height=40, corner_radius=20)
        self.email.place(relx=0.15, rely=0.52)

        CTkLabel(left_frame, text="Phone", font=("", 15, "bold")).place(relx=0.15, rely=0.62)
        self.phone = CTkEntry(left_frame, placeholder_text="Enter Your Phone (optional)", width=230, height=40, corner_radius=20)
        self.phone.place(relx=0.15, rely=0.69)

        self.signupbtn = CTkButton(
            left_frame, text="Sign up", fg_color="black", width=230, height=40,
            corner_radius=20, text_color="white", font=("", 15, "bold"),
            hover_color="#575657", command=self.signup
        )
        self.signupbtn.place(relx=0.15, rely=0.8)

        _=CTkLabel(master=left_frame,text="Already have an account?",text_color="#c7c6cf")
        _.place(relx=0.15,rely=.9)

        login = CTkButton(master=left_frame,text="Login",width=6,fg_color="white",bg_color="white",hover_color="white",text_color="black",command=self.login)
        login.place(relx=0.45,rely=.9)

        # Right Side - Image
        img_path = os.path.join(os.getcwd(), "assets", "images", "singup.png")
        pil_img = Image.open(img_path)
        img_tk = CTkImage(dark_image=pil_img, light_image=pil_img, size=(510, 600))
        CTkLabel(right_frame, image=img_tk, width=510, height=600).place(relx=0, rely=0)
        
        self.window.after(2000, lambda: Thread(target=self.window.attributes('-topmost', False)).start)

    

'''# ---------------- Run ----------------
if __name__ == "__main__":
    window = CTkToplevel()
    app = SignUp(window=window)
    app.gui()
    window.mainloop()'''