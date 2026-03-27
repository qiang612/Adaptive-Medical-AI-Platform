from fastapi import Request
from sqlalchemy.orm import Session
from datetime import datetime
from typing import Optional

from app.models.login_log import LoginLog
from app.models.operation_log import OperationLog, OperationType, UserRole as OpUserRole


def get_client_ip(request: Request) -> str:
    forwarded = request.headers.get("X-Forwarded-For")
    if forwarded:
        return forwarded.split(",")[0].strip()
    return request.client.host if request.client else "unknown"


def create_login_log(
    db: Session,
    username: str,
    full_name: str,
    role: str,
    ip_address: str,
    user_agent: str,
    status: str,
    fail_reason: str = None
) -> LoginLog:
    log = LoginLog(
        username=username,
        full_name=full_name,
        role=role,
        ip_address=ip_address,
        user_agent=user_agent,
        location="",
        status=status,
        fail_reason=fail_reason,
        login_time=datetime.now()
    )
    db.add(log)
    db.commit()
    return log


def create_operation_log(
    db: Session,
    operator_id: int,
    operator_role: str,
    operation_type: OperationType,
    operation_content: str,
    ip_address: str,
    success: bool = True,
    error_msg: str = None
) -> OperationLog:
    log = OperationLog(
        operator_id=operator_id,
        operator_role=OpUserRole.ADMIN if operator_role == "admin" else OpUserRole.DOCTOR,
        operation_type=operation_type,
        operation_content=operation_content,
        ip_address=ip_address,
        success=success,
        error_msg=error_msg,
        operation_time=datetime.now()
    )
    db.add(log)
    db.commit()
    return log


class LogManager:
    def __init__(self, db: Session, request: Request = None):
        self.db = db
        self.request = request
        self.ip_address = get_client_ip(request) if request else "unknown"
    
    def log_login(self, username: str, full_name: str, role: str, 
                  user_agent: str, status: str, fail_reason: str = None) -> LoginLog:
        return create_login_log(
            db=self.db,
            username=username,
            full_name=full_name,
            role=role,
            ip_address=self.ip_address,
            user_agent=user_agent,
            status=status,
            fail_reason=fail_reason
        )
    
    def log_operation(self, operator_id: int, operator_role: str,
                      operation_type: OperationType, operation_content: str,
                      success: bool = True, error_msg: str = None) -> OperationLog:
        return create_operation_log(
            db=self.db,
            operator_id=operator_id,
            operator_role=operator_role,
            operation_type=operation_type,
            operation_content=operation_content,
            ip_address=self.ip_address,
            success=success,
            error_msg=error_msg
        )
