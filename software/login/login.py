from customtkinter import CTk, CTkFrame, CTkButton, CTkLabel, CTkEntry, CTkImage, set_appearance_mode
from tkinter import messagebox
from threading import Thread
from PIL import Image
import requests, os, re

from otp_logic.verification_login import VerifyScreen
from signup.sign_up import SignUp
from serverId import quilla_Server
set_appearance_mode('light')

URL = quilla_Server()

class LoginScreen:
    appdata_path = os.getenv('APPDATA')

    def __init__(self, main,usernname,plan_details,loginbtn):
        self.window = main
        self.username = usernname
        self.plan_details = plan_details
        self.loginBtn = loginbtn

    def send_otp(self, email):
        """Send OTP to the user's email."""
        data = {"email": email}
        try:
            response = requests.post(url=f"{URL}/send-otp", json=data, timeout=10)
            if response.status_code == 200:
                app = VerifyScreen(main=self.window, email=email,username=self.username,plan_details=self.plan_details,loginbtn=self.loginBtn)
                app.gui()
            else:
                messagebox.showerror("Server Error", f"Failed to send OTP. Code: {response.status_code}",parent=self.window)
        except Exception as e:
            messagebox.showerror("Network Error", f"Error: {str(e)}",parent=self.window)



    def signup(self):

        app = SignUp(window=self.window,username=self.username,plan=self.plan_details,loginBtn=self.loginBtn)
        app.gui()



    def login(self):
        """Handle login button click."""
        email = self.email_entry.get().strip()
        name = self.username_entry.get().strip()
        if not email or not name:
            messagebox.showwarning("Error", "All fields are required.",parent=self.window)
            return
        
        if not self.is_valid_email(email):
            messagebox.showerror("Invalid Email", "Please enter a valid email address.",parent=self.window)
            return

        
        self.loginbtn.configure(state='disabled')
        self.loginbtn.configure(text='Please wait...')
        if self.user_check(name="name",email=email,phone="1234567890")=="invalid user":
            self.loginbtn.configure(state='disabled')
            self.loginbtn.configure(text='Login')
            messagebox.showinfo(title="InvalidUser",message="Please Signup first!",parent=self.window)
        else:
            Thread(target=self.send_otp, args=(email,), daemon=True).start()

           



    def user_check(self, name, email, phone):
        try:
            data = {"username": name, "email": email, "mobile": phone}
            res = requests.post(url=f"{URL}/user_check", json=data, timeout=10)
            res_data = res.json()
            print(f"_______________________________\nStatus:{res_data.get('status')}\nDetail:{res_data.get('detail')}\n")
            return res_data.get('status')
        except Exception as e:
            messagebox.showerror("Network Error", f"User check failed:\n{str(e)}",parent=self.window)
            return False


    def is_valid_email(self, email):
        return re.match(r"[^@]+@[^@]+\.[^@]+", email)

    def netcheck(self):
        try:
            response = requests.get('https://www.google.com', timeout=10)
            if response.status_code == 200:
                print("Internet Connected")
            else:
                messagebox.showerror("Connection Error", "Please check your internet connection.",parent=self.window)
        except Exception as e:
            messagebox.showerror("Connection Error", f"Network check failed:\n{str(e)}",parent=self.window)

    def gui(self):
        icon_pth = os.path.join(os.getcwd(), "assets", "images", "icon.ico")
        print("Window Icon load Successfully")
        self.window.iconbitmap(icon_pth)
        self.window.attributes("-topmost", True)
        self.window.resizable(False,False)
        self.window.title("DraftZero")

        width, height = 1020, 600
        screen_width = self.window.winfo_screenwidth()
        screen_height = self.window.winfo_screenheight()
        position_top = int((screen_height / 2) - (height / 2))
        position_right = int((screen_width / 2) - (width / 2))
        self.window.geometry(f'{width}x{height}+{position_right}+{position_top}')

        for widget in self.window.winfo_children():
            widget.destroy()
        

        self.element_frame = CTkFrame(master=self.window, width=1020, height=600, fg_color="white", corner_radius=0)
        self.element_frame.place(relx=0, rely=0)

        # Left Frame
        left_frame = CTkFrame(master=self.element_frame, width=510, height=600, fg_color="white", corner_radius=0)
        left_frame.place(relx=0, rely=0)

        # Right Frame
        right_frame = CTkFrame(master=self.element_frame, width=510, height=600, fg_color="white", corner_radius=0)
        right_frame.place(relx=0.5, rely=0)

        CTkLabel(master=left_frame, text="Login", text_color="black", font=("", 27, "bold")).place(relx=0.4, rely=0.15)

        self.username_entry = CTkEntry(master=left_frame, placeholder_text="Username", width=250, height=40, corner_radius=0)
        self.username_entry.place(relx=0.25, rely=0.28)

        self.email_entry = CTkEntry(master=left_frame, placeholder_text="Email Address", width=250, height=40, corner_radius=0)
        self.email_entry.place(relx=0.25, rely=0.4)

        self.loginbtn = CTkButton(master=left_frame, width=250, height=40, corner_radius=0,
                  text="Login", fg_color="black", text_color="white",
                  font=("", 17, "bold"), command=self.login)
        self.loginbtn.place(relx=0.25, rely=.55)

        CTkLabel(master=left_frame, text="Don't have an account?").place(relx=0.28, rely=.68)
        CTkButton(master=left_frame, text="Signup", text_color="black",
                  width=50, hover_color="white", fg_color="white", bg_color="white",command=self.signup).place(relx=0.55, rely=0.68)

        img_path = Image.open(os.path.join(os.getcwd(), "assets", "images", "login.png"))
        img_tk = CTkImage(dark_image=img_path, light_image=img_path, size=(510, 600))
        CTkLabel(master=right_frame, image=img_tk, width=510, height=600).place(relx=0, rely=0)
        self.window.after(2000, lambda: Thread(target=self.window.attributes('-topmost', False)).start)


if __name__ == "__main__":
 window = CTk()
 app = LoginScreen(main=window)
 app.gui()
 window.mainloop()
