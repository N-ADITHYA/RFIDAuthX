from sqlalchemy import Column, Integer, String, ForeignKey, DateTime, Boolean
from sqlalchemy.orm import relationship
from datetime import datetime
from database import Base

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String, nullable=False)
    rfid_uid = Column(String, nullable=False, unique=True)
    mobile_number = Column(String, nullable=False, unique=True)

    logs = relationship("AccessLog", back_populates="user")


class AccessLog(Base):
    __tablename__ = "access_logs"

    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    rfid_uid = Column(String, nullable=True)
    is_active = Column(Boolean, nullable=False)
    logging_time = Column(DateTime, nullable=False, default=datetime.utcnow)

    user = relationship("User", back_populates="logs")