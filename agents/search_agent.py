import aiohttp
import wikipediaapi
from urllib.parse import quote
from utils.model_providers import GeminiProvider

class SearchAgent:
    def __init__(self, model_provider):
        self.model_provider = model_provider
        self.wiki = wikipediaapi.Wikipedia(
            user_agent='ResearchAssistant/1.0 (research@example.com)',
            language='en'
        )
        
        self.instructions = (
            "You are a research assistant. Given a search term, you search the web for that term and "
            "produce a concise summary of the results. The summary must be 2-3 paragraphs and less than 300 "
            "words. Capture the main points. Write succinctly."
        )

    async def run(self, input_text: str) -> str:
        # Extract search term from input
        lines = input_text.split('\n')
        search_term = None
        reason = "General research"
        
        for line in lines:
            if line.startswith('Search term:'):
                search_term = line.replace('Search term:', '').strip()
            elif line.startswith('Reason for searching:'):
                reason = line.replace('Reason for searching:', '').strip()
        
        if not search_term:
            search_term = input_text
        
        # Perform search using Wikipedia and web search
        search_results = await self._perform_search(search_term)
        
        # Generate summary
        if search_results:
            prompt = f"""
            Search results for '{search_term}' (reason: {reason}):
            {search_results}
            
            Please provide a concise 2-3 paragraph summary of these results.
            Focus on the most relevant information for the research purpose.
            """
        else:
            # Fallback if no search results
            prompt = f"""
            Generate a 2-3 paragraph summary about '{search_term}' based on general knowledge.
            The research reason is: {reason}
            """
        
        summary = await self.model_provider.generate_content(
            prompt=prompt,
            system_prompt=self.instructions
        )
        
        return summary

    async def _perform_search(self, query: str) -> str:
        """Perform search using Wikipedia and web search"""
        results = []
        
        try:
            # Try Wikipedia first (most reliable)
            wiki_result = await self._wikipedia_search(query)
            if wiki_result:
                results.append(f"Wikipedia: {wiki_result}")
        except Exception as e:
            print(f"Wikipedia search error: {e}")
        
        try:
            # Try web search as fallback
            web_result = await self._web_search(query)
            if web_result:
                results.append(f"Web Search: {web_result}")
        except Exception as e:
            print(f"Web search error: {e}")
        
        return "\n\n".join(results) if results else ""

    async def _wikipedia_search(self, query: str) -> str:
        """Search Wikipedia for information"""
        try:
            # Try direct page access first
            page = self.wiki.page(query)
            if page.exists():
                summary = page.summary
                return summary[:500] + "..." if len(summary) > 500 else summary
            
            # If direct page doesn't exist, search for pages using Wikipedia API
            search_url = f"https://en.wikipedia.org/w/api.php?action=query&list=search&srsearch={quote(query)}&format=json&srlimit=2"
            
            async with aiohttp.ClientSession() as session:
                async with session.get(search_url) as response:
                    if response.status == 200:
                        data = await response.json()
                        search_results = data.get('query', {}).get('search', [])
                        
                        if search_results:
                            # Get the first result
                            page_title = search_results[0]['title']
                            page = self.wiki.page(page_title)
                            if page.exists():
                                summary = page.summary
                                return summary[:500] + "..." if len(summary) > 500 else summary
                            
                            # If we can't get the page, return the snippet
                            snippet = search_results[0].get('snippet', '')
                            # Clean HTML tags from snippet
                            import re
                            clean_snippet = re.sub('<[^<]+?>', '', snippet)
                            return clean_snippet + "..."
        except Exception as e:
            print(f"Wikipedia API error: {e}")
        
        return ""

    async def _web_search(self, query: str) -> str:
        """Simple web search using Wikipedia API or DuckDuckGo-like service"""
        try:
            # Use Wikipedia search as web search fallback
            search_url = f"https://en.wikipedia.org/w/api.php?action=query&list=search&srsearch={quote(query)}&format=json&srlimit=3"
            
            async with aiohttp.ClientSession() as session:
                async with session.get(search_url) as response:
                    if response.status == 200:
                        data = await response.json()
                        search_results = data.get('query', {}).get('search', [])
                        
                        if search_results:
                            results = []
                            for result in search_results:
                                title = result.get('title', '')
                                snippet = result.get('snippet', '')
                                # Clean HTML tags
                                import re
                                clean_snippet = re.sub('<[^<]+?>', '', snippet)
                                results.append(f"{title}: {clean_snippet}...")
                            
                            return "\n".join(results)
        except Exception as e:
            print(f"Web search error: {e}")
        
        return ""