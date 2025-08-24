import asyncio
from typing import AsyncGenerator
from utils.config import Config
from utils.model_providers import GeminiProvider
from agents.planner_agent import PlannerAgent, WebSearchPlan
from agents.search_agent import SearchAgent
from agents.writer_agent import WriterAgent, ReportData
from agents.email_agent import EmailAgent

class ResearchManager:
    def __init__(self):
        Config.validate()
        self.model_provider = GeminiProvider()
        
        # Initialize agents
        self.planner_agent = PlannerAgent(self.model_provider)
        self.search_agent = SearchAgent(self.model_provider)
        self.writer_agent = WriterAgent(self.model_provider)
        self.email_agent = EmailAgent(self.model_provider)

    async def run(self, query: str) -> AsyncGenerator[str, None]:
        """Run the deep research process, yielding status updates and the final report"""
        yield f"Starting research with {self.model_provider.get_model_name()}..."
        
        # Plan searches
        yield "Planning search strategy..."
        search_plan = await self.plan_searches(query)
        yield f"Planned {len(search_plan.searches)} searches, starting execution..."
        
        # Perform searches
        search_results = []
        async for status_update in self.perform_searches(search_plan):
            if status_update.startswith("Completed search"):
                yield status_update
            else:
                search_results.append(status_update)
        
        yield "Searches completed, synthesizing report..."
        
        # Write report
        report = await self.write_report(query, search_results)
        yield "Report synthesized, preparing email notification..."
        
        # Send email
        email_result = await self.send_email(report.markdown_report)
        yield f"Email status: {email_result['status']}"
        
        # Yield final report
        yield report.markdown_report

    async def plan_searches(self, query: str) -> WebSearchPlan:
        """Plan the searches to perform for the query"""
        return await self.planner_agent.run(query)

    async def perform_searches(self, search_plan: WebSearchPlan) -> AsyncGenerator[str, None]:
        """Perform the searches for the query"""
        tasks = []
        for item in search_plan.searches:
            input_text = f"Search term: {item.query}\nReason for searching: {item.reason}"
            tasks.append(self.search_agent.run(input_text))
        
        for i, task in enumerate(asyncio.as_completed(tasks)):
            try:
                result = await task
                yield result
                yield f"Completed search {i+1}/{len(tasks)}"
            except Exception as e:
                yield f"Search {i+1} failed: {str(e)}"
                yield f"Completed search {i+1}/{len(tasks)}"

    async def write_report(self, query: str, search_results: list[str]) -> ReportData:
        """Write the report for the query"""
        return await self.writer_agent.run(query, search_results)
    
    async def send_email(self, report: str) -> dict:
        """Send the report via email"""
        return await self.email_agent.run(report)