# backend/app/services/email_service.py
import os
# Import the Emails class from the resend library
from resend import Emails

class EmailService:
    def __init__(self):
        # In a real application, initialize Resend client with actual API key
        # self.resend_client = Emails(api_key=os.getenv("RESEND_API_KEY"))
        self.resend_client = None # Mock client for now

    async def send_verification_email(self, recipient_email: str, verification_link: str):
        print(f"Simulating sending verification email to {recipient_email}")
        print(f"Verification Link: {verification_link}")
        
        if self.resend_client:
            try:
                r = self.resend_client.emails.send({
                    "from": "onboarding@resend.dev",
                    "to": recipient_email,
                    "subject": "Verify your email for The AI Helping Tool",
                    "html": f"<p>Click the link to verify your email: <a href='{verification_link}'>{verification_link}</a></p>"
                })
                print(r)
            except Exception as e:
                print(f"Error sending email: {e}")
                raise # Re-raise to indicate failure
        else:
            print("Resend client is not initialized (API key missing or mocked). Simulating email send.")

        # Simulate success
        return {"id": "mock_email_id_123"}

email_service = EmailService()
