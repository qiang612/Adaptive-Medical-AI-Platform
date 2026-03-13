from fastapi import FastAPI, UploadFile, File, Form
from fastapi.middleware.cors import CORSMiddleware
from app.api.v1 import api_router
from app.core.config import settings
from app.core.database import engine, SessionLocal
from app.core.celery_app import celery
# 🔥 关键：导入模型的 Base（已包含所有6张表的定义）
from app.models import Base
from fastapi.staticfiles import StaticFiles
import os
from app.models.patient import Patient
# ===================== 核心建表逻辑（修正后） =====================
# 强制创建所有表（检测到模型并在 medical_ai_db 中生成）
# checkfirst=True：避免重复创建，已存在则跳过
Base.metadata.create_all(bind=engine, checkfirst=True)
print("✅ 数据库表检查完成：已自动创建缺失的表")

# ===================== 自动创建默认账号 =====================
from app.models import User, UserRole
from app.core.hashing import get_password_hash
from datetime import datetime
from sqlalchemy.exc import SQLAlchemyError
from app.models.teaching_case import TeachingCase

db = SessionLocal()
try:
    # 1. 检查并创建管理员
    admin = db.query(User).filter(User.username == "admin").first()
    if not admin:
        new_admin = User(
            username="admin",
            password=get_password_hash("admin123"),  # 修改为前端提示的密码
            full_name="系统管理员",
            role=UserRole.ADMIN,
            is_active=True,
            create_time=datetime.now(),
            update_time=datetime.now()
        )
        db.add(new_admin)
        print("✅ 管理员账号创建成功：admin/admin123")

    # 2. 检查并创建测试医生
    doctor = db.query(User).filter(User.username == "doctor").first()
    if not doctor:
        new_doctor = User(
            username="doctor",
            password=get_password_hash("doctor123"),  # 修改为前端提示的密码
            full_name="李医生",
            department="放射科",
            role=UserRole.DOCTOR,
            is_active=True,
            create_time=datetime.now(),
            update_time=datetime.now()
        )
        db.add(new_doctor)
        print("✅ 医生账号创建成功：doctor/doctor123")

    teaching_case_count = db.query(TeachingCase).count()
    if teaching_case_count == 0:
        mock_cases = [
            TeachingCase(
                title="典型右上肺周围型肺癌伴胸膜牵拉",
                disease_type="肺结节",
                case_type="典型病例",
                difficulty="入门",
                description="患者男，65岁，长期吸烟史。体检发现右上肺结节。CT显示右肺上叶尖后段可见一大小约2.5cm×2.0cm的不规则分叶状实性结节。",
                findings=["分叶征阳性", "长短毛刺征", "胸膜凹陷征", "内部可见空泡征"],
                view_count=120, star_count=45
            ),
            TeachingCase(
                title="复杂冠脉多支病变伴严重钙化",
                disease_type="冠心病",
                case_type="疑难病例",
                difficulty="高级",
                description="患者女，72岁，反复胸闷胸痛3年，加重1周。既往有高血压、糖尿病史。冠脉CTA显示前降支、回旋支及右冠状动脉多发弥漫性混合斑块及重度钙化。",
                findings=["LAD近中段重度狭窄(>80%)", "LCX可见多发斑块", "RCA弥漫性重度钙化", "管腔严重变形"],
                view_count=350, star_count=128
            ),
            TeachingCase(
                title="早期宫颈病变(CIN II)的阴道镜下表现",
                disease_type="宫颈癌",
                case_type="典型病例",
                difficulty="进阶",
                description="患者女，35岁，TCT提示ASC-US，HPV 16阳性。阴道镜下醋酸试验可见致密白色上皮，边缘锐利。",
                findings=["醋白上皮厚且致密", "可见镶嵌及点状血管", "碘试验不着色区域明显"],
                view_count=210, star_count=89
            ),
            TeachingCase(
                title="糖尿病视网膜病变增殖期(PDR)典型改变",
                disease_type="眼底病变",
                case_type="典型病例",
                difficulty="进阶",
                description="患者男，58岁，糖尿病病史15年，血糖控制不佳。近期出现双眼视力下降。眼底镜检查及荧光造影(FFA)可见大量新生血管及出血。",
                findings=["视网膜大量微血管瘤及出血", "视盘可见新生血管", "黄斑区硬性渗出及水肿", "可见增殖性纤维条索"],
                view_count=185, star_count=66
            ),
            TeachingCase(
                title="极微小肺原位腺癌(AIS)误诊分析",
                disease_type="肺结节",
                case_type="误诊病例",
                difficulty="高级",
                description="患者女，45岁，体检发现右肺下叶一5mm纯磨玻璃结节(pGGN)。初诊考虑炎性结节，随访1年后结节增大并出现实性成分，术后病理为AIS。",
                findings=["初始表现为纯磨玻璃结节", "随访过程中体积轻度增大", "出现微小实性成分", "血管集束征早期表现"],
                view_count=420, star_count=156
            ),
            TeachingCase(
                title="罕见心肌桥致重度冠脉狭窄一例",
                disease_type="冠心病",
                case_type="罕见病例",
                difficulty="进阶",
                description="患者男，28岁，运动后突发剧烈胸痛。冠脉造影及CTA发现前降支中段存在深层心肌桥，收缩期管腔受压几乎闭塞。",
                findings=["LAD中段走行于心肌内", "收缩期管腔狭窄达90%以上", "舒张期管腔恢复正常",
                          "桥前段未见动脉粥样硬化"],
                view_count=280, star_count=112
            ),
            TeachingCase(
                title="高血压视网膜病变与糖尿病合并",
                disease_type="眼底病变",
                case_type="疑难病例",
                difficulty="高级",
                description="患者男，62岁，高血压合并糖尿病多年。眼底表现同时具有两种疾病的特征，需进行细致鉴别与综合评估。",
                findings=["动脉变细且反光增强", "动静脉交叉压迫征(AV征)", "可见微血管瘤与点片状出血", "棉絮斑散在分布"],
                view_count=190, star_count=74
            ),
            TeachingCase(
                title="宫颈微小浸润癌(IA1期)早期识别",
                disease_type="宫颈癌",
                case_type="疑难病例",
                difficulty="高级",
                description="患者女，42岁，常规筛查异常。阴道镜下病变范围较小且不典型，活检及LEEP刀锥切后深层病理切片才明确诊断为微小浸润。",
                findings=["非典型血管增生", "醋白上皮消退缓慢", "病变深入隐窝", "边界不规则"],
                view_count=310, star_count=95
            ),
            TeachingCase(
                title="典型糖尿病足下肢血管病变评估",
                disease_type="糖尿病",
                case_type="典型病例",
                difficulty="入门",
                description="患者男，68岁，糖尿病史20年，右足破溃不愈合1月。下肢动脉CTA显示双下肢多发血管狭窄及闭塞。",
                findings=["胫前/胫后动脉多发节段性狭窄", "管壁可见广泛轨道样钙化", "足背动脉闭塞无显影",
                          "侧支循环形成不良"],
                view_count=150, star_count=52
            ),
            TeachingCase(
                title="多发散在实性肺结节伴纵隔淋巴结肿大",
                disease_type="肺结节",
                case_type="典型病例",
                difficulty="进阶",
                description="患者男，55岁，偶发阵发性干咳。胸部高分辨率CT(HRCT)显示双肺多发大小不等的实性结节，且伴有隆突下淋巴结肿大，需与肺转移瘤进行鉴别。",
                findings=["双肺多发大小不等实性结节", "边缘光整伴轻微叶裂", "隆突下淋巴结肿大（短径>1.5cm）",
                          "增强扫描呈中等度强化"],
                view_count=230, star_count=78
            ),
            TeachingCase(
                title="宫颈内膜腺癌早期漏诊分析",
                disease_type="宫颈癌",
                case_type="误诊病例",
                difficulty="高级",
                description="患者女，48岁，不规则阴道流血半年。多次TCT检查未见异常，宫颈外观光滑。后经宫颈管搔刮术(ECC)及深部组织活检确诊为宫颈内膜腺癌。",
                findings=["宫颈表面光滑无糜烂", "颈管内可见暗红色突起", "细胞学检查呈假阴性",
                          "深部活检提示腺体结构异常"],
                view_count=450, star_count=192
            ),
            TeachingCase(
                title="右冠状动脉(RCA)近段局限性重度狭窄",
                disease_type="冠心病",
                case_type="典型病例",
                difficulty="入门",
                description="患者男，45岁，劳累后心绞痛1个月。冠脉造影(CAG)明确显示右冠状动脉主干近段存在明显的局限性狭窄，远端血流代偿良好。",
                findings=["RCA近段可见非钙化偏心性斑块", "管腔狭窄程度约85%", "远端血流TIMI 3级",
                          "未见明显侧支循环形成"],
                view_count=320, star_count=105
            ),
            TeachingCase(
                title="糖尿病肾病合并严重感染性休克",
                disease_type="糖尿病",
                case_type="疑难病例",
                difficulty="高级",
                description="患者女，65岁，2型糖尿病25年，近期合并泌尿系统严重感染导致休克。超声显示双肾具有典型的糖尿病肾病晚期形态学改变。",
                findings=["尿蛋白(+++)且持续存在", "eGFR显著下降 (<30 ml/min)", "双肾体积轻度增大且皮质变薄",
                          "肾实质回声弥漫性增强"],
                view_count=275, star_count=110
            ),
            TeachingCase(
                title="非典型糖尿病性视乳头病变(DP)",
                disease_type="眼底病变",
                case_type="罕见病例",
                difficulty="高级",
                description="患者男，32岁，1型糖尿病史。突发单眼视力轻度下降伴视野生理盲点扩大。眼底检查发现视盘水肿，易与视神经炎混淆。",
                findings=["视盘充血水肿且边界不清", "视盘周围浅层可见线状出血", "黄斑区轻度继发性水肿",
                          "FFA早期视盘表面毛细血管扩张渗漏"],
                view_count=390, star_count=145
            ),
            TeachingCase(
                title="肺部隐球菌感染类似恶性肿瘤空洞",
                disease_type="肺结节",
                case_type="罕见病例",
                difficulty="高级",
                description="患者男，38岁，免疫力低下人群。CT偶然发现右肺下叶厚壁空洞性结节，形态极似鳞癌。经皮肺穿刺活检最终证实为隐球菌感染。",
                findings=["右肺下叶厚壁空洞性结节", "内壁欠光滑且伴有液性暗区", "周围可见晕征(Halo sign)",
                          "抗炎治疗2周后结节无明显缩小"],
                view_count=410, star_count=168
            ),
            TeachingCase(
                title="急性重症心肌炎心电图改变误诊为STEMI",
                disease_type="冠心病",
                case_type="误诊病例",
                difficulty="进阶",
                description="患者男，22岁，发热伴剧烈胸痛入院。心电图提示广泛前壁ST段抬高，初步诊断为急性心肌梗死。急诊冠脉造影正常，最终确诊为重症爆发性心肌炎。",
                findings=["广泛导联ST段呈弓背向下抬高", "冠脉造影未见明显狭窄及血栓", "心肌酶谱呈非典型持续升高演变",
                          "心脏超声示室壁弥漫性运动减弱"],
                view_count=520, star_count=210
            ),
            TeachingCase(
                title="晚期宫颈外生型鳞癌伴阴道穹窿侵犯",
                disease_type="宫颈癌",
                case_type="典型病例",
                difficulty="入门",
                description="患者女，60岁，绝经后阴道排液伴恶臭。妇科检查及盆腔MRI提示宫颈巨大外生型肿块，已侵犯阴道穹窿及上1/3阴道壁。",
                findings=["宫颈区呈菜花状巨大低信号肿物", "触之极易出血且质地脆硬", "阴道穹窿消失，上1/3受侵犯",
                          "宫旁组织条索状及结节状增粗"],
                view_count=180, star_count=65
            ),
            TeachingCase(
                title="高血压性视网膜分支静脉阻塞(BRVO)误诊",
                disease_type="眼底病变",
                case_type="误诊病例",
                difficulty="进阶",
                description="患者女，58岁，高血压病史10年。右眼眼前黑影飘动伴视力下降。初诊时因出血量较少被误诊为单纯的轻度背景性糖尿病视网膜病变。",
                findings=["颞上支静脉旁可见火焰状出血", "动静脉交叉处静脉受压呈笔尖状狭窄",
                          "受累血管供应区视网膜灰白水肿", "可见散在棉絮斑(软性渗出)"],
                view_count=260, star_count=88
            ),
            TeachingCase(
                title="初发T2DM伴高渗高血糖综合征(HHS)倾向",
                disease_type="糖尿病",
                case_type="典型病例",
                difficulty="入门",
                description="患者男，70岁，极度口渴、多饮多尿伴意识模糊就诊。既往无明确糖尿病史。实验室检查提示血糖极高且伴有严重的脱水征象。",
                findings=["血糖极度升高(>33.3mmol/L)", "血浆有效渗透压显著增高(>320mOsm/kg)", "尿酮体呈弱阳性或阴性",
                          "伴有严重的皮肤弹性差等脱水体征"],
                view_count=145, star_count=50
            ),
            TeachingCase(
                title="伴有爆米花样钙化的典型肺错构瘤",
                disease_type="肺结节",
                case_type="疑难病例",
                difficulty="进阶",
                description="患者女，42岁，常规体检发现左肺结节。该结节虽然体积较大，但具有非常典型的良性影像学特征，AI平台与医生一致评估为良性错构瘤可能大。",
                findings=["左肺上叶孤立性边缘极度光滑结节", "结节内部可见典型的爆米花样粗大钙化",
                          "含有明确的脂肪密度影(CT值为负数)", "增强扫描结节实质无明显强化"],
                view_count=340, star_count=125
            )

        ]
        db.add_all(mock_cases)
        print("✅ 演示教学案例数据插入成功")

    db.commit()
except SQLAlchemyError as e:
    print(f"❌ 账号创建失败：{str(e)}")
    db.rollback()
finally:
    db.close()

# ===================== 其余 FastAPI 配置（保留） =====================


app = FastAPI(
    title="医疗AI模型接入平台",
    description="仅支持医生+管理员的多模型异步推理平台",
    version="1.0.0"
)
app.mount("/uploads", StaticFiles(directory=settings.UPLOAD_DIR), name="uploads")
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(api_router)

@app.get("/")
def root():
    return {"message": f"医疗AI模型接入平台服务已启动（数据库：medical_ai_platform）"}

# 上传测试接口（保留）
@app.post("/upload-test")
async def upload_test(files: list[UploadFile] = File(...)):
    os.makedirs(settings.UPLOAD_DIR, exist_ok=True)
    saved_files = []
    for file in files:
        file_path = os.path.join(settings.UPLOAD_DIR, file.filename)
        with open(file_path, "wb") as f:
            f.write(await file.read())
        saved_files.append(file_path)
    return {"message": f"成功上传 {len(files)} 个文件", "files": saved_files}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=True
    )