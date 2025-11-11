import requests
from tkinter import messagebox
from plyer import notification
import json,os,time
from threading import Thread


from serverId import quilla_Server

URL = quilla_Server()

APPICATION_VERSION = 1.3


class UpdateManager:
     

    def __init__(self):
        pass
    def show_update_prompt(self):
            
        messagebox.showwarning(title="Mandatory Update",message="A required update is available. The software will not function without updating.\n\nPlease update now.")

    def show_notification(self, title, message):
        """Display system notification."""
        try:
            notification.notify(
                title=title,
                message=message,
                app_name="DraftZero Updater",
                timeout=8
            )
        except Exception as e:
            print(f"Notification error: {e}")


    def download_update(self, link):
        try:
            response = requests.get(link, timeout=10)
            response.raise_for_status()
        except requests.RequestException as e:
            print(f"Download failed: {e}")
            return

        appdata_path = os.getenv("TEMP")
        if not appdata_path:
            print("Error: Could not determine TEMP path.")
            return

        save_dir = os.path.join(appdata_path, ".quilla", "update")
        os.makedirs(save_dir, exist_ok=True)

        self.file_name = os.path.join(save_dir, "DraftZero.exe")

        with open(self.file_name, "wb") as f:
            f.write(response.content)

        print(f"Update downloaded and saved at: {self.file_name}")

        # Run installer (optional)
        
        th= Thread(target=self.update)
        th.start()

        time.sleep(2)
        
        try:
            os.system("taskkill /IM DraftZero.exe /F")
        except :
            pass   


    def update(self):
        
        os.startfile(self.file_name)
        print("Insaconncet Update")
        

    def check_for_updates(self):

        re = requests.get(url=f"{URL}/update")

        try:

            if re.status_code==200:
            
                print(f"Contain: {re.content}\n")
                
                res_data = re.json()
                version = res_data.get('version')
                installer_link = res_data.get('executable_link')
                print(f"VERSION: {version}\nINSTALLER: {installer_link}\n")
                
                if version>APPICATION_VERSION:
                    self.show_update_prompt()
                    self.show_notification(
                        title="DraftZero Update Available",
                        message=f"Downloading version v{version}..."
                    )
                    self.download_update(installer_link)

                else:
                    print(f"________________\nApplication verssion: {APPICATION_VERSION}\nLatest Verssion: {version}\nNo Already upto date!")

                
                
                
                
                
                
            else:
                print("UPDATE: ERROR: [404]")

        except requests.RequestException as e:
            print(f"Network error during checking update: {e}")
            messagebox.showerror("Network Error", "Unable to connect to the server. Please check your internet connection.")




'''update_app = update()
update_app.get_details_from_server()
'''