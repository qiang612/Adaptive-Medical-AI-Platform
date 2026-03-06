from .base_adapter import BaseAIAdapter
from typing import Dict, Any, List
from ultralytics import YOLO
import cv2
import os
import uuid
from app.core.config import settings


class YoloCervicalAdapter(BaseAIAdapter):
    def __init__(self):
        # 加载真实的YOLOv8模型
        model_path = os.path.join(settings.WEIGHTS_DIR, "yolov8n.pt")
        if not os.path.exists(model_path):
            raise FileNotFoundError(f"模型权重未找到: {model_path}，请下载并放入weights目录")
        self.model = YOLO(model_path)
        # 类别映射（COCO数据集，实际医疗模型需替换为自己的类别）
        self.class_names = self.model.names

    def process(self, input_data: Dict[str, Any], file_paths: List[str]) -> Dict[str, Any]:
        if not file_paths:
            return {"error": "未上传影像文件"}

        image_path = file_paths[0]
        # 执行推理
        results = self.model(image_path)

        detections = []
        annotated_image_path = None

        for result in results:
            # 提取检测框
            for box in result.boxes:
                x1, y1, x2, y2 = box.xyxy[0].cpu().numpy().astype(int)
                conf = float(box.conf[0].cpu().numpy())
                cls_id = int(box.cls[0].cpu().numpy())
                class_name = self.class_names[cls_id]

                # 只保留置信度>0.5的检测
                if conf > 0.5:
                    detections.append({
                        "class": class_name,
                        "confidence": conf,
                        "bbox": [int(x1), int(y1), int(x2), int(y2)]
                    })

            # 生成标注图像
            if detections:
                annotated_img = result.plot()  # YOLO自带的标注绘制
                annotated_filename = f"annotated_{uuid.uuid4().hex}.jpg"
                annotated_image_path = os.path.join(settings.UPLOAD_DIR, "images", annotated_filename)
                cv2.imwrite(annotated_image_path, annotated_img)

        return {
            "model_type": "YOLOv8",
            "original_image": image_path,
            "annotated_image": annotated_image_path,
            "detections": detections,
            "total_detections": len(detections)
        }