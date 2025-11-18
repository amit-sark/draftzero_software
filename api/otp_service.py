import random
from database import SessionLocal
from models import OTP
from datetime import datetime, timedelta
import os


import random
from sqlalchemy.orm import Session
from models import OTP
from datetime import datetime, timedelta

def generate_otp():
    return str(random.randint(100000, 999999))

def store_otp(db: Session, email: str, otp: str):
    new_otp = OTP(email=email, otp=otp)
    db.add(new_otp)
    db.commit()
    db.refresh(new_otp)
    return new_otp

def verify_otp(db: Session, email: str, otp: str):
    record = db.query(OTP).filter(OTP.email == email).order_by(OTP.created_at.desc()).first()

    if record and record.otp == otp:
        record.verified = True
        db.commit()
        return True
    return False


def send_email(receiver_email: str, otp: str):
    import smtplib
    from email.message import EmailMessage

    # Check if receiver is Hotmail/Outlook
    is_microsoft_email = any(domain in receiver_email.lower() for domain in ['@hotmail.', '@outlook.', '@live.'])

    # Choose SMTP provider based on receiver's domain
    if is_microsoft_email:
        # Use Gmail for Hotmail/Outlook recipients
        EMAIL_USER = "sarkzone52@gmail.com"  # Replace with your Gmail
        EMAIL_PASS = "eplkfoaueknzgvwm"  # Replace with your Gmail App Password
        EMAIL_HOST = "smtp.gmail.com"
        EMAIL_PORT = 465
        FROM_EMAIL = "DraftZero AI <sarkzone52@gmail.com>"
    else:
        # Use Zoho by default
        EMAIL_USER = "no-reply@draftzero.in"
        EMAIL_PASS = "Xujdh2RSKx2x"
        EMAIL_HOST = "smtp.zoho.in"
        EMAIL_PORT = 465
        FROM_EMAIL = "DraftZero AI <no-reply@draftzero.in>"

    msg = EmailMessage()
    msg["Subject"] = "DraftZero AI Authentication code"
    msg["From"] = FROM_EMAIL
    msg["Reply-To"] = "support@draftzero.in"
    msg["Return-Path"] = "no-reply@draftzero.in"
    msg["Message-ID"] = f"<{datetime.now().timestamp()}@draftzero.in>"
    msg["To"] = receiver_email

    html_content = f"""
        <html>
        <head>
        <style>
        body {{ font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; background-color: #f4f6f8; color: #333333; padding: 20px; margin: 0; }}
        .container {{ max-width: 600px; background-color: #ffffff; margin: auto; padding: 30px; border-radius: 10px; box-shadow: 0 4px 12px rgba(0,0,0,0.1); text-align: center; }}
        .header {{ font-size: 24px; font-weight: 700; margin-bottom: 15px; color: #2c3e50; }}
        .otp-code {{ display: inline-block; font-size: 36px; letter-spacing: 10px; font-weight: 700; color: #1abc9c; background-color: #eafaf8; padding: 15px 30px; border-radius: 8px; margin: 20px 0; user-select: all; }}
        .footer {{ font-size: 14px; color: #777777; margin-top: 30px; }}
        .note {{ margin-top: 20px; font-size: 16px; color: #555555; }}
        </style>
        </head>
        <body>
        <div class="container">
        <div class="header">OTP Verification</div>
        <p>Use the following One-Time Password (OTP) to complete your verification process:</p>
        <div class="otp-code">{otp}</div>
        <p class="note">This OTP is valid for <strong>2 minutes</strong>.</p>
        <div class="footer">
        If you did not request this code, please ignore this email.<br> 
        Thank you for choosing our service.
        </div>
        </div>

        </body>
        </html>
    """

    msg.set_content(f"Your OTP is: {otp} (valid for 2 minutes)")
    msg.add_alternative(html_content, subtype="html")

    try:
        with smtplib.SMTP_SSL(EMAIL_HOST, EMAIL_PORT) as server:
            server.login(EMAIL_USER, EMAIL_PASS)
            server.send_message(msg)
        print(f"Email sent successfully using {EMAIL_HOST}")
    except Exception as e:
        print(f"Error sending email: {e}")
        raise