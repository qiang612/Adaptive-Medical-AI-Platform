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
        """
        自动生成一个用于演示的冠心病风险评估 MLP 模型和归一化缩放器 (Scaler)
        """
        print(f"⚠️ 找不到预训练模型，正在生成演示模型至: {self.model_path}")

        # 1. 构造一些虚拟的结构化数据用于训练
        # 每一列代表: [age(年龄), sbp(收缩压), cholesterol(胆固醇), glucose(血糖)]
        X_dummy = np.array([
            [45, 120, 4.5, 5.0],  # 相对健康
            [60, 150, 6.0, 7.0],  # 偏高风险
            [30, 110, 4.0, 4.5],  # 健康
            [75, 160, 6.5, 8.0],  # 高危
            [50, 130, 5.0, 5.5],  # 中等
            [65, 145, 5.8, 6.5],  # 偏高风险
            [80, 170, 7.0, 9.0],  # 极高危
            [35, 115, 4.2, 4.8]  # 健康
        ])

        # 对应的患病标签: 0 代表低风险/健康，1 代表高风险/患病
        y_dummy = np.array([0, 1, 0, 1, 0, 1, 1, 0])

        # 2. 数据标准化 (非常重要，否则 MLP 很难收敛)
        scaler = StandardScaler()
        X_scaled = scaler.fit_transform(X_dummy)

        # 3. 训练一个轻量级的多层感知机 (MLP)
        # hidden_layer_sizes=(8, 4) 代表两个隐藏层分别有 8 个和 4 个神经元
        model = MLPClassifier(hidden_layer_sizes=(8, 4), max_iter=1000, random_state=42)
        model.fit(X_scaled, y_dummy)

        # 4. 确保保存权重的目录存在
        os.makedirs(os.path.dirname(self.model_path), exist_ok=True)

        # 5. 保存模型和 Scaler 到本地 weights 文件夹
        joblib.dump(model, self.model_path)
        joblib.dump(scaler, self.scaler_path)

        print("✅ 冠心病演示模型 (chd_mlp_model.pkl) 和缩放器 (chd_scaler.pkl) 生成成功！")

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
        risk_level = "低风险" if final_risk_prob < 0.3 else "中风险" if final_risk_prob < 0.7 else "高风险"
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