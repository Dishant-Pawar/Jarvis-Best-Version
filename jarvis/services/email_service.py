import smtplib
import imaplib
import email
from email.mime.text import MIMEText
from typing import Tuple
from jarvis.utils.logger import logger
from jarvis.config.settings import SENDER_EMAIL, SENDER_PASSWORD

class EmailService:
    @staticmethod
    def send_email(to_email: str, subject: str, body: str) -> Tuple[bool, str]:
        """Send an email using SMTP. Falls back to simulation if credentials are not configured."""
        if not SENDER_EMAIL or not SENDER_PASSWORD or "your_email" in SENDER_EMAIL:
            # Simulation Mode
            sim_msg = f"[SIMULATED EMAIL] To: {to_email} | Subject: {subject} | Body: {body}"
            logger.info(sim_msg)
            return True, "Email sent successfully in simulation mode. Configure your .env file for real SMTP sending."

        try:
            logger.info(f"Preparing to send email to: {to_email}")
            msg = MIMEText(body, 'plain', 'utf-8')
            msg['Subject'] = subject
            msg['From'] = SENDER_EMAIL
            msg['To'] = to_email

            # Assuming Gmail SMTP setup, port 465 SSL
            server = smtplib.SMTP_SSL('smtp.gmail.com', 465)
            server.login(SENDER_EMAIL, SENDER_PASSWORD)
            server.sendmail(SENDER_EMAIL, [to_email], msg.as_string())
            server.quit()
            
            logger.info("Email sent successfully!")
            return True, "Email has been sent successfully."
        except Exception as e:
            err_msg = f"Failed to send email: {e}"
            logger.error(err_msg)
            return False, err_msg

    @staticmethod
    def read_recent_emails(limit: int = 3) -> str:
        """Fetch details of recent emails using IMAP. Falls back to simulation if credentials are not configured."""
        if not SENDER_EMAIL or not SENDER_PASSWORD or "your_email" in SENDER_EMAIL:
            # Simulation Mode
            logger.info("Simulation mode: reading email details...")
            return (
                "Here are your simulated recent emails. "
                "First, from John: Hey, let's meet up today at 5 PM. "
                "Second, from HR: Please complete your weekly attendance report. "
                "Third, from GitHub: A security alert was triggered on one of your repositories."
            )

        try:
            logger.info("Connecting to IMAP server to fetch email details...")
            mail = imaplib.IMAP4_SSL('imap.gmail.com')
            mail.login(SENDER_EMAIL, SENDER_PASSWORD)
            mail.select('inbox')

            # Search all emails
            status, search_data = mail.search(None, 'ALL')
            mail_ids = search_data[0].split()

            if not mail_ids:
                return "You have no emails in your inbox."

            email_details = []
            # Get latest 'limit' emails
            recent_ids = mail_ids[-limit:]
            # Reverse order to read newest first
            recent_ids.reverse()

            for mail_id in recent_ids:
                status, data = mail.fetch(mail_id, '(RFC822)')
                raw_email = data[0][1]
                msg = email.message_from_bytes(raw_email)
                
                # Parse Subject and From headers safely
                subject = msg.get("Subject", "No Subject")
                from_sender = msg.get("From", "Unknown Sender")
                
                # Try parsing readable sender name
                if "<" in from_sender:
                    from_sender = from_sender.split("<")[0].strip()
                
                email_details.append(f"From {from_sender} regarding '{subject}'")

            mail.close()
            mail.logout()

            details_str = ". ".join(email_details)
            return f"Here are your top recent emails: {details_str}"
        except Exception as e:
            err_msg = f"Failed to fetch recent emails: {e}"
            logger.error(err_msg)
            return "I'm sorry, I encountered an error connecting to your inbox."
