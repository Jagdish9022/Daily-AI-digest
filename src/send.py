import os
import smtplib
import logging
from concurrent.futures import ThreadPoolExecutor, as_completed
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from datetime import datetime

logger = logging.getLogger(__name__)


RECIPIENT_EMAILS = [
    "jagdishpagar28@gmail.com",
    "sahilwable.in@gmail.com",
]


def get_recipient_list() -> list[str]:
    """
    Retrieves and deduplicates recipient emails from:
    1. RECIPIENT_EMAIL environment variable (supports comma-separated emails).
    2. RECIPIENT_EMAILS array defined above.
    """
    recipients = []

    # 1. Environment variable (supports single or comma-separated emails)
    env_recipients = os.getenv("RECIPIENT_EMAIL", "")
    if env_recipients:
        for email in env_recipients.split(","):
            cleaned = email.strip()
            if cleaned and cleaned not in recipients:
                recipients.append(cleaned)

    # 2. Python list/array defined above
    for email in RECIPIENT_EMAILS:
        cleaned = email.strip()
        if cleaned and cleaned not in recipients:
            recipients.append(cleaned)

    return recipients


def _send_to_single_recipient(sender: str, password: str, recipient: str, html_content: str, subject: str) -> tuple[str, bool, str]:
    """
    Sends an email to a single recipient over SMTP SSL.
    Returns (recipient, success_boolean, status_message).
    """
    msg = MIMEMultipart('alternative')
    msg['Subject'] = subject
    msg['From'] = sender
    msg['To'] = recipient

    part = MIMEText(html_content, 'html')
    msg.attach(part)

    try:
        with smtplib.SMTP_SSL('smtp.gmail.com', 465) as server:
            server.login(sender, password)
            server.sendmail(sender, recipient, msg.as_string())
        return recipient, True, "Success"
    except Exception as e:
        return recipient, False, str(e)


def send_email(html_content: str) -> bool:
    """
    Sends email simultaneously to all configured recipients using a thread pool.
    """
    sender = os.getenv("EMAIL_ADDRESS")
    password = os.getenv("EMAIL_APP_PASSWORD")
    recipients = get_recipient_list()

    if not sender or not password:
        logger.error("EMAIL_ADDRESS or EMAIL_APP_PASSWORD not set in environment variables.")
        return False

    if not recipients:
        logger.error("No recipient emails found. Add emails to RECIPIENT_EMAILS array in src/send.py or set RECIPIENT_EMAIL in .env.")
        return False

    subject = f"Daily AI & Tech Digest - {datetime.now().strftime('%b %d, %Y')}"
    logger.info(f"Sending email to {len(recipients)} recipient(s) simultaneously: {', '.join(recipients)}")

    success_count = 0
    total = len(recipients)

    # Send emails simultaneously in parallel threads
    max_workers = min(10, len(recipients))
    with ThreadPoolExecutor(max_workers=max_workers) as executor:
        future_to_email = {
            executor.submit(_send_to_single_recipient, sender, password, recipient, html_content, subject): recipient
            for recipient in recipients
        }

        for future in as_completed(future_to_email):
            recipient, success, msg_text = future.result()
            if success:
                logger.info(f"Successfully sent email to {recipient}")
                success_count += 1
            else:
                logger.error(f"Failed to send email to {recipient}: {msg_text}")

    logger.info(f"Email delivery complete: {success_count}/{total} emails sent successfully.")
    return success_count > 0

