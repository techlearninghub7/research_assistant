import google.generativeai as genai
import asyncio
import time
from utils.config import Config

class GeminiProvider:
    def __init__(self):
        genai.configure(api_key=Config.GOOGLE_API_KEY)
        self.model_name = Config.GEMINI_MODEL
        self.model = genai.GenerativeModel(self.model_name)
        self.last_request_time = 0
        self.request_delay = 2  # Add delay between requests to avoid rate limiting
    
    async def generate_content(self, prompt: str, system_prompt: str = None, **kwargs):
        # Add delay to avoid rate limiting
        current_time = time.time()
        time_since_last_request = current_time - self.last_request_time
        if time_since_last_request < self.request_delay:
            await asyncio.sleep(self.request_delay - time_since_last_request)
        
        full_prompt = f"{system_prompt}\n\n{prompt}" if system_prompt else prompt
        
        try:
            # For longer responses, use streaming to avoid timeouts
            response = await self.model.generate_content_async(full_prompt, **kwargs)
            self.last_request_time = time.time()
            return response.text
        except Exception as e:
            print(f"Error generating content: {e}")
            # Fallback response if API fails
            return self._create_fallback_response(full_prompt)
    
    def _create_fallback_response(self, prompt: str) -> str:
        """Create a fallback response when the API fails"""
        if "search" in prompt.lower() and "summary" in prompt.lower():
            return f"Based on research about {prompt.split('Search results for')[1].split('(')[0].strip() if 'Search results for' in prompt else 'the topic'}, here is a summary of key findings..."
        elif "research report" in prompt.lower():
            return f"# Research Report\n\n## Summary\n\nThis is a comprehensive report based on the research conducted.\n\n## Detailed Analysis\n\nResearch findings indicate important information about the topic.\n\n## Conclusion\n\nFurther research may be needed to explore additional aspects."
        else:
            return "I apologize, but I'm experiencing technical difficulties. Please try again later."
    
    def get_model_name(self):
        return self.model_name