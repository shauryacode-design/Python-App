"""
Indian Real Estate Management System - Complete Working Version
Save this as: app.py
Run with: python app.py
"""

print("=" * 60)
print("Indian Real Estate Management System - Starting...")
print("=" * 60)

from flask import Flask, render_template_string, request, jsonify, redirect, url_for, session
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

# HTML Templates
HOME_TEMPLATE = """
<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Indian Real Estate System</title>
    <style>
        @import url('https://fonts.googleapis.com/css2?family=Montserrat:ital,wght@0,100..900;1,100..900&display=swap');
        @import url('https://fonts.googleapis.com/css2?family=Montserrat+Alternates:ital,wght@0,100;0,200;0,300;0,400;0,500;0,600;0,700;0,800;0,900;1,100;1,200;1,300;1,400;1,500;1,600;1,700;1,800;1,900&display=swap');
    * { margin: 0; padding: 0; box-sizing: border-box; }
    body { font-family: "Montserrat", sans-serif; background-color:#f8f6f0 ; min-height: 100vh; color:#432818}
    .navbar {font-family: "Montserrat Alternates", sans-serif; background: white; padding: 1rem 2rem; box-shadow: 0 2px 10px rgba(0,0,0,0.1); display: flex;
    justify-content: space-between; align-items: center; }
    .navbar h1 { color: #432818; }
    .navbar a { margin-left: 2rem; text-decoration: none; color: #333; font-weight: bold;}
    .navbar a:hover { color: #386641; }
    nav{font-family: "Montserrat Alternates", sans-serif;margin-right: 25px;}
    .container { max-width: 1200px; margin: 2rem auto; padding: 0 2rem; }
    .hero { background: white; border-radius: 20px; padding: 3rem; text-align: center; box-shadow: 0 10px 40px
    rgba(0,0,0,0.1); }
    .hero h2 { font-size: 2rem; margin-bottom: 1rem; }
    .btn { background: #386641; color: white; padding: 1rem 2rem; border: none; border-radius: 10px; text-decoration:
    none; display: inline-block; margin: 0.5rem; }
    .btn:hover { opacity: 0.9; }
    .btn-secondary { background: #bc986c; }
    .properties { display: grid; grid-template-columns: repeat(auto-fill, minmax(300px, 1fr)); gap: 2rem; margin-top:
    2rem; }
    .property-card { background: white; border-radius: 15px; padding: 1.5rem; box-shadow: 0 5px 20px rgba(0,0,0,0.1); }
    .property-title { color: #333; font-size: 1.3rem; margin-bottom: 0.5rem; }
    .property-price { color: #432818; font-size: 1.5rem; font-weight: bold; margin: 1rem 0; }
    .user-info { background: white; padding: 1rem; border-radius: 10px; margin-bottom: 1rem; }
    .status { background: white; padding: 2rem; border-radius: 15px; margin-top: 2rem; text-align: center; }
    </style>
</head>
<body>
    <div class="navbar">
        <h1>🏡 Indian Real Estate</h1>
        <nav>
            <a href="/">Home</a>
            {% if session.user_id %}
                {% if session.user_type == 'dealer' %}
                    <a href="/dealer/dashboard">Dashboard</a>
                    <a href="/dealer/add-property">Add Property</a>
                {% else %}
                    <a href="/buyer/dashboard">Dashboard</a>
                {% endif %}
                <a href="/logout">Logout</a>
            {% else %}
                <a href="/login">Login</a>
                <a href="/register">Register</a>
            {% endif %}
        </nav>
    </div>

    <div class="container">
        {% if session.user_id %}
        <div class="user-info">
            <strong>Welcome, {{ session.username }}!</strong> ({{ session.user_type|capitalize }})
        </div>
        {% endif %}

        <div class="hero">
            <h2>Find Your Perfect Plot in India</h2>
            <p style="color: #666; margin: 1rem 0;">Connect with dealers and explore properties with 3D visualization and pricing calculators</p>
            {% if not session.user_id %}
            <a href="/register?type=buyer" class="btn">Get Started as Buyer</a>
            <a href="/register?type=dealer" class="btn btn-secondary">Register as Dealer</a>
            {% endif %}
        </div>

        {% if properties %}
        <h2 style="color: white; margin: 2rem 0 1rem;">Available Properties ({{ properties|length }})</h2>
        <div class="properties">
            {% for property in properties %}
            <div class="property-card">
                <h3 class="property-title">{{ property.title }}</h3>
                <p style="color: #666;">📍 {{ property.city }}, {{ property.state }}</p>
                <div class="property-price">₹{{ "%.2f"|format(property.total_price / 100000) }}L</div>
                <p style="color: #666;">Area: {{ "%.0f"|format(property.area_sqyard) }} sq yd</p>
                <p style="color: #666;">₹{{ "%.0f"|format(property.price_per_sqyard) }}/sq yd</p>
                <a href="/property/{{ property.id }}" class="btn" style="margin-top: 1rem; display: block; text-align: center;">View Details</a>
            </div>
            {% endfor %}
        </div>
        {% else %}
        <div class="status">
            <h3>No Properties Available Yet</h3>
            <p style="color: #666; margin: 1rem 0;">Be the first dealer to list a property!</p>
        </div>
        {% endif %}
    </div>
</body>
</html>
"""

LOGIN_TEMPLATE = """
<!DOCTYPE html>
<html>
<head>
    <title>Login</title>
    <style>
        * { margin: 0; padding: 0; box-sizing: border-box; }
        body { font-family: Arial; background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); min-height: 100vh; display: flex; align-items: center; justify-content: center; }
        .form-box { background: white; padding: 3rem; border-radius: 20px; width: 400px; }
        h1 { color: #667eea; text-align: center; margin-bottom: 2rem; }
        .form-group { margin-bottom: 1.5rem; }
        label { display: block; margin-bottom: 0.5rem; color: #333; }
        input { width: 100%; padding: 0.75rem; border: 2px solid #e0e0e0; border-radius: 8px; }
        .btn { width: 100%; background: #667eea; color: white; padding: 1rem; border: none; border-radius: 8px; cursor: pointer; }
        .error { background: #fee; color: #c33; padding: 1rem; border-radius: 8px; margin-bottom: 1rem; }
        .success { background: #efe; color: #3c3; padding: 1rem; border-radius: 8px; margin-bottom: 1rem; }
        .links { text-align: center; margin-top: 1rem; }
        .links a { color: #667eea; }
    </style>
</head>
<body>
    <div class="form-box">
        <h1>Login</h1>
        {% if error %}<div class="error">{{ error }}</div>{% endif %}
        {% if success %}<div class="success">{{ success }}</div>{% endif %}
        <form method="POST">
            <div class="form-group">
                <label>Email</label>
                <input type="email" name="email" required>
            </div>
            <div class="form-group">
                <label>Password</label>
                <input type="password" name="password" required>
            </div>
            <button type="submit" class="btn">Login</button>
        </form>
        <div class="links">
            <p>Don't have an account? <a href="/register">Register</a></p>
            <p><a href="/">Back to Home</a></p>
        </div>
    </div>
</body>
</html>
"""

REGISTER_TEMPLATE = """
<!DOCTYPE html>
<html>
<head>
    <title>Register</title>
    <style>
        * { margin: 0; padding: 0; box-sizing: border-box; }
        body { font-family: Arial; background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); min-height: 100vh; display: flex; align-items: center; justify-content: center; padding: 2rem; }
        .form-box { background: white; padding: 3rem; border-radius: 20px; width: 500px; }
        h1 { color: #667eea; text-align: center; margin-bottom: 2rem; }
        .form-group { margin-bottom: 1.5rem; }
        label { display: block; margin-bottom: 0.5rem; color: #333; }
        input, select { width: 100%; padding: 0.75rem; border: 2px solid #e0e0e0; border-radius: 8px; }
        .btn { width: 100%; background: #667eea; color: white; padding: 1rem; border: none; border-radius: 8px; cursor: pointer; }
        .error { background: #fee; color: #c33; padding: 1rem; border-radius: 8px; margin-bottom: 1rem; }
        .links { text-align: center; margin-top: 1rem; }
        .links a { color: #667eea; }
    </style>
</head>
<body>
    <div class="form-box">
        <h1>Register</h1>
        {% if error %}<div class="error">{{ error }}</div>{% endif %}
        <form method="POST">
            <div class="form-group">
                <label>Username</label>
                <input type="text" name="username" required>
            </div>
            <div class="form-group">
                <label>Email</label>
                <input type="email" name="email" required>
            </div>
            <div class="form-group">
                <label>Phone</label>
                <input type="tel" name="phone" pattern="[0-9]{10}">
            </div>
            <div class="form-group">
                <label>Password</label>
                <input type="password" name="password" required minlength="6">
            </div>
            <div class="form-group">
                <label>Confirm Password</label>
                <input type="password" name="confirm_password" required>
            </div>
            <div class="form-group">
                <label>Register as</label>
                <select name="user_type" required>
                    <option value="buyer">Buyer</option>
                    <option value="dealer">Dealer</option>
                </select>
            </div>
            <button type="submit" class="btn">Register</button>
        </form>
        <div class="links">
            <p>Already registered? <a href="/login">Login</a></p>
            <p><a href="/">Back to Home</a></p>
        </div>
    </div>
</body>
</html>
"""

ADD_PROPERTY_TEMPLATE = """
<!DOCTYPE html>
<html>
<head>
    <title>Add Property</title>
    <style>
        * { margin: 0; padding: 0; box-sizing: border-box; }
        body { font-family: Arial; background: #f5f5f5; }
        .navbar { background: white; padding: 1rem 2rem; box-shadow: 0 2px 10px rgba(0,0,0,0.1); }
        .navbar h1 { color: #667eea; }
        .navbar a { margin-left: 2rem; text-decoration: none; color: #333; }
        .container { max-width: 900px; margin: 2rem auto; padding: 0 2rem; }
        .form-card { background: white; padding: 3rem; border-radius: 20px; }
        .form-grid { display: grid; grid-template-columns: repeat(2, 1fr); gap: 1.5rem; }
        .form-group { margin-bottom: 1.5rem; }
        .form-group.full { grid-column: 1 / -1; }
        label { display: block; margin-bottom: 0.5rem; color: #333; font-weight: 500; }
        input, select, textarea { width: 100%; padding: 0.75rem; border: 2px solid #e0e0e0; border-radius: 8px; font-family: inherit; }
        textarea { min-height: 100px; }
        .btn { background: #667eea; color: white; padding: 1rem 2rem; border: none; border-radius: 10px; cursor: pointer; width: 100%; }
        .calc-result { background: #f9f9f9; padding: 1rem; border-radius: 8px; margin-top: 0.5rem; font-weight: bold; color: #667eea; }
        h3 { color: #667eea; margin: 1rem 0; grid-column: 1/-1; }
    </style>
</head>
<body>
    <div class="navbar">
        <h1>Add Property</h1>
        <nav style="display: inline;">
            <a href="/">Home</a>
            <a href="/dealer/dashboard">Dashboard</a>
            <a href="/logout">Logout</a>
        </nav>
    </div>

    <div class="container">
        <div class="form-card">
            <h2 style="margin-bottom: 2rem;">Add New Property</h2>
            <form method="POST">
                <div class="form-group full">
                    <label>Property Title *</label>
                    <input type="text" name="title" required>
                </div>

                <div class="form-group full">
                    <label>Description</label>
                    <textarea name="description"></textarea>
                </div>

                <h3>Location Details</h3>

                <div class="form-grid">
                    <div class="form-group">
                        <label>Address *</label>
                        <input type="text" name="address" required>
                    </div>
                    <div class="form-group">
                        <label>City *</label>
                        <input type="text" name="city" required>
                    </div>
                    <div class="form-group">
                        <label>State *</label>
                        <input type="text" name="state" required value="Uttarakhand">
                    </div>
                    <div class="form-group">
                        <label>Pincode</label>
                        <input type="text" name="pincode">
                    </div>
                </div>

                <h3>Dimensions</h3>

                <div class="form-grid">
                    <div class="form-group">
                        <label>Length (feet) *</label>
                        <input type="number" step="any" name="length" required id="length" oninput="calc()">
                    </div>
                    <div class="form-group">
                        <label>Width (feet) *</label>
                        <input type="number" step="any" name="width" required id="width" oninput="calc()">
                    </div>
                    <div class="form-group full">
                        <div class="calc-result" id="area">Area will be calculated</div>
                    </div>
                </div>

                <h3>Pricing</h3>

                <div class="form-grid">
                    <div class="form-group">
                        <label>Price per Square Yard (₹) *</label>
                        <input type="number" step="any" name="price_per_sqyard" required id="price" oninput="calc()">
                    </div>
                    <div class="form-group">
                        <div class="calc-result" id="total" style="margin-top: 1.8rem;">Total: ₹0</div>
                    </div>
                </div>

                <h3>Features</h3>

                <div class="form-grid">
                    <div class="form-group">
                        <label>Boundary Type</label>
                        <select name="boundary_type">
                            <option value="">Select</option>
                            <option value="Wall">Wall</option>
                            <option value="Fence">Fence</option>
                            <option value="Open">Open</option>
                        </select>
                    </div>
                    <div class="form-group">
                        <label>Road Type</label>
                        <select name="road_type">
                            <option value="">Select</option>
                            <option value="Paved">Paved</option>
                            <option value="Kuccha">Kuccha</option>
                        </select>
                    </div>
                    <div class="form-group">
                        <label><input type="checkbox" name="water_access" value="1"> Water Access</label>
                        <label><input type="checkbox" name="electricity" value="1"> Electricity</label>
                    </div>
                </div>

                <div class="form-group full">
                    <button type="submit" class="btn">Add Property</button>
                </div>
            </form>
        </div>
    </div>

    <script>
        let areaSqYard = 0;
        function calc() {
            const l = parseFloat(document.getElementById('length').value) || 0;
            const w = parseFloat(document.getElementById('width').value) || 0;
            const sqft = l * w;
            areaSqYard = sqft / 9;
            document.getElementById('area').innerHTML = `Area: <strong>${sqft.toFixed(2)} sq ft | ${areaSqYard.toFixed(2)} sq yd</strong>`;
            
            const price = parseFloat(document.getElementById('price').value) || 0;
            const total = areaSqYard * price;
            document.getElementById('total').innerHTML = `Total: <strong>₹${total.toLocaleString('en-IN')}</strong> (₹${(total/100000).toFixed(2)} L)`;
        }
    </script>
</body>
</html>
"""

PROPERTY_DETAIL_TEMPLATE = """
<!DOCTYPE html>
<html>
<head>
    <title>{{ property.title }}</title>
    <style>
        * { margin: 0; padding: 0; box-sizing: border-box; }
        body { font-family: Arial; background: #f5f5f5; }
        .navbar { background: white; padding: 1rem 2rem; box-shadow: 0 2px 10px rgba(0,0,0,0.1); }
        .navbar h1 { color: #667eea; display: inline; }
        .navbar a { margin-left: 2rem; text-decoration: none; color: #333; }
        .container { max-width: 1200px; margin: 2rem auto; padding: 0 2rem; }
        .back-btn { display: inline-block; background: #667eea; color: white; padding: 0.75rem 1.5rem; border-radius: 8px; text-decoration: none; margin-bottom: 1rem; }
        .header { background: white; padding: 2rem; border-radius: 15px; margin-bottom: 2rem; }
        .grid { display: grid; grid-template-columns: 2fr 1fr; gap: 2rem; }
        .card { background: white; padding: 2rem; border-radius: 15px; margin-bottom: 2rem; }
        .card h3 { color: #333; margin-bottom: 1rem; padding-bottom: 1rem; border-bottom: 2px solid #e0e0e0; }
        .detail-grid { display: grid; grid-template-columns: repeat(2, 1fr); gap: 1rem; }
        .detail-item { padding: 1rem; background: #f9f9f9; border-radius: 8px; }
        .detail-label { color: #999; font-size: 0.9rem; }
        .detail-value { color: #333; font-size: 1.1rem; font-weight: 600; }
        canvas { width: 100%; height: 400px; background: #f5f5f5; border-radius: 10px; }
        .dealer-avatar { width: 100px; height: 100px; border-radius: 50%; background: #667eea; color: white; display: flex; align-items: center; justify-content: center; font-size: 2.5rem; margin: 0 auto 1rem; }
        .btn { background: #667eea; color: white; padding: 1rem 2rem; border: none; border-radius: 10px; cursor: pointer; width: 100%; margin-top: 1rem; }
        .calculator input { width: 100%; padding: 0.75rem; border: 2px solid #e0e0e0; border-radius: 8px; margin-bottom: 1rem; }
        .calc-result { background: #667eea; color: white; padding: 1rem; border-radius: 8px; text-align: center; font-size: 1.2rem; font-weight: bold; }
    </style>
</head>
<body>
    <div class="navbar">
        <h1>🏡 Indian Real Estate</h1>
        <nav style="float: right;">
            <a href="/">Home</a>
        </nav>
    </div>

    <div class="container">
        <a href="/" class="back-btn">← Back</a>
        
        <div class="header">
            <h1>{{ property.title }}</h1>
            <p style="color: #666;">📍 {{ property.address }}, {{ property.city }}, {{ property.state }}</p>
            <div style="color: #667eea; font-size: 2.5rem; font-weight: bold; margin-top: 1rem;">
                ₹{{ "%.2f"|format(property.total_price / 100000) }} Lakhs
            </div>
            <p style="color: #666;">₹{{ "%.0f"|format(property.price_per_sqyard) }} per sq yard</p>
        </div>

        <div class="grid">
            <div>
                <div class="card">
                    <h3>📏 Dimensions</h3>
                    <div class="detail-grid">
                        <div class="detail-item">
                            <div class="detail-label">Length</div>
                            <div class="detail-value">{{ "%.2f"|format(property.length) }} ft</div>
                        </div>
                        <div class="detail-item">
                            <div class="detail-label">Width</div>
                            <div class="detail-value">{{ "%.2f"|format(property.width) }} ft</div>
                        </div>
                        <div class="detail-item">
                            <div class="detail-label">Area (sq ft)</div>
                            <div class="detail-value">{{ "%.0f"|format(property.area_sqft) }}</div>
                        </div>
                        <div class="detail-item">
                            <div class="detail-label">Area (sq yd)</div>
                            <div class="detail-value">{{ "%.0f"|format(property.area_sqyard) }}</div>
                        </div>
                    </div>
                </div>

                <div class="card">
                    <h3>🎯 3D Plot Visualization</h3>
                    <canvas id="plot"></canvas>
                </div>

                <div class="card">
                    <h3>📝 Description</h3>
                    <p style="color: #666;">{{ property.description or 'No description' }}</p>
                </div>
            </div>

            <div>
                <div class="card" style="text-align: center;">
                    <h3>👤 Dealer</h3>
                    <div class="dealer-avatar">{{ property.dealer.username[0]|upper }}</div>
                    <h4>{{ property.dealer.username }}</h4>
                    <p style="color: #666;">{{ property.dealer.email }}</p>
                    {% if session.user_id and session.user_type == 'buyer' %}
                    <button class="btn" onclick="contact()">Contact Dealer</button>
                    {% elif not session.user_id %}
                    <a href="/login" class="btn" style="text-decoration: none; display: block;">Login to Contact</a>
                    {% endif %}
                </div>

                <div class="card">
                    <h3>🧮 Calculator</h3>
                    <div class="calculator">
                        <label style="color: #666;">Custom Area (sq yd):</label>
                        <input type="number" id="customArea" value="{{ '%.0f'|format(property.area_sqyard) }}" oninput="calcPrice()">
                        <div class="calc-result" id="result">₹{{ "%.2f"|format(property.total_price / 100000) }}L</div>
                    </div>
                </div>
            </div>
        </div>
    </div>

    <script>
        const price = {{ property.price_per_sqyard }};
        const propId = {{ property.id }};

        function calcPrice() {
            const area = parseFloat(document.getElementById('customArea').value) || 0;
            const total = area * price;
            document.getElementById('result').textContent = '₹' + (total / 100000).toFixed(2) + 'L';
        }

        function contact() {
            const msg = prompt('Enter your message:');
            if (!msg) return;
            fetch('/api/inquiry', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ property_id: propId, message: msg })
            })
            .then(r => r.json())
            .then(d => alert(d.success ? 'Sent!' : 'Failed'));
        }

        // Draw plot
        const canvas = document.getElementById('plot');
        const ctx = canvas.getContext('2d');
        const l = {{ property.length }};
        const w = {{ property.width }};
        
        function draw() {
            canvas.width = canvas.offsetWidth;
            canvas.height = 400;
            const scale = Math.min((canvas.width - 100) / l, (canvas.height - 100) / w);
            const x = (canvas.width - l * scale) / 2;
            const y = (canvas.height - w * scale) / 2;
            
            ctx.fillStyle = '#667eea';
            ctx.fillRect(x, y, l * scale, w * scale);
            ctx.strokeStyle = '#333';
            ctx.lineWidth = 3;
            ctx.strokeRect(x, y, l * scale, w * scale);
            
            ctx.fillStyle = '#333';
            ctx.font = '16px Arial';
            ctx.textAlign = 'center';
            ctx.fillText(l + ' ft', x + (l * scale) / 2, y - 10);
        }
        draw();
    </script>
</body>
</html>
"""

DEALER_DASHBOARD = """
<!DOCTYPE html>
<html>
<head>
    <title>Dashboard</title>
    <style>
        * { margin: 0; padding: 0; box-sizing: border-box; }
        body { font-family: Arial; background: #f5f5f5; }
        .navbar { background: white; padding: 1rem 2rem; }
        .navbar h1 { color: #667eea; display: inline; }
        .navbar a { margin-left: 2rem; text-decoration: none; color: #333; }
        .container { max-width: 1200px; margin: 2rem auto; padding: 0 2rem; }
        .card { background: white; padding: 2rem; border-radius: 15px; margin-bottom: 2rem; }
        .properties { display: grid; grid-template-columns: repeat(auto-fill, minmax(300px, 1fr)); gap: 1.5rem; }
        .property-card { border: 2px solid #e0e0e0; border-radius: 10px; padding: 1.5rem; }
        .btn { background: #667eea; color: white; padding: 0.75rem 1.5rem; border-radius: 8px; text-decoration: none; display: inline-block; margin-top: 1rem; }
    </style>
</head>
<body>
    <div class="navbar">
        <h1>Dealer Dashboard</h1>
        <nav style="float: right;">
            <a href="/">Home</a>
            <a href="/dealer/add-property">Add Property</a>
            <a href="/logout">Logout</a>
        </nav>
    </div>

    <div class="container">
        <div class="card">
            <h2>Welcome, {{ session.username }}!</h2>
        </div>

        <div class="card">
            <h2>Your Properties ({{ properties|length }})</h2>
            {% if properties %}
            <div class="properties" style="margin-top: 1.5rem;">
                {% for p in properties %}
                <div class="property-card">
                    <h3>{{ p.title }}</h3>
                    <p style="color: #666;">📍 {{ p.city }}</p>
                    <p style="color: #667eea; font-weight: bold;">₹{{ "%.2f"|format(p.total_price / 100000) }}L</p>
                    <a href="/property/{{ p.id }}" class="btn">View</a>
                </div>
                {% endfor %}
            </div>
            {% else %}
            <p style="margin-top: 1rem; color: #666;">No properties yet. <a href="/dealer/add-property">Add one</a></p>
            {% endif %}
        </div>
    </div>
</body>
</html>
"""

BUYER_DASHBOARD = """
<!DOCTYPE html>
<html>
<head>
    <title>Dashboard</title>
    <style>
        * { margin: 0; padding: 0; box-sizing: border-box; }
        body { font-family: Arial; background: #f5f5f5; }
        .navbar { background: white; padding: 1rem 2rem; }
        .navbar h1 { color: #667eea; display: inline; }
        .navbar a { margin-left: 2rem; text-decoration: none; color: #333; }
        .container { max-width: 1200px; margin: 2rem auto; padding: 0 2rem; }
        .card { background: white; padding: 2rem; border-radius: 15px; margin-bottom: 2rem; }
        .inquiry { border: 2px solid #e0e0e0; border-radius: 10px; padding: 1.5rem; margin-bottom: 1rem; }
    </style>
</head>
<body>
    <div class="navbar">
        <h1>Buyer Dashboard</h1>
        <nav style="float: right;">
            <a href="/">Browse Properties</a>
            <a href="/logout">Logout</a>
        </nav>
    </div>

    <div class="container">
        <div class="card">
            <h2>Welcome, {{ session.username }}!</h2>
        </div>

        <div class="card">
            <h2>Your Inquiries ({{ inquiries|length }})</h2>
            {% if inquiries %}
                {% for inq in inquiries %}
                <div class="inquiry">
                    <h3>{{ inq.property.title }}</h3>
                    <p style="color: #666;">{{ inq.message }}</p>
                    <p style="color: #999; font-size: 0.9rem;">{{ inq.created_at.strftime('%d %b %Y') }}</p>
                </div>
                {% endfor %}
            {% else %}
            <p style="margin-top: 1rem; color: #666;">No inquiries yet. <a href="/">Browse properties</a></p>
            {% endif %}
        </div>
    </div>
</body>
</html>
"""

# Routes
@app.route('/')
def home():
    properties = Property.query.order_by(Property.created_at.desc()).all()
    return render_template_string(HOME_TEMPLATE, properties=properties)

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
            return render_template_string(REGISTER_TEMPLATE, error='Passwords do not match')
        
        if User.query.filter_by(email=email).first():
            return render_template_string(REGISTER_TEMPLATE, error='Email already registered')
        
        hashed = generate_password_hash(password)
        user = User(username=username, email=email, phone=phone, password=hashed, user_type=user_type)
        db.session.add(user)
        db.session.commit()
        
        return redirect(url_for('login', success='Registration successful'))
    
    return render_template_string(REGISTER_TEMPLATE)

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
        
        return render_template_string(LOGIN_TEMPLATE, error='Invalid credentials')
    
    return render_template_string(LOGIN_TEMPLATE, success=success)

@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('home'))

@app.route('/property/<int:property_id>')
def property_detail(property_id):
    property = Property.query.get_or_404(property_id)
    return render_template_string(PROPERTY_DETAIL_TEMPLATE, property=property)

@app.route('/dealer/dashboard')
def dealer_dashboard():
    if 'user_id' not in session or session['user_type'] != 'dealer':
        return redirect(url_for('login'))
    
    properties = Property.query.filter_by(dealer_id=session['user_id']).all()
    inquiries = Inquiry.query.join(Property).filter(Property.dealer_id == session['user_id']).all()
    
    return render_template_string(DEALER_DASHBOARD, properties=properties, inquiries=inquiries)

@app.route('/buyer/dashboard')
def buyer_dashboard():
    if 'user_id' not in session or session['user_type'] != 'buyer':
        return redirect(url_for('login'))
    
    inquiries = Inquiry.query.filter_by(buyer_id=session['user_id']).all()
    return render_template_string(BUYER_DASHBOARD, inquiries=inquiries)

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
    
    return render_template_string(ADD_PROPERTY_TEMPLATE)

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