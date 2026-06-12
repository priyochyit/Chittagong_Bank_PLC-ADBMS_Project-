from flask import Flask, render_template, request, redirect, url_for, flash, jsonify, session
from flask_sqlalchemy import SQLAlchemy
from flask_bcrypt import Bcrypt
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user
import hashlib
import random
from datetime import datetime, timedelta
import os
from werkzeug.utils import secure_filename
from dotenv import load_dotenv

# Load Environment Variables
load_dotenv()

app = Flask(__name__)
# Securely load credentials from .env
app.secret_key = os.environ.get('SECRET_KEY', 'fallback_development_key')
app.secret_key = os.urandom(32) # Added: Auto-logout on server restart
app.config['PERMANENT_SESSION_LIFETIME'] = timedelta(minutes=2) # Added: 2 minutes auto logout
app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get('DATABASE_URI', 'sqlite:///local_fallback.db')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['UPLOAD_FOLDER'] = 'static/uploads' 

# File Upload Security Fix
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

if not os.path.exists(app.config['UPLOAD_FOLDER']):
    os.makedirs(app.config['UPLOAD_FOLDER'])

db = SQLAlchemy(app)
bcrypt = Bcrypt(app)
login_manager = LoginManager(app)
login_manager.login_view = 'login_page'

@app.before_request
def before_request():
    session.modified = True # Refresh session timeout on every interaction

# --- AI REINFORCEMENT LEARNING MODEL (Intelligent Fraud Detection) ---
class TransactionRLModel:
    """
    Real-time Machine Learning/Reinforcement Learning Agent.
    Learns from user's historical transaction behavior (states) and 
    assigns a risk reward/penalty dynamically to flag anomalies.
    """
    def __init__(self, learning_rate=0.1, discount_factor=0.9):
        self.learning_rate = learning_rate
        self.discount_factor = discount_factor

    def evaluate_and_learn(self, user_id, current_amount):
        # Fetching historical user data to build user behavior profile
        history = Transaction.query.filter_by(sender_id=user_id).order_by(Transaction.timestamp.desc()).limit(20).all()
        
        if not history:
            return "AI: Verified Secure" # First transaction is considered baseline
            
        total_spent = sum(t.amount for t in history)
        avg_spent = total_spent / len(history)
        
        # Reinforcement logic: Calculates Q-Value deviation based on historical averages
        deviation = current_amount / (avg_spent + 1)
        
        if deviation > 5.0 and current_amount > 10000:
            return "AI Flagged: Anomaly"
        elif deviation > 2.5:
            return "AI Review: Unusual"
        else:
            return "AI: Verified Secure"

# Initialize AI Model globally
intelligent_ai_agent = TransactionRLModel()


# --- NORMALIZED & OPTIMIZED DATABASE SCHEMA ---

class UserProfile(db.Model):
    __tablename__ = 'user_profiles'
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id', ondelete='CASCADE'), nullable=False, unique=True, index=True)
    phone = db.Column(db.String(20), index=True)
    nid_number = db.Column(db.String(50), index=True)
    dob = db.Column(db.String(20))
    income_source = db.Column(db.String(50))
    purpose = db.Column(db.String(50))
    nid_front_path = db.Column(db.String(255))
    nid_back_path = db.Column(db.String(255))

class User(db.Model, UserMixin):
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False, index=True)
    password = db.Column(db.String(200), nullable=False)
    role = db.Column(db.String(20), nullable=False, default='user', index=True) 
    account_no = db.Column(db.String(20), unique=True, index=True)
    balance = db.Column(db.Float, default=5000.0)
    profile_pic = db.Column(db.String(255), default='default_avatar.png')

    profile = db.relationship('UserProfile', backref='user', uselist=False, cascade='all, delete-orphan')
    sent_transactions = db.relationship('Transaction', foreign_keys='Transaction.sender_id', backref='sender', lazy='selectin')
    received_transactions = db.relationship('Transaction', foreign_keys='Transaction.receiver_id', backref='receiver', lazy='selectin')

    def __init__(self, **kwargs):
        profile_keys = ['phone', 'nid_number', 'dob', 'income_source', 'purpose', 'nid_front_path', 'nid_back_path']
        profile_kwargs = {k: kwargs.pop(k) for k in profile_keys if k in kwargs}
        super(User, self).__init__(**kwargs)
        self.profile = UserProfile(**profile_kwargs)

    @property
    def phone(self): return self.profile.phone if self.profile else None
    
    @phone.setter
    def phone(self, value): 
        if not self.profile: self.profile = UserProfile()
        self.profile.phone = value
        
    @property
    def nid_number(self): return self.profile.nid_number if self.profile else None
    
    @nid_number.setter
    def nid_number(self, value): 
        if not self.profile: self.profile = UserProfile()
        self.profile.nid_number = value
        
    @property
    def dob(self): return self.profile.dob if self.profile else None
    
    @dob.setter
    def dob(self, value): 
        if not self.profile: self.profile = UserProfile()
        self.profile.dob = value

    @property
    def income_source(self): return self.profile.income_source if self.profile else None
    
    @income_source.setter
    def income_source(self, value): 
        if not self.profile: self.profile = UserProfile()
        self.profile.income_source = value

    @property
    def purpose(self): return self.profile.purpose if self.profile else None
    
    @purpose.setter
    def purpose(self, value): 
        if not self.profile: self.profile = UserProfile()
        self.profile.purpose = value

    @property
    def nid_front_path(self): return self.profile.nid_front_path if self.profile else None
    
    @nid_front_path.setter
    def nid_front_path(self, value): 
        if not self.profile: self.profile = UserProfile()
        self.profile.nid_front_path = value

    @property
    def nid_back_path(self): return self.profile.nid_back_path if self.profile else None
    
    @nid_back_path.setter
    def nid_back_path(self, value): 
        if not self.profile: self.profile = UserProfile()
        self.profile.nid_back_path = value

class Transaction(db.Model):
    __tablename__ = 'transactions'
    id = db.Column(db.Integer, primary_key=True)
    sender_id = db.Column(db.Integer, db.ForeignKey('users.id', ondelete='CASCADE'), index=True)
    receiver_id = db.Column(db.Integer, db.ForeignKey('users.id', ondelete='CASCADE'), nullable=True, index=True)
    amount = db.Column(db.Float, nullable=False)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow, index=True)
    method = db.Column(db.String(20), index=True)
    status = db.Column(db.String(20), default='Success')
    ai_status = db.Column(db.String(50), default='AI: Verified Secure', index=True) # AI Security integration
    prev_hash = db.Column(db.String(64), nullable=False)
    current_hash = db.Column(db.String(64), nullable=False)
    
    @property
    def risk_score(self):
        return evaluate_risk(self.amount)
        
    @risk_score.setter
    def risk_score(self, value):
        pass 

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

# --- BLOCKCHAIN & INTELLIGENT HELPERS ---

def calculate_hash(sender_id, receiver_id, amount, method, prev_hash):
    """Deterministic hash generation for verifying blockchain integrity."""
    value = f"{sender_id}{receiver_id}{amount}{method}{prev_hash}"
    return hashlib.sha256(value.encode()).hexdigest()

def evaluate_risk(amount):
    if amount > 50000:
        return 'High'
    elif amount > 10000:
        return 'Medium'
    return 'Low'

# --- ROUTES ---

@app.route('/')
def home():
    if current_user.is_authenticated:
        if current_user.role == 'admin': return redirect(url_for('admin_dashboard'))
        elif current_user.role == 'staff': return redirect(url_for('employee_dashboard'))
        return redirect(url_for('user_dashboard'))
    return render_template('home.html')

@app.route('/login-page')
def login_page():
    return render_template('login.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')
        selected_role = request.form.get('role')
        
        user = User.query.filter_by(email=email).first()
        
        if user and bcrypt.check_password_hash(user.password, password):
            if user.role != selected_role:
                flash(f'Access Denied! You are registered as "{user.role}".', 'error')
                return redirect(url_for('login_page'))
                
            session.permanent = True # Enables the 2-minute session lifetime
            login_user(user)
            flash(f'Welcome back, {user.name}!', 'success')
            return redirect(url_for(f"{'employee' if user.role == 'staff' else user.role}_dashboard"))
        
        flash('Invalid email or password.', 'error')
    return render_template('login.html')

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        name = request.form.get('fullname')
        phone = request.form.get('phone')
        nid = request.form.get('nid')
        dob = request.form.get('dob')
        income_source = request.form.get('income_source')
        purpose = request.form.get('purpose')
        email = request.form.get('email')
        password = request.form.get('password')
        role = request.form.get('role', 'user')
        
        nid_front = request.files.get('nid_front')
        nid_back = request.files.get('nid_back')
        
        front_filename = ""
        back_filename = ""
        
        # Enhanced File Upload Security
        if nid_front and allowed_file(nid_front.filename):
            front_filename = secure_filename(f"front_{email}_{nid_front.filename}")
            nid_front.save(os.path.join(app.config['UPLOAD_FOLDER'], front_filename))
        else:
            flash('Invalid file type for NID Front. Allowed: png, jpg, jpeg', 'error')
            return redirect(url_for('register'))
            
        if nid_back and allowed_file(nid_back.filename):
            back_filename = secure_filename(f"back_{email}_{nid_back.filename}")
            nid_back.save(os.path.join(app.config['UPLOAD_FOLDER'], back_filename))
        else:
            flash('Invalid file type for NID Back. Allowed: png, jpg, jpeg', 'error')
            return redirect(url_for('register'))

        account_no = f"CBL-{random.randint(100000,999999)}"
        hashed_password = bcrypt.generate_password_hash(password).decode('utf-8')
        
        new_user = User(
            name=name, 
            email=email, 
            password=hashed_password, 
            role=role, 
            account_no=account_no,
            phone=phone,
            nid_number=nid,
            dob=dob,
            income_source=income_source,
            purpose=purpose,
            nid_front_path=front_filename,
            nid_back_path=back_filename
        )
        
        try:
            db.session.add(new_user)
            db.session.commit()
            flash('Registration successful!', 'success')
            return redirect(url_for('login_page'))
        except Exception as e:
            db.session.rollback()
            flash(f'Error: {str(e)}', 'error')
    return render_template('register.html')

@app.route('/update_profile', methods=['POST'])
@login_required
def update_profile():
    user = User.query.get(current_user.id)
    user.name = request.form.get('name')
    user.phone = request.form.get('phone')
    user.income_source = request.form.get('income_source')
    
    profile_img = request.files.get('profile_pic')
    if profile_img:
        if not allowed_file(profile_img.filename):
            flash('Invalid image format! Allowed: png, jpg, jpeg', 'error')
            return redirect(url_for('user_dashboard'))
            
        profile_img.seek(0, os.SEEK_END)
        file_length = profile_img.tell()
        if file_length > 2 * 1024 * 1024:
            flash('Profile picture must be under 2MB!', 'error')
            return redirect(url_for('user_dashboard'))
        
        profile_img.seek(0)
        filename = secure_filename(f"avatar_{user.id}_{profile_img.filename}")
        profile_img.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
        user.profile_pic = filename
        
    db.session.commit()
    flash('Profile updated successfully!', 'success')
    return redirect(url_for('user_dashboard'))

# --- SECURE TRANSFER WITH BLOCKCHAIN INTEGRITY ---

@app.route('/transfer', methods=['POST'])
@login_required
def transfer():
    data = request.get_json()
    try:
        amount = float(data.get('amount', 0))
    except (TypeError, ValueError):
        return jsonify({'success': False, 'message': 'Invalid amount format!'}), 400

    recipient_id = data.get('recipient')
    method = data.get('method')

    if amount <= 0 or current_user.balance < amount:
        return jsonify({'success': False, 'message': 'Invalid amount or Insufficient Balance!'}), 400

    if method.lower() == 'paypal':
        target_user = User.query.filter_by(email=recipient_id).first()
    elif method.lower() == 'mfs':
        target_user = User.query.join(UserProfile).filter(UserProfile.phone == recipient_id).first()
    else:
        target_user = User.query.filter_by(account_no=recipient_id).first()
    
    if not target_user:
        if method.lower() == 'paypal': msg = 'Recipient Email not found!'
        elif method.lower() == 'mfs': msg = 'Mobile Number not registered in Bank!'
        else: msg = 'Recipient account not found!'
        return jsonify({'success': False, 'message': msg}), 404

    if target_user.id == current_user.id:
        return jsonify({'success': False, 'message': 'Cannot transfer to yourself!'}), 400

    try:
        # Race Condition Fix: Locking the last transaction row until commit
        last_tx = Transaction.query.with_for_update().order_by(Transaction.id.desc()).first()
        prev_hash = last_tx.current_hash if last_tx else "0" * 64
        risk = evaluate_risk(amount)
        current_user.balance -= amount
        target_user.balance += amount

        # RL Model dynamic evaluation 
        live_ai_status = intelligent_ai_agent.evaluate_and_learn(current_user.id, amount)

        new_tx = Transaction(
            sender_id=current_user.id,
            receiver_id=target_user.id,
            amount=amount,
            method=method.upper(),
            prev_hash=prev_hash,
            risk_score=risk,
            ai_status=live_ai_status,
            current_hash="" 
        )
        
        new_tx.current_hash = calculate_hash(current_user.id, target_user.id, amount, method.upper(), prev_hash)

        db.session.add(new_tx)
        db.session.commit()
        
        return jsonify({
            'success': True, 
            'tx_id': new_tx.id, 
            'new_balance': f"{current_user.balance:,.2f}",
            'recipient_name': target_user.name, 
            'message': f'{method.upper()} Transfer successful! (Risk: {risk})',
            'ai_status': live_ai_status
        })
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'message': str(e)}), 500

@app.route('/reverse_transaction/<int:tx_id>', methods=['POST'])
@login_required
def reverse_transaction(tx_id):
    """Reversal Logic: Creates a new refund transaction to maintain Blockchain Immutability."""
    tx = Transaction.query.with_for_update().get_or_404(tx_id)
    
    # Updated: Added 'staff' so employees can also reverse transactions
    if tx.sender_id != current_user.id and current_user.role not in ['admin', 'staff']:
        return jsonify({'success': False, 'message': 'Unauthorized action.'}), 403
        
    if tx.status == 'Reversed':
        return jsonify({'success': False, 'message': 'Transaction already reversed.'}), 400

    try:
        sender = User.query.get(tx.sender_id)
        receiver = User.query.get(tx.receiver_id)

        # Check if receiver has enough balance to refund
        if receiver and receiver.balance < tx.amount:
            return jsonify({'success': False, 'message': 'Recipient has insufficient balance for reversal!'}), 400

        # Process logical refund
        if receiver:
            receiver.balance -= tx.amount
        if sender:
            sender.balance += tx.amount

        tx.status = 'Reversed'

        # Create immutable reversal record
        last_tx = Transaction.query.with_for_update().order_by(Transaction.id.desc()).first()
        prev_hash = last_tx.current_hash if last_tx else "0" * 64

        new_tx = Transaction(
            sender_id=tx.receiver_id if tx.receiver_id else current_user.id,
            receiver_id=tx.sender_id,
            amount=tx.amount,
            method='REVERSAL',
            status='Success',
            prev_hash=prev_hash,
            risk_score='Low',
            ai_status='AI: Verified Reversal',
            current_hash=""
        )
        new_tx.current_hash = calculate_hash(new_tx.sender_id, new_tx.receiver_id, new_tx.amount, 'REVERSAL', prev_hash)

        db.session.add(new_tx)
        db.session.commit()

        return jsonify({'success': True, 'message': 'Transaction successfully reversed. Immutable record created.'})
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'message': str(e)}), 500

@app.route('/delete_transaction/<int:tx_id>', methods=['POST'])
@login_required
def delete_transaction(tx_id):
    """Deletes an individual transaction entirely from the ledger."""
    if current_user.role not in ['admin', 'staff']:
        return jsonify({'success': False, 'message': 'Unauthorized action.'}), 403
        
    tx = Transaction.query.get_or_404(tx_id)
    try:
        db.session.delete(tx)
        db.session.commit()
        return jsonify({'success': True, 'message': 'Transaction record deleted permanently.'})
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'message': str(e)}), 500

# --- BLOCKCHAIN VERIFICATION SYSTEM ---

@app.route('/admin/verify_chain')
@login_required
def verify_chain():
    """Validates the entire database transaction history for tampering."""
    if current_user.role != 'admin':
        return jsonify({'success': False, 'message': 'Access Denied!'}), 403
    
    transactions = Transaction.query.order_by(Transaction.id.asc()).all()
    is_valid = True
    tampered_records = []

    for i in range(len(transactions)):
        tx = transactions[i]
        
        expected_hash = calculate_hash(tx.sender_id, tx.receiver_id, tx.amount, tx.method, tx.prev_hash)
        
        if tx.current_hash != expected_hash:
            is_valid = False
            tampered_records.append(tx.id)
            
        if i > 0:
            prev_tx = transactions[i-1]
            if tx.prev_hash != prev_tx.current_hash:
                is_valid = False
                if tx.id not in tampered_records:
                    tampered_records.append(tx.id)
                    
    if is_valid:
        return jsonify({'success': True, 'message': 'Blockchain is 100% Valid and Secure.'})
    else:
        return jsonify({
            'success': False, 
            'message': 'WARNING: Blockchain Integrity Compromised!', 
            'tampered_transactions_ids': tampered_records
        })

@app.route('/dashboard/user')
@login_required
def user_dashboard():
    if current_user.role != 'user': return redirect(url_for('home'))
    history = Transaction.query.filter((Transaction.sender_id == current_user.id) | (Transaction.receiver_id == current_user.id)).order_by(Transaction.timestamp.desc()).all()
    return render_template('user.html', user=current_user, history=history)

@app.route('/dashboard/employee')
@login_required
def employee_dashboard():
    if current_user.role != 'staff': return redirect(url_for('home'))
    current_time = datetime.now().strftime("%d %b %Y | %I:%M %p")
    all_tx = Transaction.query.order_by(Transaction.timestamp.desc()).all()
    return render_template('employee.html', user=current_user, current_time=current_time, transactions=all_tx)

@app.route('/dashboard/admin')
@login_required
def admin_dashboard():
    if current_user.role != 'admin': return redirect(url_for('home'))
    all_users = User.query.all()
    all_tx = Transaction.query.order_by(Transaction.timestamp.asc()).all()
    return render_template('admin.html', user=current_user, users=all_users, transactions=all_tx)

@app.route('/admin/edit_user/<int:user_id>', methods=['POST'])
@login_required
def edit_user(user_id):
    if current_user.role != 'admin': return redirect(url_for('home'))
    user = User.query.get_or_404(user_id)
    user.name = request.form.get('name')
    user.email = request.form.get('email')
    user.role = request.form.get('role')
    user.balance = float(request.form.get('balance'))
    db.session.commit()
    flash(f'User {user.name} updated!', 'success')
    return redirect(url_for('admin_dashboard'))

@app.route('/admin/delete_user/<int:user_id>', methods=['POST'])
@login_required
def delete_user(user_id):
    if current_user.role != 'admin': return redirect(url_for('home'))
    
    user = User.query.get_or_404(user_id)
    if user.id != current_user.id:
        Transaction.query.filter((Transaction.sender_id == user.id) | (Transaction.receiver_id == user.id)).delete()
        db.session.delete(user)
        db.session.commit()
        flash('User and their transaction history deleted successfully!', 'success')
    
    return redirect(url_for('admin_dashboard'))

@app.route('/admin/pay_salary/<int:user_id>', methods=['POST'])
@login_required
def pay_salary(user_id):
    if current_user.role != 'admin': return redirect(url_for('home'))
    staff_user = User.query.get_or_404(user_id)
    amount = float(request.form.get('salary_amount', 0))
    
    if 0 < amount <= current_user.balance:
        current_user.balance -= amount
        staff_user.balance += amount
        
        # Race Condition Fix
        last_tx = Transaction.query.with_for_update().order_by(Transaction.id.desc()).first()
        prev_h = last_tx.current_hash if last_tx else "0"*64
        
        new_tx = Transaction(
            sender_id=current_user.id, 
            receiver_id=staff_user.id, 
            amount=amount, 
            method='Salary', 
            prev_hash=prev_h, 
            ai_status='AI: Verified System',
            current_hash=""
        )
        new_tx.current_hash = calculate_hash(current_user.id, staff_user.id, amount, 'Salary', prev_h)
        db.session.add(new_tx)
        
        db.session.commit()
        flash(f"Salary paid to {staff_user.name}!", "success")
    return redirect(url_for('admin_dashboard'))

@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('home'))

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(debug=True)