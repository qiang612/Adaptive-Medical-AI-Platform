from abc import ABC, abstractmethod
from typing import Dict, Any, List

class BaseAIAdapter(ABC):
    @abstractmethod
    def process(self, input_data: Dict[str, Any], file_paths: List[str]) -> Dict[str, Any]:
        pass