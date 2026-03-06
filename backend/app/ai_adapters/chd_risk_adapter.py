from .base_adapter import BaseAIAdapter
from typing import Dict, Any, List
import numpy as np
import os
import joblib
from sklearn.neural_network import MLPClassifier
from sklearn.preprocessing import StandardScaler
from app.core.config import settings


class CHDRiskAdapter(BaseAIAdapter):
    def __init__(self):
        self.model_path = os.path.join(settings.WEIGHTS_DIR, "chd_mlp_model.pkl")
        self.scaler_path = os.path.join(settings.WEIGHTS_DIR, "chd_scaler.pkl")

        # 如果模型不存在，创建一个示例模型（实际应使用真实数据训练）
        if not os.path.exists(self.model_path) or not os.path.exists(self.scaler_path):
            self._create_demo_model()

        # 加载模型和标准化器
        self.model = joblib.load(self.model_path)
        self.scaler = joblib.load(self.scaler_path)

    def _create_demo_model(self):
        """创建一个示例模型用于演示（实际项目中删除此方法，使用真实训练）"""
        # 生成模拟数据
        np.random.seed(42)
        X = np.random.rand(1000, 4) * [100, 200, 10, 20] + [20, 80, 3, 3]
        y = (X[:, 0] > 50).astype(int)  # 简单规则

        # 标准化
        scaler = StandardScaler()
        X_scaled = scaler.fit_transform(X)

        # 训练MLP
        model = MLPClassifier(hidden_layer_sizes=(64, 32), max_iter=500, random_state=42)
        model.fit(X_scaled, y)

        # 保存
        os.makedirs(settings.WEIGHTS_DIR, exist_ok=True)
        joblib.dump(model, self.model_path)
        joblib.dump(scaler, self.scaler_path)

    def process(self, input_data: Dict[str, Any], file_paths: List[str]) -> Dict[str, Any]:
        # 提取特征
        features = np.array([
            input_data.get("age", 50),
            input_data.get("sbp", 120),
            input_data.get("cholesterol", 5.0),
            input_data.get("glucose", 5.5)
        ]).reshape(1, -1)

        # 标准化
        features_scaled = self.scaler.transform(features)

        # 预测
        risk_prob = self.model.predict_proba(features_scaled)[0, 1]
        risk_level = "低风险" if risk_prob < 0.3 else "中风险" if risk_prob < 0.7 else "高风险"

        # 简单的特征权重（SHAP值更好，这里简化）
        feature_weights = {
            "年龄": 0.25 + (features[0, 0] - 50) * 0.01,
            "收缩压": 0.35 + (features[0, 1] - 120) * 0.005,
            "胆固醇": 0.2 + (features[0, 2] - 5) * 0.1,
            "血糖": 0.2 + (features[0, 3] - 5.5) * 0.08
        }

        # 归一化权重
        total = sum(feature_weights.values())
        feature_weights = {k: v / total for k, v in feature_weights.items()}

        recommendations = []
        if risk_level != "低风险":
            if features[0, 1] > 140: recommendations.append("建议控制血压，低盐饮食")
            if features[0, 2] > 6.2: recommendations.append("胆固醇偏高，建议减少动物脂肪摄入")
            if features[0, 3] > 7.0: recommendations.append("血糖偏高，建议控制碳水化合物摄入")
        if not recommendations:
            recommendations.append("各项指标良好，建议保持健康生活方式")

        return {
            "model_type": "MLP",
            "input_features": input_data,
            "risk_score": float(risk_prob),
            "risk_level": risk_level,
            "feature_weights": feature_weights,
            "recommendation": "；".join(recommendations)
        }