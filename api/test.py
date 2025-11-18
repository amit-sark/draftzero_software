import csv
from email_test import send_bulk_email
from time import sleep
index=0

with open("users.csv",mode="r") as file:

    reader = csv.DictReader(file)
    for row in reader:
        index=index+1
        username = row['username']
        email = row['email']
        send_bulk_email(receiver_email=email,receiver_name=username)
        sleep(1)        