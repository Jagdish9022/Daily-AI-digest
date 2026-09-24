import os
import smtplib
import logging
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from datetime import datetime

logger = logging.getLogger(__name__)

def send_email(html_content: str) -> bool:
    sender = os.getenv("EMAIL_ADDRESS")
    password = os.getenv("EMAIL_APP_PASSWORD")
    recipient = os.getenv("RECIPIENT_EMAIL")
    
    if not all([sender, password, recipient]):
        logger.error("Email credentials or recipient not set in environment variables.")
        return False
        
    msg = MIMEMultipart('alternative')
    msg['Subject'] = f"Daily AI & Tech Digest - {datetime.now().strftime('%b %d, %Y')}"
    msg['From'] = sender
    msg['To'] = recipient
    
    part = MIMEText(html_content, 'html')
    msg.attach(part)
    
    try:
        server = smtplib.SMTP_SSL('smtp.gmail.com', 465)
        server.login(sender, password)
        server.sendmail(sender, recipient, msg.as_string())
        server.quit()
        logger.info("Email sent successfully.")
        return True
    except Exception as e:
        logger.error(f"Failed to send email: {e}")
        return False
