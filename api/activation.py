from datetime import datetime, timedelta
import uuid
from sqlalchemy.orm import Session
from models import Activation

def create_activation(db: Session):
    new_activation = Activation(
        uuid=str(uuid.uuid4()),
        expiry_date=datetime.utcnow() + timedelta(days=28),
        already_active=False
    )
    db.add(new_activation)
    db.commit()
    db.refresh(new_activation)
    return new_activation


def check_activation(db: Session, uuid_code: str):
    activation = db.query(Activation).filter(Activation.uuid == uuid_code).first()
    if not activation:
        return {"status": "error", "message": "UUID not found"}
    
    if activation.expiry_date < datetime.utcnow():
        return {"status": "expired", "message": "Activation expired"}
    
    if activation.already_active:
        return {"status": "used", "message": "Activation already used"}
    
    # Mark as active
    activation.already_active = True
    db.commit()
    return {
        "status": "success",
        "uuid": activation.uuid,
        "expiry_date": activation.expiry_date
    }

def get_activation_details(db: Session, uuid_code: str):
    activation = db.query(Activation).filter(Activation.uuid == uuid_code).first()
    
    if not activation:
        return {"status": "error", "message": "UUID not found"}
    
    return {
        "status": "success",
        "uuid": activation.uuid,
        "expiry_date": activation.expiry_date,
        "already_active": activation.already_active
    }

