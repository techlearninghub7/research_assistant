from pydantic import BaseModel, Field
from utils.model_providers import GeminiProvider

class WebSearchItem(BaseModel):
    reason: str = Field(description="Your reasoning for why this search is important to the query.")
    query: str = Field(description="The search term to use for the web search.")

class WebSearchPlan(BaseModel):
    searches: list[WebSearchItem] = Field(description="A list of web searches to perform to best answer the query.")

class PlannerAgent:
    def __init__(self, model_provider):
        self.model_provider = model_provider
        self.how_many_searches = 5
        
        self.instructions = (
            f"You are a helpful research assistant. Given a query, come up with a set of web searches "
            f"to perform to best answer the query. Output {self.how_many_searches} terms to query for. "
            f"Return the results as a JSON object with a 'searches' array containing objects with 'reason' and 'query' fields."
        )

    async def run(self, query: str) -> WebSearchPlan:
        prompt = f"Query: {query}\n\nPlease create a search plan with {self.how_many_searches} search queries in JSON format."
        
        response = await self.model_provider.generate_content(
            prompt=prompt,
            system_prompt=self.instructions
        )
        
        # Parse the response to create search items
        searches = self._parse_response(response)
        
        # If we couldn't parse enough searches, create default ones
        if len(searches) < self.how_many_searches:
            searches = self._create_default_searches(query)
        
        return WebSearchPlan(searches=searches[:self.how_many_searches])
    
    def _parse_response(self, response: str) -> list:
        """Parse the AI response to extract search items"""
        searches = []
        
        # Try to find JSON-like structure
        import json
        import re
        
        # Look for JSON pattern
        json_match = re.search(r'\{.*\}', response, re.DOTALL)
        if json_match:
            try:
                data = json.loads(json_match.group())
                if 'searches' in data and isinstance(data['searches'], list):
                    for item in data['searches']:
                        if 'query' in item and 'reason' in item:
                            searches.append(WebSearchItem(
                                reason=item['reason'],
                                query=item['query']
                            ))
            except json.JSONDecodeError:
                pass
        
        # If no JSON found, try to parse line by line
        if not searches:
            lines = response.split('\n')
            for line in lines:
                if ':' in line and ('search' in line.lower() or 'query' in line.lower()):
                    parts = line.split(':', 1)
                    if len(parts) == 2:
                        query = parts[1].strip()
                        reason = f"Researching {query} to answer the main query"
                        searches.append(WebSearchItem(reason=reason, query=query))
        
        return searches
    
    def _create_default_searches(self, query: str) -> list:
        """Create default search items if parsing fails"""
        return [
            WebSearchItem(reason="General research on the topic", query=query),
            WebSearchItem(reason="Recent developments", query=f"recent {query}"),
            WebSearchItem(reason="Key concepts", query=f"key concepts of {query}"),
            WebSearchItem(reason="Applications", query=f"applications of {query}"),
            WebSearchItem(reason="Future trends", query=f"future trends in {query}"),
        ]