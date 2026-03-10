# backend/app/ai_adapters/lung_nodule_adapter.py
from .base_adapter import BaseAIAdapter
from typing import Dict, Any, List
from ultralytics import YOLO
import cv2
import os
import uuid
from app.core.config import settings


class LungNoduleAdapter(BaseAIAdapter):
    def __init__(self):
        # 加载肺结节专属模型 (如果没有，可暂时用 yolov8n.pt 替代演示)
        model_path = os.path.join(settings.WEIGHTS_DIR, "yolov8_lung.pt")
        if not os.path.exists(model_path):
            model_path = os.path.join(settings.WEIGHTS_DIR, "yolov8n.pt")  # 降级方案
        self.model = YOLO(model_path)

    def process(self, input_data: Dict[str, Any], file_paths: List[str]) -> Dict[str, Any]:
        if not file_paths:
            return {"error": "未上传肺部 CT 影像文件"}

        image_path = file_paths[0]
        results = self.model(image_path)

        detections = []
        annotated_image_path = None

        for result in results:
            for box in result.boxes:
                x1, y1, x2, y2 = box.xyxy[0].cpu().numpy().astype(int)
                conf = float(box.conf[0].cpu().numpy())
                # 强制映射为结节类别用于演示
                if conf > 0.4:
                    detections.append({
                        "class": "疑似肺结节 (Nodule)",
                        "confidence": conf,
                        "bbox": [int(x1), int(y1), int(x2), int(y2)]
                    })

            if detections:
                annotated_img = result.plot()
                annotated_filename = f"lung_result_{uuid.uuid4().hex}.jpg"
                annotated_image_path = os.path.join(settings.UPLOAD_DIR, "images", annotated_filename)
                cv2.imwrite(annotated_image_path, annotated_img)

        return {
            "model_type": "YOLOv8_Detection",
            "original_image": image_path,
            "annotated_image": annotated_image_path,
            "detections": detections,
            "conclusion": f"共发现 {len(detections)} 处疑似结节，请结合临床进一步诊断。"
        }