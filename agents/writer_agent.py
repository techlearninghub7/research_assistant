from pydantic import BaseModel, Field
from utils.model_providers import GeminiProvider

class ReportData(BaseModel):
    short_summary: str = Field(description="A short 2-3 sentence summary of the findings.")
    markdown_report: str = Field(description="The final report")
    follow_up_questions: list[str] = Field(description="Suggested topics to research further")

class WriterAgent:
    def __init__(self, model_provider):
        self.model_provider = model_provider
        
        self.instructions = (
            "You are a senior researcher tasked with writing a cohesive report for a research query. "
            "You will be provided with the original query and research findings.\n"
            "Generate a comprehensive report in markdown format with at least 1000 words. "
            "Return the results as a JSON object with 'short_summary', 'markdown_report', and 'follow_up_questions' fields."
        )

    async def run(self, query: str, search_results: list[str]) -> ReportData:
        research_text = "\n\n".join([f"## Research Finding {i+1}\n{result}" for i, result in enumerate(search_results)])
        
        prompt = f"""
        Original Query: {query}
        
        Research Findings:
        {research_text}
        
        Please create a comprehensive research report with:
        1. A short 2-3 sentence summary
        2. A detailed markdown report (1000+ words)
        3. 3-5 follow-up questions for further research
        
        Return the results in JSON format.
        """
        
        response = await self.model_provider.generate_content(
            prompt=prompt,
            system_prompt=self.instructions
        )
        
        # Parse the response into the required format
        return self._parse_response(response, query)

    def _parse_response(self, response: str, query: str) -> ReportData:
        """Parse the AI response into structured data"""
        import json
        import re
        
        # Try to extract JSON from the response
        json_match = re.search(r'\{.*\}', response, re.DOTALL)
        if json_match:
            try:
                data = json.loads(json_match.group())
                return ReportData(
                    short_summary=data.get('short_summary', f"Summary of research on {query}"),
                    markdown_report=data.get('markdown_report', response),
                    follow_up_questions=data.get('follow_up_questions', [
                        f"What are the latest developments in {query}?",
                        f"How is {query} being applied in industry?",
                        f"What are the future trends in {query}?"
                    ])
                )
            except json.JSONDecodeError:
                pass
        
        # Fallback if JSON parsing fails
        return ReportData(
            short_summary=f"Summary of research on {query}",
            markdown_report=response,
            follow_up_questions=[
                f"What are the latest developments in {query}?",
                f"How is {query} being applied in industry?",
                f"What are the future trends in {query}?"
            ]
        )