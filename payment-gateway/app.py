from flask import Flask, request, jsonify, render_template,send_from_directory
from flask_cors import CORS
import razorpay
from models import db, Payment
import hashlib
import hmac
import os 
import requests

app = Flask(__name__)
CORS(app)

# Configuration
#app.config['SQLALCHEMY_DATABASE_URI'] = "mysql+pymysql://root@localhost/wishpen"
app.config['SQLALCHEMY_DATABASE_URI'] = "mysql+pymysql://root@localhost/draftzero"
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SECRET_KEY'] = 'your-secret-key-here'

# Razorpay Configuration
RAZORPAY_KEY_ID = 'rzp_test_RasOSVrTASk9l4'
RAZORPAY_KEY_SECRET = 'DHQ2yt2p1MvjnzYSFMDcF5v9'

db.init_app(app)
razorpay_client = razorpay.Client(auth=(RAZORPAY_KEY_ID, RAZORPAY_KEY_SECRET))

# Create tables
with app.app_context():
    db.create_all()

@app.route('/')
def home():
    return jsonify({
        'message': 'Razorpay Payment Gateway API',
        'endpoints': {
            'create_order': '/create-order (POST)',
            'payment_page': '/payment/<order_id> (GET)',
            'verify_payment': '/verify-payment (POST)',
            'get_payment_status': '/payment-status/<order_id> (GET)'
        }
    })

@app.route('/create-order', methods=['POST'])
def create_order():
    try:
        data = request.get_json()
        amount = float(data.get('amount', 0))
        currency = data.get('currency', 'INR')
        customer_email = data.get('email', '')
        
        # Create Razorpay order
        order_data = {
            'amount': int(amount * 100),
            'currency': currency,
            'payment_capture': 1
        }
        
        razorpay_order = razorpay_client.order.create(data=order_data)
        
        # Save to database
        payment = Payment(
            order_id=razorpay_order['id'],
            amount=amount,
            currency=currency,
            status='created',
            customer_email=customer_email,
        )
        db.session.add(payment)
        db.session.commit()
        
        return jsonify({
            'status': 'success',
            'order_id': razorpay_order['id'],
            'amount': amount,
            'currency': currency,
            'payment_url': f'http://localhost:5000/payment/{razorpay_order["id"]}'
        })
        
    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)}), 400

@app.route('/payment/<order_id>')
def payment_page(order_id):
    payment = Payment.query.filter_by(order_id=order_id).first()
    if not payment:
        return "Payment not found", 404
    
    # Use render_template instead of render_template_string
    return render_template(
        'payment.html',
        order_id=order_id,
        amount=payment.amount,
        key_id=RAZORPAY_KEY_ID
    )

@app.route('/verify-payment', methods=['POST'])
def verify_payment():
    try:
        data = request.get_json()
        order_id = data.get('order_id')
        payment_id = data.get('payment_id')
        signature = data.get('signature')
        
        # Verify signature
        generated_signature = hmac.new(
            RAZORPAY_KEY_SECRET.encode(),
            f"{order_id}|{payment_id}".encode(),
            hashlib.sha256
        ).hexdigest()
        
        if generated_signature == signature:
            # Update payment in database
            payment = Payment.query.filter_by(order_id=order_id).first()
            if payment:
                payment.payment_id = payment_id
                payment.razorpay_signature = signature
                payment.status = 'success'
                
                # Generate license ONLY here when payment is verified successfully
                BASE_URL = 'http://127.0.0.1:8000'
                try:
                    response = requests.post(url=f"{BASE_URL}/create_id")
                    response_data = response.json()
                    licence_uuid = response_data.get('uuid')
                    
                    # Store license in database
                    payment.licence_uuid = licence_uuid
                    
                except Exception as e:
                    print(f"License generation error: {e}")
                    licence_uuid = None
                
                db.session.commit()
                
                return jsonify({
                    'status': 'success',
                    'message': 'Payment verified successfully',
                    'payment': payment.to_dict(),
                    'licence': licence_uuid
                })
        
        return jsonify({'status': 'failed', 'message': 'Invalid signature'}), 400
        
    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)}), 400

@app.route('/payment-status/<order_id>', methods=['GET'])
def payment_status(order_id):
    payment = Payment.query.filter_by(order_id=order_id).first()
    if not payment:
        return jsonify({'status': 'error', 'message': 'Payment not found'}), 404
    
    return jsonify({
        'status': 'success',
        'payment': payment.to_dict()
    })

@app.route('/update-payment-status', methods=['POST'])
def update_payment_status():
    try:
        data = request.get_json()
        order_id = data.get('order_id')
        status = data.get('status')
        
        payment = Payment.query.filter_by(order_id=order_id).first()
        if payment:
            payment.status = status
            db.session.commit()
            return jsonify({'status': 'success'})
        
        return jsonify({'status': 'error', 'message': 'Payment not found'}), 404
    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)}), 400



@app.route('/static/<path:filename>')
def static_files(filename):
    return send_from_directory(os.path.join(app.root_path, 'static'), filename)
if __name__ == '__main__':
    app.run(debug=True, port=5000)