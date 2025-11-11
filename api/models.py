# models.py
from sqlalchemy import Column, Integer, String, TIMESTAMP, Boolean, DateTime,Float,func
from datetime import datetime, timedelta
from database import Base   # ✅ use the shared Base
import uuid

class Registration(Base):
    __tablename__ = "users"

    sl = Column(Integer, primary_key=True, index=True)
    username = Column(String(100), nullable=False)
    email = Column(String(150), nullable=False, unique=True)
    mobile = Column(String(50), nullable=False)
    timestamp = Column(TIMESTAMP, default=datetime.now)
    free_trial_active = Column(Boolean, default=True)
    free_trial_start = Column(DateTime, default=datetime.now)
    free_trial_end = Column(DateTime, default=lambda: datetime.now() + timedelta(days=30))


class updateCheck(Base):
    __tablename__ = "update"

    id = Column(Integer, primary_key=True, index=True)
    version = Column(Float, nullable=False)
    executable_link = Column(String(1000))


class Feedback(Base):
    __tablename__ = "feedback"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), nullable=False)
    timestamp = Column(TIMESTAMP, default=datetime.now)
    email = Column(String(150), nullable=False)
    feedback = Column(String(10000), nullable=False)

class OTP(Base):
    __tablename__ = "otps"
    id = Column(Integer, primary_key=True, index=True)
    email = Column(String(255), nullable=False, index=True)
    otp = Column(String(10), nullable=False)
    verified = Column(Boolean, default=False)  # NEW COLUMN
    created_at = Column(TIMESTAMP, server_default=func.now())

class Activation(Base):
    __tablename__ = "activation"

    id = Column(Integer, primary_key=True, index=True)
    uuid = Column(String(36), unique=True, index=True, default=lambda: str(uuid.uuid4()))
    expiry_date = Column(DateTime, default=lambda: datetime.now() + timedelta(days=28))
    already_active = Column(Boolean, default=False)
    created_at = Column(DateTime, server_default=func.now())


class UserCostingLogs(Base):
    __tablename__ = "logs"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String(100))
    email = Column(String(150))
    model = Column(String(100))
    input_token = Column(Integer)
    output_token = Column(Integer)
    total_token = Column(Integer)
    input_cost_inr = Column(Float)
    output_cost_inr = Column(Float)
    total_cost_inr = Column(Float)
    timestamp = Column(TIMESTAMP, default=datetime.now)

