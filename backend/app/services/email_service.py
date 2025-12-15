# backend/app/services/email_service.py
import os
import resend # Import the top-level resend library

class EmailService:
    def __init__(self):
        self._resend_configured = False
        resend_api_key = os.getenv("RESEND_API_KEY")
        if not resend_api_key:
            print("WARNING: RESEND_API_KEY environment variable is not set. Email service will be disabled.")
            # Do not set resend.api_key if not available
        else:
            resend.api_key = resend_api_key
            self._resend_configured = True
            print("Resend client initialized.")

    async def send_verification_email(self, recipient_email: str, verification_link: str):
        if not self._resend_configured:
            print(f"WARNING: Email service is not configured. Cannot send verification email to {recipient_email}.")
            return {"id": "email_service_disabled"}

        print(f"Sending verification email to {recipient_email}")
        print(f"Verification Link: {verification_link}")
        
        try:
            # Use resend.Emails.send directly now that API key is set globally
            r = resend.Emails.send({
                "from": "onboarding@resend.dev",
                "to": recipient_email,
                "subject": "Verify your email for The AI Helping Tool",
                "html": f"<p>Click the link to verify your email: <a href='{verification_link}'>{verification_link}</a></p>"
            })
            print(r)
        except Exception as e:
            print(f"Error sending email: {e}")
            raise 

        return {"id": r.id} if hasattr(r, 'id') else {"id": "resend_success"}

email_service = EmailService()
