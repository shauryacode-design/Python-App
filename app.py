"""
Indian Real Estate Management System - Complete Working Version
Save this as: app.py
Run with: python app.py
"""

print("=" * 60)
print("Indian Real Estate Management System - Starting...")
print("=" * 60)

from flask import Flask, render_template, request, jsonify, redirect, url_for, session
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime
import os
import json
import webbrowser
import threading

app = Flask(__name__)
app.config['SECRET_KEY'] = 'indian-real-estate-secret-key-2024'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///real_estate.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)

print("✓ Flask initialized")
print("✓ Database configured")

# Database Models
class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password = db.Column(db.String(200), nullable=False)
    user_type = db.Column(db.String(20), nullable=False)
    phone = db.Column(db.String(15))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    properties = db.relationship('Property', backref='dealer', lazy=True)

class Property(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text)
    dealer_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    address = db.Column(db.String(300), nullable=False)
    city = db.Column(db.String(100), nullable=False)
    state = db.Column(db.String(100), nullable=False)
    pincode = db.Column(db.String(10))
    latitude = db.Column(db.Float)
    longitude = db.Column(db.Float)
    length = db.Column(db.Float, nullable=False)
    width = db.Column(db.Float, nullable=False)
    area_sqft = db.Column(db.Float, nullable=False)
    area_sqyard = db.Column(db.Float, nullable=False)
    area_sqm = db.Column(db.Float, nullable=False)
    price_per_sqyard = db.Column(db.Float, nullable=False)
    total_price = db.Column(db.Float, nullable=False)
    boundary_type = db.Column(db.String(50))
    water_access = db.Column(db.Boolean, default=False)
    electricity = db.Column(db.Boolean, default=False)
    road_frontage = db.Column(db.Float)
    road_type = db.Column(db.String(50))
    legal_status = db.Column(db.String(100))
    documentation = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    inquiries = db.relationship('Inquiry', backref='property', lazy=True)

class Inquiry(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    property_id = db.Column(db.Integer, db.ForeignKey('property.id'), nullable=False)
    buyer_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    message = db.Column(db.Text, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    buyer = db.relationship('User', backref='inquiries')

print("✓ Database models created")

# Custom filter
@app.template_filter('from_json')
def from_json_filter(value):
    if value:
        try:
            return json.loads(value)
        except:
            return []
    return []

# Routes
@app.route('/')
def home():
    properties = Property.query.order_by(Property.created_at.desc()).all()
    return render_template('home.html', properties=properties)

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        email = request.form['email']
        phone = request.form.get('phone')
        password = request.form['password']
        confirm_password = request.form['confirm_password']
        user_type = request.form['user_type']
        
        if password != confirm_password:
            return render_template('register.html', error='Passwords do not match')
        
        if User.query.filter_by(email=email).first():
            return render_template('register.html', error='Email already registered')
        
        hashed = generate_password_hash(password)
        user = User(username=username, email=email, phone=phone, password=hashed, user_type=user_type)
        db.session.add(user)
        db.session.commit()
        
        return redirect(url_for('login', success='Registration successful'))
    
    # GET request or after processing
    return render_template('register.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    success = request.args.get('success')
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']
        user = User.query.filter_by(email=email).first()
        
        if user and check_password_hash(user.password, password):
            session['user_id'] = user.id
            session['username'] = user.username
            session['user_type'] = user.user_type
            
            if user.user_type == 'dealer':
                return redirect(url_for('dealer_dashboard'))
            else:
                return redirect(url_for('buyer_dashboard'))
        
        return render_template('login.html', error='Invalid credentials')
    
    return render_template('login.html', success=success)

@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('home'))

@app.route('/property/<int:property_id>')
def property_detail(property_id):
    property = Property.query.get_or_404(property_id)
    return render_template('property_detail.html', property=property)

@app.route('/dealer/dashboard')
def dealer_dashboard():
    if 'user_id' not in session or session['user_type'] != 'dealer':
        return redirect(url_for('login'))
    
    properties = Property.query.filter_by(dealer_id=session['user_id']).all()
    inquiries = Inquiry.query.join(Property).filter(Property.dealer_id == session['user_id']).all()
    
    return render_template('dealer_dashboard.html', properties=properties, inquiries=inquiries)

@app.route('/buyer/dashboard')
def buyer_dashboard():
    if 'user_id' not in session or session['user_type'] != 'buyer':
        return redirect(url_for('login'))
    
    inquiries = Inquiry.query.filter_by(buyer_id=session['user_id']).all()
    return render_template('buyer_dashboard.html', inquiries=inquiries)

@app.route('/dealer/add-property', methods=['GET', 'POST'])
def add_property():
    if 'user_id' not in session or session['user_type'] != 'dealer':
        return redirect(url_for('login'))
    
    if request.method == 'POST':
        length = float(request.form['length'])
        width = float(request.form['width'])
        area_sqft = length * width
        area_sqyard = area_sqft / 9
        area_sqm = area_sqft * 0.092903
        price_per_sqyard = float(request.form['price_per_sqyard'])
        total_price = area_sqyard * price_per_sqyard
        
        property = Property(
            title=request.form['title'],
            description=request.form.get('description'),
            dealer_id=session['user_id'],
            address=request.form['address'],
            city=request.form['city'],
            state=request.form['state'],
            pincode=request.form.get('pincode'),
            latitude=float(request.form['latitude']) if request.form.get('latitude') else None,
            longitude=float(request.form['longitude']) if request.form.get('longitude') else None,
            length=length,
            width=width,
            area_sqft=area_sqft,
            area_sqyard=area_sqyard,
            area_sqm=area_sqm,
            price_per_sqyard=price_per_sqyard,
            total_price=total_price,
            boundary_type=request.form.get('boundary_type'),
            water_access='water_access' in request.form,
            electricity='electricity' in request.form,
            road_frontage=float(request.form['road_frontage']) if request.form.get('road_frontage') else None,
            road_type=request.form.get('road_type'),
            legal_status=request.form.get('legal_status'),
            documentation=request.form.get('documentation')
        )
        
        db.session.add(property)
        db.session.commit()
        
        return redirect(url_for('dealer_dashboard'))
    
    return render_template('add_property.html')

@app.route('/api/inquiry', methods=['POST'])
def create_inquiry():
    if 'user_id' not in session or session['user_type'] != 'buyer':
        return jsonify({'success': False, 'error': 'Unauthorized'})
    
    data = request.json
    inquiry = Inquiry(
        property_id=data['property_id'],
        buyer_id=session['user_id'],
        message=data['message']
    )
    db.session.add(inquiry)
    db.session.commit()
    
    return jsonify({'success': True})

# Initialize database
with app.app_context():
    db.create_all()
    print("✓ Database tables created")

print("=" * 60)
print("✓ Application ready!")
print("=" * 60)
print("\nStarting server on http://127.0.0.1:5000")
print("Press CTRL+C to quit\n")

if __name__ == '__main__':
    def open_browser():
        webbrowser.open('http://127.0.0.1:5000')
    
    threading.Timer(1.5, open_browser).start()
    app.run(debug=True, port=5000, use_reloader=False)
