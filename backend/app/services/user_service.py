from sqlalchemy.orm import Session
from app.models.user import User
from app.schemas.user import UserCreate, UserUpdate
from app.core.hashing import get_password_hash, verify_password

class UserService:
    def get_user_by_id(self, db: Session, user_id: int):
        return db.query(User).filter(User.id == user_id).first()

    def get_user_by_username(self, db: Session, username: str):
        return db.query(User).filter(User.username == username).first()

    def get_users(self, db: Session, skip: int = 0, limit: int = 100):
        return db.query(User).offset(skip).limit(limit).all()

    def create_user(self, db: Session, user_in: UserCreate):
        db_user = User(
            username=user_in.username,
            password=get_password_hash(user_in.password),
            full_name=user_in.full_name,
            email=user_in.email,
            phone=user_in.phone,
            role=user_in.role,
            department=user_in.department,
            title=user_in.title,
            remark=user_in.remark,
            is_active=user_in.is_active if user_in.is_active is not None else True
        )
        db.add(db_user)
        db.commit()
        db.refresh(db_user)
        return db_user

    def update_user(self, db: Session, db_user: User, user_in: UserUpdate):
        update_data = user_in.model_dump(exclude_unset=True)
        for field, value in update_data.items():
            setattr(db_user, field, value)
        db.commit()
        db.refresh(db_user)
        return db_user

    def authenticate(self, db: Session, username: str, password: str):
        user = self.get_user_by_username(db, username=username)
        if not user:
            return None
        if not verify_password(password, user.password):
            return None
        return user

user_service = UserService()