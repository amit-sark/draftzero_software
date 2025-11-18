import smtplib
from email.message import EmailMessage
from datetime import datetime
import time

def send_bulk_email(receiver_email,receiver_name):
    """
    Send bulk email to multiple recipients about service update
    
    Args:
        receiver_emails: List of email addresses to send to
    """
    
    # Email credentials
    EMAIL_USER = "no-reply@draftzero.in"
    EMAIL_PASS = "Xujdh2RSKx2x"
    EMAIL_HOST = "smtp.zoho.in"
    EMAIL_PORT = 465

    success_count = 0
    failed_emails = []

    try:
            msg = EmailMessage()
            msg["Subject"] = "Service Update - DraftZero AI Back Online"
            msg["From"] = "DraftZero AI <no-reply@draftzero.in>"
            msg["Reply-To"] = "support@draftzero.in"
            msg["Return-Path"] = "no-reply@draftzero.in"
            msg["Message-ID"] = f"<{datetime.now().timestamp()}@draftzero.in>"
            msg["To"] = receiver_email

            html_content = f"""
            <html>
            <head>
            <style>
            body {{ font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; background-color: #f4f6f8; color: #333333; padding: 20px; margin: 0; }}
            .container {{ max-width: 600px; background-color: #ffffff; margin: auto; padding: 30px; border-radius: 10px; box-shadow: 0 4px 12px rgba(0,0,0,0.1); }}
            .header {{ font-size: 26px; font-weight: 700; margin-bottom: 20px; color: #2c3e50; text-align: center; }}
            .content {{ font-size: 16px; line-height: 1.6; color: #555555; }}
            .highlight {{ background-color: #fff3cd; padding: 15px; border-left: 4px solid #ffc107; margin: 20px 0; border-radius: 5px; }}
            .update-box {{ background-color: #d4edda; padding: 15px; border-left: 4px solid #28a745; margin: 20px 0; border-radius: 5px; }}
            .footer {{ font-size: 14px; color: #777777; margin-top: 30px; text-align: center; border-top: 1px solid #eeeeee; padding-top: 20px; }}
            .button {{ display: inline-block; padding: 12px 30px; background-color: #1abc9c; color: #ffffff; text-decoration: none; border-radius: 5px; margin: 20px 0; font-weight: 600; }}
            </style>
            </head>
            <body>
            <div class="container">
                <div class="header">Thank You for Choosing DraftZero AI</div>
                
                <div class="content">
                    <p>Dear {receiver_name},</p>
                    
                    <p>First and foremost, we want to express our heartfelt gratitude for choosing <strong>DraftZero AI</strong> as your trusted tool. Your support means everything to us.</p>
                    
                    <div class="highlight">
                        <strong>⚠️ Service Interruption Notice</strong><br>
                        We sincerely apologize for the service unavailability that occurred from <strong>November 10, 2025</strong> to <strong>November 11, 2025 (8:00 PM)</strong>. We understand how frustrating this must have been, and we take full responsibility for the inconvenience caused.
                    </div>
                    
                    <div class="update-box">
                        <strong>✅ We're Back & Better!</strong><br>
                        We're pleased to inform you that we've deployed a <strong>major update</strong> that fixes critical bugs and resolves the issues that led to the downtime. Our service is now fully operational and more stable than ever.
                    </div>
                    
                    <p><strong>What we've fixed:</strong></p>
                    <ul>
                        <li>Resolved critical system bugs causing service interruptions</li>
                        <li>Improved system stability and performance</li>
                        <li>Enhanced error handling and monitoring</li>
                        <li>Implemented additional safeguards to prevent future outages</li>
                    </ul>
                    
                    <p>We are committed to providing you with the best possible experience and are working tirelessly to ensure such incidents don't happen again.</p>
                    
                    <p><strong>Thank you for your patience and continued trust in DraftZero AI.</strong></p>
                    
                    <p>If you have any questions or concerns, please don't hesitate to reach out to our support team.</p>
                </div>
                
                <div class="footer">
                    Best regards,<br>
                    <strong>The DraftZero AI Team</strong><br>
                    <a href="mailto:support@draftzero.in">support@draftzero.in</a>
                </div>
            </div>
            </body>
            </html>
            """

            # Plain text version
            plain_text = f"""
Thank You for Choosing DraftZero AI

Dear Valued User,

First and foremost, we want to express our heartfelt gratitude for choosing DraftZero AI as your trusted tool. Your support means everything to us.

SERVICE INTERRUPTION NOTICE:
We sincerely apologize for the service unavailability that occurred from November 10, 2025 to November 11, 2025 (8:00 PM). We understand how frustrating this must have been, and we take full responsibility for the inconvenience caused.

WE'RE BACK & BETTER!
We're pleased to inform you that we've deployed a major update that fixes critical bugs and resolves the issues that led to the downtime. Our service is now fully operational and more stable than ever.

What we've fixed:
- Resolved critical system bugs causing service interruptions
- Improved system stability and performance
- Enhanced error handling and monitoring
- Implemented additional safeguards to prevent future outages

We are committed to providing you with the best possible experience and are working tirelessly to ensure such incidents don't happen again.

Thank you for your patience and continued trust in DraftZero AI.

If you have any questions or concerns, please don't hesitate to reach out to our support team.

Best regards,
The DraftZero AI Team
support@draftzero.in
            """

            msg.set_content(plain_text)
            msg.add_alternative(html_content, subtype="html")

            # Send email
            with smtplib.SMTP_SSL(EMAIL_HOST, EMAIL_PORT) as server:
                server.login(EMAIL_USER, EMAIL_PASS)
                server.send_message(msg)
            
            success_count += 1
            print(f"✓ Email sent successfully to: {receiver_email}")
            
    except Exception as e:
        failed_emails.append(receiver_email)
        print(f"✗ Failed to send email to {receiver_email}: {str(e)}")
    
    # Summary
    print(f"\n{'='*50}")
    print(f"Email sending completed!")
    print(f"Successfully sent: {success_count}")
    if failed_emails:
        print(f"Failed emails: {', '.join(failed_emails)}")
    print(f"{'='*50}")
    
    return success_count, failed_emails
