# backend/init_data.py
"""
数据库初始化脚本 - 独立于应用启动流程

使用方式:
    python init_data.py

说明:
    该脚本用于初始化默认账号和演示数据，应在应用首次部署时执行一次。
    与 init_models.py 配合使用，后者负责初始化 AI 模型注册数据。
"""
import sys
import os

sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app.core.database import SessionLocal
from app.models import User, UserRole
from app.models.operation_log import OperationLog, OperationType, UserRole as OpUserRole
from app.models.login_log import LoginLog
from app.core.hashing import get_password_hash
from datetime import datetime, timedelta
from sqlalchemy.exc import SQLAlchemyError


def init_default_users(db):
    """初始化默认用户账号"""
    admin = None
    doctor = None

    admin = db.query(User).filter(User.username == "admin").first()
    if not admin:
        new_admin = User(
            username="admin",
            password=get_password_hash("admin123"),
            full_name="系统管理员",
            role=UserRole.ADMIN,
            is_active=True,
            create_time=datetime.now(),
            update_time=datetime.now()
        )
        db.add(new_admin)
        db.flush()
        admin = new_admin
        print("✅ 管理员账号创建成功：admin/admin123")
    else:
        print("⏭️ 管理员账号已存在，跳过创建")

    doctor = db.query(User).filter(User.username == "doctor").first()
    if not doctor:
        new_doctor = User(
            username="doctor",
            password=get_password_hash("doctor123"),
            full_name="李医生",
            department="放射科",
            role=UserRole.DOCTOR,
            is_active=True,
            create_time=datetime.now(),
            update_time=datetime.now()
        )
        db.add(new_doctor)
        db.flush()
        doctor = new_doctor
        print("✅ 医生账号创建成功：doctor/doctor123")
    else:
        print("⏭️ 医生账号已存在，跳过创建")

    return admin, doctor


def init_operation_logs(db, admin, doctor):
    """初始化演示操作日志"""
    if db.query(OperationLog).count() > 0:
        print("⏭️ 操作日志数据已存在，跳过创建")
        return

    if not admin or not doctor:
        print("⚠️ 缺少用户数据，跳过操作日志初始化")
        return

    mock_op_logs = [
        OperationLog(
            operator_id=admin.id,
            operator_role=OpUserRole.ADMIN,
            operation_type=OperationType.MODEL_REGISTER,
            operation_content="注册了新模型 [肺结节检测 v2.0]",
            ip_address="192.168.1.100",
            success=True,
            operation_time=datetime.now() - timedelta(days=1)
        ),
        OperationLog(
            operator_id=admin.id,
            operator_role=OpUserRole.ADMIN,
            operation_type=OperationType.USER_CREATE,
            operation_content="创建了新医生账号 [王医生]",
            ip_address="192.168.1.100",
            success=True,
            operation_time=datetime.now() - timedelta(hours=12)
        ),
        OperationLog(
            operator_id=doctor.id,
            operator_role=OpUserRole.DOCTOR,
            operation_type=OperationType.TASK_SUBMIT,
            operation_content="提交了新的影像推理任务",
            ip_address="10.0.0.55",
            success=False,
            error_msg="模型服务超时",
            operation_time=datetime.now() - timedelta(hours=2)
        ),
    ]
    db.add_all(mock_op_logs)
    print("✅ 演示【操作日志】数据插入成功")


def init_login_logs(db):
    """初始化演示登录日志"""
    if db.query(LoginLog).count() > 0:
        print("⏭️ 登录日志数据已存在，跳过创建")
        return

    mock_login_logs = [
        LoginLog(
            username="admin",
            full_name="系统管理员",
            role="admin",
            ip_address="192.168.1.100",
            user_agent="Mozilla/5.0 Windows NT 10.0 Chrome/120.0",
            location="北京",
            status="success",
            login_time=datetime.now() - timedelta(days=2)
        ),
        LoginLog(
            username="doctor",
            full_name="李医生",
            role="doctor",
            ip_address="10.0.0.55",
            user_agent="Mozilla/5.0 Mac OS X 10_15_7 Safari/605",
            location="上海",
            status="success",
            login_time=datetime.now() - timedelta(hours=5)
        ),
        LoginLog(
            username="doctor",
            full_name="李医生",
            role="doctor",
            ip_address="10.0.0.55",
            user_agent="Mozilla/5.0 Mac OS X",
            location="上海",
            status="fail",
            fail_reason="密码错误",
            login_time=datetime.now() - timedelta(hours=6)
        ),
    ]
    db.add_all(mock_login_logs)
    print("✅ 演示【登录日志】数据插入成功")


def init_all_data():
    """执行所有初始化逻辑"""
    print("=" * 50)
    print("🚀 开始执行数据库初始化...")
    print("=" * 50)

    db = SessionLocal()
    try:
        print("\n[1/3] 初始化默认用户账号...")
        admin, doctor = init_default_users(db)

        print("\n[2/3] 初始化操作日志...")
        init_operation_logs(db, admin, doctor)

        print("\n[3/3] 初始化登录日志...")
        init_login_logs(db)

        db.commit()
        print("\n" + "=" * 50)
        print("✅ 数据库初始化完成！")
        print("=" * 50)
        print("\n默认账号信息:")
        print("  - 管理员: admin / admin123")
        print("  - 医生:   doctor / doctor123")

    except SQLAlchemyError as e:
        print(f"\n❌ 初始化失败：{str(e)}")
        db.rollback()
        sys.exit(1)
    finally:
        db.close()


if __name__ == "__main__":
    init_all_data()
