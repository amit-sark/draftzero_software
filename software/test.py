import csv 
import os 

appdata = os.getenv('APPDATA')
quilla_folder = os.path.join(appdata, ".Quilla")

LOGIN_PATH = os.path.join(quilla_folder, "login_data.csv")
SIGN_PATH = os.path.join(quilla_folder, "signup_data.csv")


if os.path.exists(LOGIN_PATH) or os.path.exists(SIGN_PATH):
        file_path = LOGIN_PATH if os.path.exists(LOGIN_PATH) else SIGN_PATH
        print("Login button hidden — user file found.")
        with open(file_path, 'r', newline='', encoding='utf-8') as file:
                reader = csv.DictReader(file)  # Automatically uses header names
                print(f"\nReading data from: {file_path}\n")
                for row in reader:
                    print(f"SL: {row['sl']}")
                    print(f"Username: {row['username']}")
                    print(f"Email: {row['email']}")
                    print(f"Mobile: {row['mobile']}")
                    print(f"Free Trial Active: {row['free_trial_active']}")
                    print(f"Free Trial Start: {row['free_trial_start']}")
                    print(f"Free Trial End: {row['free_trial_end']}")
                    print(f"Stored At: {row['stored_at']}")
                    print("-" * 60)

                                  