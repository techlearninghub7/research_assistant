import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    # API Keys
    GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")
    SENDGRID_API_KEY = os.getenv("SENDGRID_API_KEY")
    
    # Email Configuration
    FROM_EMAIL = os.getenv("FROM_EMAIL")
    TO_EMAIL = os.getenv("TO_EMAIL")
    
    # Model Selection
    GEMINI_MODEL = os.getenv("GEMINI_MODEL")
    
    @classmethod
    def validate(cls):
        if not cls.GOOGLE_API_KEY:
            raise ValueError("GOOGLE_API_KEY is required")
        if not cls.SENDGRID_API_KEY:
            print("Warning: SENDGRID_API_KEY not set. Email functionality will be disabled.")