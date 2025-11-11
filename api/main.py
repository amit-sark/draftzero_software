from fastapi import FastAPI, Depends, HTTPException, status, BackgroundTasks
from sqlalchemy.orm import Session
from datetime import datetime, timedelta
from pydantic import BaseModel, EmailStr
import models
from sqlalchemy import or_
import schemas
from database import engine, SessionLocal, Base
from otp_service import generate_otp, send_email, store_otp, verify_otp
from activation import check_activation,create_activation,get_activation_details


Base.metadata.create_all(bind=engine)

app = FastAPI(title="Wish pen API's")

# Dependency

class LoginRequest(BaseModel):
    email: EmailStr
    mobile: str

class EmailRequest(BaseModel):
    email: EmailStr

class VerifyRequest(BaseModel):
    email: EmailStr
    otp: str


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@app.post("/user_check")
def check(user: schemas.UserCreate, db: Session = Depends(get_db)):
    existing_user = db.query(models.Registration).filter(
        models.Registration.email == user.email
    ).first()

    if existing_user:
        return {

            "status":"valid user",
            "detail":"User already registered or free trial already used."
        }
    else:
        return{
            "status":'invalid user',
            "detail":"Please Signup first!"
        }
           
        
@app.post("/signup", response_model=schemas.UserResponse)
def signup(user: schemas.UserCreate, db: Session = Depends(get_db)):
    existing_user = db.query(models.Registration).filter(
        models.Registration.email == user.email
    ).first()

    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="User already registered or free trial already used."
        )

    new_user = models.Registration(
        username=user.username,
        email=user.email,
        mobile=user.mobile,
        free_trial_active=True,
        free_trial_start=datetime.utcnow(),
        free_trial_end=datetime.utcnow() + timedelta(days=60)
    )

    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    return new_user

        
@app.post("/send-otp/")
def send_otp(request: EmailRequest, background_tasks: BackgroundTasks, db: Session = Depends(get_db)):
    otp = generate_otp()
    store_otp(db, request.email, otp)
    background_tasks.add_task(send_email, request.email, otp)
    return {"message": "OTP sent successfully"}

@app.post("/verify-otp/")
def verify(request: VerifyRequest, db: Session = Depends(get_db)):
    if verify_otp(db, request.email, request.otp):
        return {"message": "OTP verified successfully"}
    raise HTTPException(status_code=400, detail="Invalid OTP")

@app.post("/login", response_model=schemas.UserResponse)
def login(request: LoginRequest, db: Session = Depends(get_db)):
    user = db.query(models.Registration).filter(
            models.Registration.email == request.email,
    ).first()

    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="No user found with this email and mobile combination."
        )

    return user


@app.post("/feedback", response_model=schemas.feedbackCreate)
def feedback(user: schemas.feedbackCreate, db: Session = Depends(get_db)):
    new_feedback = models.Feedback(
        name=user.name,
        email=user.email,
        feedback=user.feedback,
    )

    db.add(new_feedback)
    db.commit()
    db.refresh(new_feedback)
    return new_feedback


@app.post("/logs", response_model=schemas.UserCostingLogs)
def userlog(user: schemas.UserCostingLogs, db: Session = Depends(get_db)):
    logs = models.UserCostingLogs(
        username=user.username,
        email=user.email,
        model=user.model,
        input_token=user.input_token,
        output_token = user.output_token,
        total_token= user.total_token,
        input_cost_inr=user.input_cost_inr,
        output_cost_inr=user.output_cost_inr,
        total_cost_inr=user.total_cost_inr,
    )

    db.add(logs)
    db.commit()
    db.refresh(logs)
    return logs



@app.get("/update")
def get_update_info(db: Session = Depends(get_db)):
    data = db.query(models.updateCheck).first() 
    return data



@app.post("/activate")
def activate(uuid: schemas.ActivationKey, db: Session = Depends(get_db)):
    return check_activation(db, uuid_code=uuid.uuid)


@app.post("/create_id")
def createActivation(db: Session=Depends(get_db)):
    return create_activation(db=db)


@app.get("/activation_details/{uuid_code}")
def activation_details(uuid_code: str, db: Session = Depends(get_db)):
    return get_activation_details(db, uuid_code)