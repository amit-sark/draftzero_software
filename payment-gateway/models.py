from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

db = SQLAlchemy()

class Payment(db.Model):
    __tablename__ = 'payments'
    
    id = db.Column(db.Integer, primary_key=True)
    order_id = db.Column(db.String(100), unique=True, nullable=False)
    payment_id = db.Column(db.String(100), unique=True)
    amount = db.Column(db.Float, nullable=False)
    currency = db.Column(db.String(10), default='INR')
    status = db.Column(db.String(50), default='created')
    customer_email = db.Column(db.String(100))
    razorpay_signature = db.Column(db.String(255))
    licence_uuid = db.Column(db.String(255))  # Add this field to store license
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    def to_dict(self):
        return {
            'id': self.id,
            'order_id': self.order_id,
            'payment_id': self.payment_id,
            'amount': self.amount,
            'currency': self.currency,
            'status': self.status,
            'customer_email': self.customer_email,
            'licence_uuid': self.licence_uuid,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }