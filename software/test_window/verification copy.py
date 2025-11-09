from customtkinter import CTk, CTkFrame, CTkButton, CTkLabel, CTkEntry, CTkImage,set_appearance_mode
from tkinter import messagebox
import requests, os
from PIL import Image

set_appearance_mode('light')

class VerifyScreen:
    appdata_path = os.getenv('APPDATA')

    def __init__(self, main, email):
        self.window = main
        self.email_id = email
        print(f'Email: {email}')

    def netcheck(self):
        print("Net Check ...")
        try:
            url = 'https://www.google.com'
            re = requests.get(url, timeout=10)
            if re.status_code == 200:
                print("Internet Connected")
            else:
                messagebox.showerror(title="Connection Error", message="Please check your internet connection")
        except Exception as e:
            messagebox.showerror(title="Connection Error", message=f"Network check failed:\n{str(e)}")

    def gui(self):
        width, height = 1020, 600
        screen_width = self.window.winfo_screenwidth()
        screen_height = self.window.winfo_screenheight()
        position_top = int((screen_height / 2) - (height / 2))
        position_right = int((screen_width / 2) - (width / 2))
        self.window.geometry(f'{width}x{height}+{position_right}+{position_top}')
        #--- Right side frame 


        self.element_window = CTkFrame(master=self.window,width=1020,height=600,fg_color="white")
        self.element_window.place(relx=0,rely=0)



        right_frame = CTkFrame(master=self.element_window,width=510,height=600,fg_color="white",corner_radius=0)
        right_frame.place(relx=0.5,rely=0)

        left_side = CTkFrame(master=self.element_window, width=510, height=400, fg_color="white",corner_radius=0)
        left_side.place(relx=0, rely=0)

        # --- Centered content area ---
        content_frame = CTkFrame(master=left_side, fg_color="transparent",corner_radius=0)
        content_frame.place(relx=0.5, rely=0.5, anchor="center")  # center vertically around 35%
        # --- Don't get frame

        resend_frame = CTkFrame(master=self.window,width=510,height=200,fg_color="white",corner_radius=0)
        resend_frame.place(relx=0.0,rely=0.665)
        # Title
        title_label = CTkLabel(content_frame, text="Confirm Your Email",font=("", 18, "bold"), text_color="black")
        title_label.pack(anchor="center")

        # Email info
        self.email_info = CTkLabel(content_frame,text=f"We sent a code to {self.email_id}",font=("", 12),wraplength=400,justify="center",text_color="#969696")
        self.email_info.pack(anchor="center", pady=(5, 15))

        # --- OTP Entry Row ---
        otp_frame = CTkFrame(master=content_frame, fg_color="transparent",corner_radius=0)
        otp_frame.pack(anchor="center", pady=(10, 20))

        self.otp_entries = []
        for i in range(6):
            entry = CTkEntry(master=otp_frame,width=45, height=50,font=("Arial", 20),corner_radius=8,justify="center" )
            entry.pack(side="left", padx=6)
            entry.bind("<KeyRelease>", lambda event, idx=i: self.on_otp_key(event, idx))
            self.otp_entries.append(entry)

        # --- Verify Button ---
        self.verify_button = CTkButton(content_frame,text="Create an account",width=250, height=45,font=("Arial", 16),corner_radius=10,fg_color="black",text_color="white",hover_color="#4b4b4b",command=self.verify_otp)
        self.verify_button.pack(anchor="center", pady=(15, 0))


        #--- Resend unit 
        CTkLabel(resend_frame, text="Didn't get a code?", font=("Arial", 12), text_color="gray").place(relx=0.31,rely=0.5)
        self.resend_button = CTkButton(resend_frame, text="Resend Code", font=("Arial", 12,"bold"),fg_color="transparent",text_color="black", width=10)
        self.resend_button.place(relx=0.495,rely=0.5)


        lady_img_path = os.path.join(os.getcwd(),"assets","images","email.png")
        img = Image.open(lady_img_path)
        lady_img_tk = CTkImage(dark_image=img,light_image=img,size=(510,600))
        _ = CTkLabel(master=right_frame,image=lady_img_tk,text="")
        _.place(relx=0,rely=0)


    def on_otp_key(self, event, index):
        key = event.char
        if key.isdigit():
            self.otp_entries[index].delete(0, "end")
            self.otp_entries[index].insert(0, key)
            if index < 5:
                self.otp_entries[index + 1].focus()
        elif key == "":
            if self.otp_entries[index].get() == "" and index > 0:
                self.otp_entries[index - 1].focus()
        else:
            self.otp_entries[index].delete(0, "end")

    def verify_otp(self):
        otp = "".join(entry.get() for entry in self.otp_entries)
        if len(otp) != 6 or not otp.isdigit():
            messagebox.showwarning("Invalid OTP", "Please enter your 6-digit OTP")
        else:
            print("Entered OTP:", otp)
            self.final_otp = otp
            self.verify_button.configure(text="Verifying...", state="disabled")


window = CTk()
app = VerifyScreen(main=window, email="amitsarkar@gmail.com")
app.gui()
window.mainloop()
