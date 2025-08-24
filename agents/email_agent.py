import os
from typing import Dict
import sendgrid
from sendgrid.helpers.mail import Email, Mail, Content, To
from utils.config import Config
from utils.model_providers import GeminiProvider

class EmailAgent:
    def __init__(self, model_provider):
        self.model_provider = model_provider
        
        self.instructions = (
            "You format research reports for email delivery. Create a clean, well-formatted email "
            "with an appropriate subject line based on the research report. Return a JSON object with "
            "'subject' and 'html_body' fields."
        )

    async def run(self, report: str) -> dict:
        prompt = f"""
        Convert this research report into a well-formatted email with subject and HTML body:
        
        {report}
        """
        
        email_content = await self.model_provider.generate_content(
            prompt=prompt,
            system_prompt=self.instructions
        )
        
        # Parse the response
        subject, html_body = self._parse_email_response(email_content)
        
        # Send email if SendGrid is configured
        if Config.SENDGRID_API_KEY:
            return await self._send_email(subject, html_body)
        else:
            return {
                "status": "success",
                "message": "Email would be sent in production environment",
                "content_preview": f"Subject: {subject}\n\n{html_body[:200]}..."
            }

    def _parse_email_response(self, response: str) -> tuple:
        """Parse the email response to extract subject and body"""
        import json
        import re
        
        # Try to extract JSON from the response
        json_match = re.search(r'\{.*\}', response, re.DOTALL)
        if json_match:
            try:
                data = json.loads(json_match.group())
                return data.get('subject', 'Research Report'), data.get('html_body', response)
            except json.JSONDecodeError:
                pass
        
        # Fallback if JSON parsing fails
        lines = response.split('\n')
        subject = "Research Report"
        body = response
        
        for i, line in enumerate(lines):
            if line.startswith("Subject:") and i == 0:
                subject = line.replace("Subject:", "").strip()
                body = '\n'.join(lines[i+1:])
                break
        
        return subject, f"<html><body><pre>{body}</pre></body></html>"

    async def _send_email(self, subject: str, html_body: str) -> Dict[str, str]:
        """Send an email with the given subject and HTML body"""
        try:
            sg = sendgrid.SendGridAPIClient(api_key=Config.SENDGRID_API_KEY)
            from_email = Email(Config.FROM_EMAIL)
            to_email = To(Config.TO_EMAIL)
            content = Content("text/html", html_body)
            mail = Mail(from_email, to_email, subject, content)
            
            response = sg.client.mail.send.post(request_body=mail.get())
            print(f"Email response: {response.status_code}")
            return {"status": "success", "message": f"Email sent successfully (Status: {response.status_code})"}
        except Exception as e:
            return {"status": "error", "message": f"Failed to send email: {str(e)}"}