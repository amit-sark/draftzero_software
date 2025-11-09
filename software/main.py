from customtkinter import CTk, CTkFrame, CTkLabel, CTkButton, CTkImage, set_appearance_mode
from PIL import Image
from functools import partial
import os,csv
import requests
# window 

from window.scripts_writer_link import ScriptWriterLink
from threading import Thread
from tkinter import messagebox
from datetime import datetime,date

from LIBS.update import UpdateManager
from serverId import quilla_Server

set_appearance_mode('light')

URL = quilla_Server()
appdata = os.getenv('APPDATA')
quilla_folder= os.path.join(appdata,".Quilla")

if not os.path.exists(quilla_folder):
    os.makedirs(quilla_folder)
    print(f"Created folder: {quilla_folder}")
else:
    print(f"Folder already exists: {quilla_folder}")

LOGIN_PATH = os.path.join(quilla_folder,"login_data.csv")
SIGN_PATH = os.path.join(quilla_folder,"signup_data.csv")


BASE_PATH = os.getcwd()

class Quilla:
    def __init__(self, main):
        self.window = main
        self.selected_button = None  
        self.current_screen = None

    def activation_validation_check(self):

        if os.path.exists(SIGN_PATH) or os.path.exists(LOGIN_PATH):

            if os.path.exists(os.path.join(quilla_folder,'qa.key')):

                with open(file=os.path.join(quilla_folder,'qa.key'),mode='r') as file:

                    id = file.readline().strip()
                    print(f"\n__________________________________________\nActivation id: {id}\n__________________________________________\n")

                    re = requests.get(url=f'{URL}/activation_details/{id}')
                    if re.status_code==200:

                        res_data = re.json()

                        if res_data.get('status')=='success':
                            expiry=res_data.get('expiry_date')
                            days_left = self.days_left(expiry)
                            print(f"\n_____________________________\nProduct Expire within: {days_left}\n_____________________________")
                            if days_left!=0:
                                self.plan_details.configure(text=f'Expire in {days_left} days.')
                            else:
                                self.plan_details.configure(text='Expired')


                    #days= self.days_left()



    
    def update_quilla(self):
        
        UpdateManager().check_for_updates()
        
        
    def select_button(self, button_name, button):
        """Handles the selection of a button with proper cleanup and highlighting."""
        
        # Reset previous button appearance
        if self.selected_button is not None:
            self.selected_button.configure(
                fg_color='#fafaf9',
                text_color='black'
            )
        
        # Highlight the newly selected button
        button.configure(
            fg_color='#e4e4e5',  # or use a more distinct color like '#d4d4d8'
            text_color='black'
        )
        
        # Update the selected button reference
        self.selected_button = button
        
        # Clean up the previous screen before switching
        if self.current_screen is not None:
            try:
                self.current_screen.stop_resizing()
                print(f"Cleaned up previous screen: {type(self.current_screen).__name__}")
            except Exception as e:
                print(f"Error during cleanup: {e}")
        
        # Now switch to the new screen
        button_name = button_name.strip()
        print(f"Selected: {button_name}")
        
        if button_name == 'Script Writer':
            self.current_screen = ScriptWriterLink(window=self.element_window)
            self.current_screen.gui()

        elif button_name == 'Feedback':
            from window.feedback import FeedbackForm
            self.current_screen = FeedbackForm(window=self.element_window)
            self.current_screen.gui()

        elif button_name == 'Profile':
            from window.user_profile import UserProfile
            self.current_screen = UserProfile(window=self.element_window)
            self.current_screen.gui()

        elif button_name == 'SEO Helper':
            from window.seo_generator import SeoGenerator
            self.current_screen = SeoGenerator(window=self.element_window)
            self.current_screen.gui()

        elif button_name == 'Caption Maker':
            from window.CaptionMaker import Captionmaker
            self.current_screen = Captionmaker(window=self.element_window)
            self.current_screen.gui()

        elif button_name == 'Setting':
            # TODO: Implement settings screen
            pass

        elif button_name == 'News & Update':
            # TODO: Implement news screen
            pass


    def loginbtn(self):

        if os.path.exists(LOGIN_PATH) or os.path.exists(SIGN_PATH):
            # Pick whichever file exists
            file_path = LOGIN_PATH if os.path.exists(LOGIN_PATH) else SIGN_PATH

            with open(file_path, 'r', newline='', encoding='utf-8') as file:
                reader = csv.DictReader(file)  # Automatically uses header names
                print(f"\nReading data from: {file_path}\n")

                for row in reader:
                    print(f"SL: {row['sl']}")
                    print(f"Username: {row['username']}")
                    name = row['username']
                    self.user_label.configure(text=name)
                    print(f"Email: {row['email']}")
                    print(f"Mobile: {row['mobile']}")
                    print(f"Free Trial Active: {row['free_trial_active']}")
                    print(f"Free Trial Start: {row['free_trial_start']}")
                    print(f"Free Trial End: {row['free_trial_end']}")
                    print(f"Stored At: {row['stored_at']}")
                    print("-" * 60)
        else:
            self.loginBtn = CTkButton(master=self.user_details,text="Login",fg_color="black",text_color="white",height=40,command=self.login_sc)
            self.loginBtn.place(relx=0,rely=0.258)
        
    def check_files(self):
        if os.path.exists(LOGIN_PATH) or os.path.exists(SIGN_PATH):
            file_path = LOGIN_PATH if os.path.exists(LOGIN_PATH) else SIGN_PATH

            # File appeared → destroy login button
            if hasattr(self, 'loginBtn') and self.loginBtn:
                self.loginBtn.destroy()
                print("Login button hidden — user file found.")

                with open(file_path, 'r', newline='', encoding='utf-8') as file:
                    reader = csv.DictReader(file)  # Automatically uses header names
                    print(f"\nReading data from: {file_path}\n")

                    for row in reader:
                        print(f"SL: {row['sl']}")
                        print(f"Username: {row['username']}")
                        name = row['username']
                        self.user_label.configure(text=name)
                        print(f"Email: {row['email']}")
                        print(f"Mobile: {row['mobile']}")
                        print(f"Free Trial Active: {row['free_trial_active']}")
                        print(f"Free Trial Start: {row['free_trial_start']}")
                        print(f"Free Trial End: {row['free_trial_end']}")
                        print(f"Stored At: {row['stored_at']}")
                        print("-" * 60)

                return  # Stop checking after file is found    
        else:
            # Check again after 1 second
            print("Checking for login details....")
            self.user_details.after(1000, self.check_files)


    def login_sc(self):

        from customtkinter import CTkToplevel
        from login.login import LoginScreen

        loging_window = CTkToplevel()
        icon_pth = os.path.join(os.getcwd(), "assets", "images", "icon.ico")
        print("Window Icon load Successfully")
        loging_window.iconbitmap(icon_pth)
        app = LoginScreen(main=loging_window,usernname=self.user_label,plan_details=self.plan_details,loginbtn=self.loginBtn)
        app.gui()


    def gui(self):
        self.window.title("DraftZero")

        width, height = 1340, 730
        screen_width = self.window.winfo_screenwidth()
        screen_height = self.window.winfo_screenheight()
        position_top = int((screen_height / 2) - (height / 2))
        position_right = int((screen_width / 2) - (width / 2))
        self.window.geometry(f'{width}x{height}+{position_right}+{position_top}')
        
        icon_pth = os.path.join(BASE_PATH, "assets", "images", "icon.ico")
        print("Window Icon load Successfully")
        self.window.iconbitmap(icon_pth)

       

        # Side panel
        self.side_panel = CTkFrame(
            master=self.window, width=250, fg_color='#fafaf9', corner_radius=0
        )
        self.side_panel.grid(column=0, row=0, sticky="nsew")

        self.element_window = CTkFrame(master=self.window)
        self.element_window.grid(column=1, row=0, sticky="nsew")

        self.window.grid_columnconfigure(0, weight=0)  
        self.window.grid_columnconfigure(1, weight=1)  
        self.window.grid_rowconfigure(0, weight=1)     

        # Title
        title_label = CTkLabel(master=self.side_panel, text='DraftZero', font=('', 22, 'bold'))
        title_label.place(relx=0.3, rely=0.03)

        self.button_frame = CTkFrame(master=self.side_panel, fg_color='#fafaf9')
        self.button_frame.place(relx=0.03, rely=0.13)


        self.account = CTkLabel(master=self.side_panel,text="Account",font=("",14,'bold'))
        self.account.place(relx=0.1,rely=0.48)

        self.user_frame = CTkFrame(master=self.side_panel, fg_color='#fafaf9')
        self.user_frame.place(relx=0.03, rely=0.53)
        
        # user detials

        self.user_details = CTkFrame(master=self.side_panel,height=60,width=240,fg_color='#fafaf9')
        self.user_details.place(relx=0.02,rely=.9)

        user_img = Image.open(os.path.join(BASE_PATH,'assets','icons','profile.png'))
        user_img = CTkImage(light_image=user_img,dark_image=user_img,size=(26,26))

        user_img_lable= CTkLabel(master=self.user_details,image=user_img,text='')
        user_img_lable.place(relx=0.03,rely=0.28)

        self.user_label = CTkLabel(master=self.user_details,text="Guest Users")
        self.user_label.place(relx=0.23,rely=0.1)

        self.plan_details = CTkLabel(master=self.user_details,text="Free Trial",text_color="#a1a0a0")
        self.plan_details.place(relx=0.23,rely=0.5)


        # Buttons with images
        imgs_pth = [
            {'name': 'Script Writer', 'path': os.path.join(BASE_PATH, 'assets', 'icons', 'pencil.png')},
            {'name': 'Caption Maker', 'path': os.path.join(BASE_PATH, 'assets', 'icons', 'caption.png')},
            {'name': 'SEO Helper', 'path': os.path.join(BASE_PATH, 'assets', 'icons', 'seo.png')},
            {'name': 'Feedback', 'path': os.path.join(BASE_PATH, 'assets', 'icons', 'feedback.png')}, 

            #{'name': 'News & Update', 'path': os.path.join(BASE_PATH, 'assets', 'icons', 'megaphone.png')},
        ]

        row = 0
        for img_path in imgs_pth:
            name, path = img_path['name'], img_path['path']
            print(f"name: {name}\tpath: {path}\n")
            try:
                img = Image.open(path)
                img_tk = CTkImage(light_image=img, dark_image=img, size=(24, 24))
            except FileNotFoundError:
                print(f"Image not found: {path}")
                img_tk = None  

            button = CTkButton(
                master=self.button_frame,
                text=name,
                width=230,
                height=43,
                fg_color='#fafaf9',
                text_color='black',
                image=img_tk,
                font=('', 14),
                hover_color='#e4e4e5',
                anchor="w",      
                compound="left",  
            )
            button.configure(command=partial(self.select_button, name, button))
            button.grid(column=0, row=row, pady=5)
            row += 1

        self.select_button('Script Writer', self.button_frame.winfo_children()[0])

        imgs_pth = [
                {'name': 'Profile', 'path': os.path.join(BASE_PATH, 'assets', 'icons', 'user.png')},
                #{'name': 'Feedback', 'path': os.path.join(BASE_PATH, 'assets', 'icons', 'feedback.png')}, 
                {'name': 'Setting', 'path': os.path.join(BASE_PATH, 'assets', 'icons', 'settings.png')},

            ]

        row = 0
        for img_path in imgs_pth:
            name, path = img_path['name'], img_path['path']
            print(f"name: {name}\tpath: {path}\n")
            try:
                img = Image.open(path)
                img_tk = CTkImage(light_image=img, dark_image=img, size=(24, 24))
            except FileNotFoundError:
                print(f"Image not found: {path}")
                img_tk = None  

            button = CTkButton(
                master=self.user_frame,
                text=name,
                width=230,
                height=43,
                fg_color='#fafaf9',
                text_color='black',
                image=img_tk,
                font=('', 14),
                hover_color='#e4e4e5',
                anchor="w",      
                compound="left",  
            )
            button.configure(command=partial(self.select_button, name, button))
            button.grid(column=0, row=row, pady=5)
            row += 1
        #self.select_button('Script Writer', self.button_frame.winfo_children()[0])
        self.select_button('Script Writer', self.button_frame.winfo_children()[0])

        signup = Thread(target=self.signup,daemon=True)
        signup.start()

        login_file_check = Thread(target=self.check_files,daemon=True)
        login_file_check.start()

        login = Thread(target=self.automatic_loging,daemon=True)
        login.start()

        activation_check = Thread(target=self.activation_validation_check,daemon=True)
        activation_check.start()

        if os.path.exists(LOGIN_PATH) or os.path.exists(SIGN_PATH):
            update_check = Thread(target=self.update_quilla)
            update_check.start()
        
        
        self.loginbtn()



    def signup(self):
        import time
        from customtkinter import CTkToplevel
        from signup.sign_up import SignUp

        time.sleep(1)
        appdata = os.getenv('APPDATA')
        quilla_folder = os.path.join(appdata,".Quilla")
        login_path = os.path.join(quilla_folder, "login_data.csv")
        signup_path = os.path.join(quilla_folder, "signup_data.csv")

        # Check if any of the files already exist
        if os.path.exists(login_path) or os.path.exists(signup_path):
            print("Signup skipped — existing user data found.")
            return  # Skip opening signup window

        # Otherwise, open signup window
        signup_window = CTkToplevel()
        icon_pth = os.path.join(os.getcwd(), "assets", "images", "icon.ico")
        print("Window Icon load Successfully")
        signup_window.iconbitmap(icon_pth)
        app = SignUp(window=signup_window,username=self.user_label,plan=self.plan_details,loginBtn=self.loginBtn)
        app.gui()

    def automatic_loging(self):

        try:
            if os.path.exists(LOGIN_PATH) or os.path.exists(SIGN_PATH):
                file_path = LOGIN_PATH if os.path.exists(LOGIN_PATH) else SIGN_PATH
                with open(file_path, 'r', newline='', encoding='utf-8') as file:
                    reader = csv.DictReader(file)  
                    print(f"\nReading data from: {file_path}\n")
                    for row in reader:
                        print(f"SL: {row['sl']}")
                        print(f"Username: {row['username']}")
                        name = row['username']
                        end_date = row['free_trial_end']
                        days = self.days_left(end_date)

                        if days==0:
                            self.plan_details.configure(
                                text=f"Free Trial End."
                            )
                        else:
                        
                            self.plan_details.configure(
                                text=f"Free Trial: {days} days left"
                            )
                            
                                
                        self.user_label.configure(text=name)
                        print(f"Email: {row['email']}")
                        email= row['email']
                        print(f"Mobile: {row['mobile']}")
                        mobile= row['mobile']
                        print(f"Free Trial Active: {row['free_trial_active']}")
                        print(f"Free Trial Start: {row['free_trial_start']}")
                        print(f"Free Trial End: {row['free_trial_end']}")
                        print(f"Stored At: {row['stored_at']}")
                        print("-" * 60)
            
            
                    data = {"email": email,"mobile":mobile}
                    res = requests.post(url=f"{URL}/login", json=data, timeout=10)

                    if res.status_code == 200:
                        response_data = res.json()  # your JSON like {"sl": 0, "username": "...", ...}

                        print(f"login contain: {response_data}")
                        #messagebox.showinfo("Success", "Account created successfully!")

                        # === Store data in CSV ===
                        appdata = os.getenv('APPDATA')
                        quilla_folder= os.path.join(appdata,'.Quilla')
                        csv_file = os.path.join(quilla_folder,"login_data.csv")

                        with open(csv_file, mode="w", newline="", encoding="utf-8") as file:
                            writer = csv.writer(file)
                            # Write header only if file is empty
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

                        self.user_label.configure(text=response_data.get("username"))

                    else:
                        print("Response:", res.text)
                        self.loginBtn = CTkButton(master=self.user_details,text="Login",fg_color="black",text_color="white",height=40,command=self.login_sc)
                        self.loginBtn.place(relx=0,rely=0.258)
                        self.plan_details.configure(text="")
                        messagebox.showwarning(title="User Not Found 🚫",message=( "Oops! We couldn’t find that username.\n" "Double-check your spelling or try again.\n" "Everyone makes typos — even the best of us!"))


        except requests.RequestException as e:
            print(f"Network error during login: {e}")
            messagebox.showerror("Network Error", "Unable to connect to the server. Please check your internet connection.")
        except Exception as e:
            print(f"Unexpected error: {e}")
            messagebox.showerror("Error", "An unexpected error occurred. Please try again later.")

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
if __name__ == "__main__":
    window = CTk()
    application = Quilla(main=window)
    application.gui()
    window.mainloop()