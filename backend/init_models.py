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

        # 1. 肺结节模型 (单模态)
        model_lung = ModelRegistry(
            model_code="LUNG_NODULE_01",
            model_name="肺结节检测模型 (YOLOv8)",
            model_type="单模态",
            task_type="目标检测",
            model_version="v1.0",
            # 利用 model_path 字段存储适配器反射路径
            model_path="app.ai_adapters.lung_nodule_adapter.LungNoduleAdapter",
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
            # 补充真实的输出协议
            output_schema={
                "type": "object",
                "properties": {
                    "image_result": {"type": "string", "description": "带检测框的结果影像图 (Base64)"},
                    "nodule_count": {"type": "integer", "description": "检测到的结节数量"},
                    "detections": {
                        "type": "array",
                        "description": "结节详细信息列表",
                        "items": {
                            "type": "object",
                            "properties": {
                                "bbox": {"type": "array", "items": {"type": "number"}, "description": "坐标 [x1, y1, x2, y2]"},
                                "confidence": {"type": "number", "description": "置信度"}
                            }
                        }
                    }
                }
            },
            accuracy=0.85,
            description="用于检测CT影像中的疑似肺结节位置",
            is_active=True
        )

        # 2. 宫颈病变模型 (单模态)
        model_cervical = ModelRegistry(
            model_code="CERVICAL_CELL_01",
            model_name="宫颈病变细胞筛查模型",
            model_type="单模态",
            task_type="目标检测",
            model_version="v1.0",
            model_path="app.ai_adapters.yolo_cervical_adapter.YoloCervicalAdapter",
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
            # 补充真实的输出协议
            output_schema={
                "type": "object",
                "properties": {
                    "image_result": {"type": "string", "description": "带检测框的细胞标注图 (Base64)"},
                    "abnormal_count": {"type": "integer", "description": "异常病变细胞数量"},
                    "risk_level": {"type": "string", "description": "整体风险评估等级"}
                }
            },
            accuracy=0.92,
            description="用于识别显微镜影像中的异常宫颈细胞",
            is_active=True
        )

        # 3. 冠心病模型 (多模态：影像 + 体征数值)
        model_chd = ModelRegistry(
            model_code="CHD_MULTI_01",
            model_name="冠心病多模态评估模型",
            model_type="多模态",
            task_type="综合评估",
            model_version="v2.0",
            model_path="app.ai_adapters.chd_multimodal_adapter.CHDMultimodalAdapter",
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
            # 补充真实的输出协议
            output_schema={
                "type": "object",
                "properties": {
                    "risk_score": {"type": "number", "description": "0-1之间的患病概率得分"},
                    "risk_level": {"type": "string", "description": "风险等级: 低风险、中风险、高风险"},
                    "feature_importance": {"type": "object", "description": "各项生理指标对预测结果的贡献度分析"},
                    "clinical_advice": {"type": "string", "description": "AI生成的临床辅助建议"}
                }
            },
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