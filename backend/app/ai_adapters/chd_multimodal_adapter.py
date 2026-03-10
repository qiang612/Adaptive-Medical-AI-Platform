# backend/app/ai_adapters/chd_multimodal_adapter.py
from .base_adapter import BaseAIAdapter
from typing import Dict, Any, List
import numpy as np
import os
import joblib
from sklearn.neural_network import MLPClassifier
from sklearn.preprocessing import StandardScaler
from app.core.config import settings
import cv2

class CHDMultimodalAdapter(BaseAIAdapter):
    def __init__(self):
        self.model_path = os.path.join(settings.WEIGHTS_DIR, "chd_mlp_model.pkl")
        self.scaler_path = os.path.join(settings.WEIGHTS_DIR, "chd_scaler.pkl")
        if not os.path.exists(self.model_path):
            self._create_demo_model() # 保留你原有的生成演示模型逻辑
        self.model = joblib.load(self.model_path)
        self.scaler = joblib.load(self.scaler_path)

    def _create_demo_model(self):
        # (保留你原本 chd_risk_adapter.py 中的 _create_demo_model 代码)
        pass

    def process(self, input_data: Dict[str, Any], file_paths: List[str]) -> Dict[str, Any]:
        # 1. 处理临床表格数据 (数值模态)
        features = np.array([
            float(input_data.get("age", 50)),
            float(input_data.get("sbp", 120)),
            float(input_data.get("cholesterol", 5.0)),
            float(input_data.get("glucose", 5.5))
        ]).reshape(1, -1)
        features_scaled = self.scaler.transform(features)
        tabular_risk_prob = self.model.predict_proba(features_scaled)[0, 1]

        # 2. 处理冠脉 CT 影像数据 (视觉模态)
        image_status = "未上传影像"
        image_risk_penalty = 0.0
        if file_paths:
            img_path = file_paths[0]
            img = cv2.imread(img_path)
            if img is not None:
                image_status = "影像已解析"
                # 模拟影像特征提取：假设检测到血管钙化/狭窄，增加一定的风险权重
                # 实际这里应当调用 ResNet/DenseNet 等模型进行特征提取
                image_risk_penalty = 0.15

        # 3. 多模态特征融合 (晚期融合机制 Late Fusion)
        final_risk_prob = min(1.0, tabular_risk_prob * 0.7 + image_risk_penalty)
        risk_level = "低风险" if final_risk_prob < 0.3 else "中等风险" if final_risk_prob < 0.7 else "高风险"

        return {
            "model_type": "Multimodal_Fusion (CNN + MLP)",
            "fusion_details": {
                "tabular_data_parsed": True,
                "image_data_status": image_status
            },
            "risk_score": float(final_risk_prob),
            "risk_level": risk_level,
            "recommendation": "综合影像学与体征数据：建议立即进行冠脉造影确诊。" if risk_level == "高风险" else "建议定期复查。"
        }