# backend/init_models.py
import sys
import os

# 将项目根目录添加到 Python 路径中，避免 ModuleNotFoundError
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app.core.database import SessionLocal
from app.models.model_registry import ModelRegistry

def init_ai_models():
    db = SessionLocal()
    try:
        # 先检查是否已经有数据，避免重复插入
        if db.query(ModelRegistry).count() > 0:
            print("⚠️ 数据库中已有模型数据，无需重复初始化。")
            return

        # 1. 肺结节模型 (单模态视觉)
        model_lung = ModelRegistry(
            model_code="LUNG_NODULE_01",
            model_name="肺结节检测模型 (YOLOv8)",
            model_type="单模态视觉",
            task_type="目标检测",
            model_version="v1.0",
            # 利用 model_path 字段存储适配器反射路径
            model_path="app.ai_adapters.lung_nodule_adapter.LungNoduleAdapter",
            # 👇 去掉了 json.dumps，直接使用字典
            input_schema={
                "type": "object",
                "properties": {
                    "file_upload": {
                        "type": "string",
                        "format": "binary",
                        "description": "请上传患者肺部CT切片影像 (.jpg/.png)"
                    }
                }
            },
            output_schema={},  # 必填项，直接给空字典
            accuracy=0.85,
            description="用于检测CT影像中的疑似肺结节位置",
            is_active=True
        )

        # 2. 宫颈病变模型 (单模态视觉)
        model_cervical = ModelRegistry(
            model_code="CERVICAL_CELL_01",
            model_name="宫颈病变细胞筛查模型",
            model_type="单模态视觉",
            task_type="目标检测",
            model_version="v1.0",
            model_path="app.ai_adapters.yolo_cervical_adapter.YoloCervicalAdapter",
            # 👇 去掉了 json.dumps，直接使用字典
            input_schema={
                "type": "object",
                "properties": {
                    "file_upload": {
                        "type": "string",
                        "format": "binary",
                        "description": "请上传显微镜下的宫颈细胞涂片影像"
                    }
                }
            },
            output_schema={}, # 直接给空字典
            accuracy=0.92,
            description="用于识别显微镜影像中的异常宫颈细胞",
            is_active=True
        )

        # 3. 冠心病模型 (多模态：影像 + 体征数值)
        model_chd = ModelRegistry(
            model_code="CHD_MULTI_01",
            model_name="冠心病多模态评估模型",
            model_type="多模态混合",
            task_type="综合评估",
            model_version="v2.0",
            model_path="app.ai_adapters.chd_multimodal_adapter.CHDMultimodalAdapter",
            # 👇 去掉了 json.dumps，直接使用字典
            input_schema={
                "type": "object",
                "properties": {
                    "file_upload": {
                        "type": "string",
                        "format": "binary",
                        "description": "请上传冠脉CT造影影像 (可选)"
                    },
                    "age": {"type": "integer", "title": "患者年龄", "minimum": 0, "maximum": 120},
                    "sbp": {"type": "number", "title": "收缩压 (mmHg)"},
                    "cholesterol": {"type": "number", "title": "总胆固醇 (mmol/L)"},
                    "glucose": {"type": "number", "title": "空腹血糖 (mmol/L)"}
                },
                "required": ["age", "sbp", "cholesterol", "glucose"]
            },
            output_schema={}, # 直接给空字典
            accuracy=0.88,
            description="结合冠脉CT影像与患者体征数据的综合高危风险评估",
            is_active=True
        )

        db.add(model_lung)
        db.add(model_cervical)
        db.add(model_chd)
        db.commit()
        print("✅ 3个AI模型及自适应 Schema 成功写入数据库！")

    except Exception as e:
        db.rollback()
        print(f"❌ 插入失败: {str(e)}")
    finally:
        db.close()

if __name__ == "__main__":
    init_ai_models()