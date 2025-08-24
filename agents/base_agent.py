from abc import ABC, abstractmethod
from pydantic import BaseModel
from typing import Optional, List, Dict, Any
from utils.model_providers import ModelProvider

class BaseAgent(ABC):
    def __init__(self, name: str, instructions: str, model_provider: ModelProvider, 
                 output_type: Optional[BaseModel] = None, tools: Optional[List] = None):
        self.name = name
        self.instructions = instructions
        self.model_provider = model_provider
        self.output_type = output_type
        self.tools = tools or []
    
    @abstractmethod
    async def run(self, input_text: str) -> Any:
        pass
    
    def _format_tools_for_prompt(self) -> str:
        if not self.tools:
            return ""
        
        tools_description = "Available tools:\n"
        for tool in self.tools:
            tools_description += f"- {tool.__name__}: {tool.__doc__}\n"
        return tools_description