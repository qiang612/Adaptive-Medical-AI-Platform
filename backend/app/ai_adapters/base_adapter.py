from abc import ABC, abstractmethod
from typing import Dict, Any, List


class BaseAIAdapter(ABC):
    @abstractmethod
    def process(self, input_data: Dict[str, Any], file_paths: List[str]) -> Dict[str, Any]:
        """执行核心推理逻辑"""
        pass

    def generate_clinical_advice(self, result_data: Dict[str, Any]) -> str:
        """
        生成临床建议（可被子类重写）
        符合开题报告中多态适配器的设计模式，实现真正的"自适应"建议生成
        """
        return "本次AI分析已完成。该模型暂无定制化的临床建议，请结合患者多模态指标进行综合判断。"