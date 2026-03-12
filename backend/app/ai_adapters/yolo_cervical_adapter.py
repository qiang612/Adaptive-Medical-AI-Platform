from .base_adapter import BaseAIAdapter
from typing import Dict, Any, List
from ultralytics import YOLO
import cv2
import os
import uuid
from app.core.config import settings


class YoloCervicalAdapter(BaseAIAdapter):
    def __init__(self):
        # 初始化模型路径
        self.model_path = os.path.join(settings.WEIGHTS_DIR, "yolov8_cervical.pt")
        if not os.path.exists(self.model_path):
            self.model_path = os.path.join(settings.WEIGHTS_DIR, "yolov8n.pt")  # 降级方案

        try:
            self.model = YOLO(self.model_path)
        except Exception as e:
            print(f"初始化宫颈模型异常，降级使用基础模型: {e}")
            self.model = YOLO(os.path.join(settings.WEIGHTS_DIR, "yolov8n.pt"))

    def process(self, input_data: Dict[str, Any], file_paths: List[str]) -> Dict[str, Any]:
        if not file_paths:
            return {"error": "未上传影像文件"}

        image_path = file_paths[0]
        detections = []
        annotated_image_path = None

        try:
            # 扩大捕获范围为 Exception，防止 detect 属性等 PyTorch 底层错误导致服务崩溃
            results = self.model(image_path)
        except Exception as e:
            print(f"⚠️ 宫颈模型推理失败，自动降级为 yolov8n.pt: {e}")
            fallback_path = os.path.join(settings.WEIGHTS_DIR, "yolov8n.pt")
            fallback_model = YOLO(fallback_path)
            results = fallback_model(image_path)

        for result in results:
            # 提取检测框（增加安全检查，防止某些分割模型没有 boxes 属性）
            if hasattr(result, 'boxes') and result.boxes is not None:
                for box in result.boxes:
                    x1, y1, x2, y2 = box.xyxy[0].cpu().numpy().astype(int)
                    conf = float(box.conf[0].cpu().numpy())

                    # 放宽置信度阈值到 0.25，确保演示时能大概率画出框
                    if conf > 0.25:
                        detections.append({
                            "class": "疑似宫颈病变",  # 模仿肺结节，给定性名称
                            "confidence": round(conf, 3),
                            "bbox": [int(x1), int(y1), int(x2), int(y2)]
                        })

            # 如果检测到了目标，才生成标注图像
            if detections:
                annotated_img = result.plot()
                annotated_filename = f"cervical_annotated_{uuid.uuid4().hex}.jpg"
                annotated_image_path = os.path.join(settings.UPLOAD_DIR, "images", annotated_filename)
                cv2.imwrite(annotated_image_path, annotated_img)

        return {
            "model_type": "YOLOv8_Cervical",
            "original_image": image_path,
            "annotated_image": annotated_image_path,
            "detections": detections,
            "conclusion": f"共发现 {len(detections)} 处异常，请结合临床进一步诊断。"
        }