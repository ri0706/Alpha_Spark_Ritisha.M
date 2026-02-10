"""
Smart Healthcare Billing - Simple Flask Backend
Run: python server.py
"""

from flask import Flask, request, jsonify
from flask_cors import CORS
import sqlite3
from datetime import datetime
import json

app = Flask(__name__)
CORS(app)

DB_NAME = 'healthcare.db'

# ============================================================================
# DATABASE SETUP
# ============================================================================

def init_db():
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    
    # Create tables
    c.execute('''CREATE TABLE IF NOT EXISTS medicines (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT NOT NULL,
        category TEXT,
        govt_min_price REAL NOT NULL,
        govt_max_price REAL NOT NULL,
        unit TEXT
    )''')
    
    c.execute('''CREATE TABLE IF NOT EXISTS procedures (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT NOT NULL,
        category TEXT,
        govt_min_price REAL NOT NULL,
        govt_max_price REAL NOT NULL
    )''')
    
    c.execute('''CREATE TABLE IF NOT EXISTS bills (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        patient_name TEXT NOT NULL,
        hospital_name TEXT NOT NULL,
        bill_date TEXT NOT NULL,
        total_amount REAL NOT NULL,
        verified INTEGER DEFAULT 1,
        overcharged INTEGER DEFAULT 0,
        created_at TEXT DEFAULT CURRENT_TIMESTAMP
    )''')
    
    c.execute('''CREATE TABLE IF NOT EXISTS bill_items (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        bill_id INTEGER,
        item_type TEXT NOT NULL,
        item_id INTEGER NOT NULL,
        item_name TEXT NOT NULL,
        charged_price REAL NOT NULL,
        govt_max_price REAL NOT NULL,
        is_overcharged INTEGER DEFAULT 0,
        FOREIGN KEY (bill_id) REFERENCES bills(id)
    )''')
    
    c.execute('''CREATE TABLE IF NOT EXISTS complaints (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        bill_id INTEGER,
        patient_name TEXT NOT NULL,
        patient_email TEXT NOT NULL,
        patient_phone TEXT NOT NULL,
        hospital_name TEXT NOT NULL,
        complaint_details TEXT NOT NULL,
        overcharge_amount REAL NOT NULL,
        status TEXT DEFAULT 'Pending',
        created_at TEXT DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (bill_id) REFERENCES bills(id)
    )''')
    
    # Insert sample data if empty
    c.execute('SELECT COUNT(*) FROM medicines')
    if c.fetchone()[0] == 0:
        medicines = [
            ('Paracetamol 500mg', 'Pain Relief', 2.00, 5.00, 'tablet'),
            ('Amoxicillin 250mg', 'Antibiotic', 5.00, 12.00, 'capsule'),
            ('Metformin 500mg', 'Diabetes', 3.00, 8.00, 'tablet'),
            ('Atorvastatin 10mg', 'Cholesterol', 8.00, 20.00, 'tablet'),
            ('Omeprazole 20mg', 'Gastric', 4.00, 10.00, 'capsule'),
        ]
        c.executemany('INSERT INTO medicines (name, category, govt_min_price, govt_max_price, unit) VALUES (?,?,?,?,?)', medicines)
    
    c.execute('SELECT COUNT(*) FROM procedures')
    if c.fetchone()[0] == 0:
        procedures = [
            ('Blood Test - Complete', 'Diagnostic', 200.00, 500.00),
            ('X-Ray Chest', 'Imaging', 300.00, 800.00),
            ('ECG', 'Cardiac', 150.00, 400.00),
            ('Ultrasound Abdomen', 'Imaging', 500.00, 1500.00),
            ('General Consultation', 'Consultation', 200.00, 600.00),
        ]
        c.executemany('INSERT INTO procedures (name, category, govt_min_price, govt_max_price) VALUES (?,?,?,?)', procedures)
    
    conn.commit()
    conn.close()
    print("✅ Database initialized")

# ============================================================================
# API ENDPOINTS
# ============================================================================

@app.route('/')
def home():
    return jsonify({
        'message': 'Smart Healthcare Billing API',
        'endpoints': {
            'GET /api/medicines': 'Get all medicines',
            'GET /api/procedures': 'Get all procedures',
            'GET /api/search?q=name&type=medicine': 'Search items',
            'POST /api/check-price': 'Check price',
            'POST /api/verify-bill': 'Verify bill',
            'GET /api/bills': 'Get all bills',
            'GET /api/stats': 'Get statistics'
        }
    })

@app.route('/api/medicines')
def get_medicines():
    conn = sqlite3.connect(DB_NAME)
    conn.row_factory = sqlite3.Row
    c = conn.cursor()
    c.execute('SELECT * FROM medicines ORDER BY name')
    medicines = [dict(row) for row in c.fetchall()]
    conn.close()
    return jsonify(medicines)

@app.route('/api/procedures')
def get_procedures():
    conn = sqlite3.connect(DB_NAME)
    conn.row_factory = sqlite3.Row
    c = conn.cursor()
    c.execute('SELECT * FROM procedures ORDER BY name')
    procedures = [dict(row) for row in c.fetchall()]
    conn.close()
    return jsonify(procedures)

@app.route('/api/search')
def search_item():
    query = request.args.get('q', '')
    item_type = request.args.get('type', 'medicine')
    
    conn = sqlite3.connect(DB_NAME)
    conn.row_factory = sqlite3.Row
    c = conn.cursor()
    
    table = 'medicines' if item_type == 'medicine' else 'procedures'
    c.execute(f'SELECT * FROM {table} WHERE name LIKE ? LIMIT 10', (f'%{query}%',))
    items = [dict(row) for row in c.fetchall()]
    conn.close()
    
    return jsonify(items)

@app.route('/api/check-price', methods=['POST'])
def check_price():
    data = request.json
    item_name = data.get('item_name')
    item_type = data.get('item_type')
    charged_price = float(data.get('charged_price'))
    save_to_db = data.get('save_to_db', False)
    
    conn = sqlite3.connect(DB_NAME)
    conn.row_factory = sqlite3.Row
    c = conn.cursor()
    
    table = 'medicines' if item_type == 'medicine' else 'procedures'
    c.execute(f'SELECT * FROM {table} WHERE name LIKE ? LIMIT 1', (f'%{item_name}%',))
    item = c.fetchone()
    
    if not item:
        conn.close()
        return jsonify({'found': False, 'message': 'Item not found'})
    
    item = dict(item)
    is_valid = item['govt_min_price'] <= charged_price <= item['govt_max_price']
    overcharge = max(0, charged_price - item['govt_max_price'])
    
    if save_to_db:
        c.execute('''INSERT INTO bills (patient_name, hospital_name, bill_date, total_amount, overcharged)
                     VALUES (?, ?, ?, ?, ?)''',
                  ('Quick Check', 'Price Verification', datetime.now().date().isoformat(), charged_price, int(not is_valid)))
        conn.commit()
    
    conn.close()
    
    return jsonify({
        'found': True,
        'item': item,
        'charged_price': charged_price,
        'is_valid': is_valid,
        'overcharge': overcharge,
        'message': 'Price is within government limits' if is_valid else f'Overcharged by ₹{overcharge:.2f}'
    })

@app.route('/api/verify-bill', methods=['POST'])
def verify_bill():
    data = request.json
    patient_name = data.get('patient_name')
    hospital_name = data.get('hospital_name')
    bill_date = data.get('bill_date')
    items = data.get('items', [])
    
    conn = sqlite3.connect(DB_NAME)
    conn.row_factory = sqlite3.Row
    c = conn.cursor()
    
    total_amount = 0
    has_overcharge = False
    verified_items = []
    
    for item_data in items:
        item_name = item_data['name']
        item_type = item_data['type']
        charged_price = float(item_data['price'])
        total_amount += charged_price
        
        table = 'medicines' if item_type == 'medicine' else 'procedures'
        c.execute(f'SELECT * FROM {table} WHERE name LIKE ? LIMIT 1', (f'%{item_name}%',))
        db_item = c.fetchone()
        
        if db_item:
            db_item = dict(db_item)
            is_valid = db_item['govt_min_price'] <= charged_price <= db_item['govt_max_price']
            if not is_valid:
                has_overcharge = True
            
            verified_items.append({
                'item_id': db_item['id'],
                'item_name': db_item['name'],
                'item_type': item_type,
                'charged_price': charged_price,
                'govt_max_price': db_item['govt_max_price'],
                'is_overcharged': int(not is_valid)
            })
    
    # Create bill
    c.execute('''INSERT INTO bills (patient_name, hospital_name, bill_date, total_amount, overcharged)
                 VALUES (?, ?, ?, ?, ?)''',
              (patient_name, hospital_name, bill_date, total_amount, int(has_overcharge)))
    bill_id = c.lastrowid
    
    # Create bill items
    for item in verified_items:
        c.execute('''INSERT INTO bill_items (bill_id, item_type, item_id, item_name, charged_price, govt_max_price, is_overcharged)
                     VALUES (?, ?, ?, ?, ?, ?, ?)''',
                  (bill_id, item['item_type'], item['item_id'], item['item_name'], 
                   item['charged_price'], item['govt_max_price'], item['is_overcharged']))
    
    conn.commit()
    conn.close()
    
    return jsonify({'success': True, 'bill_id': bill_id})

@app.route('/api/bills')
def get_bills():
    conn = sqlite3.connect(DB_NAME)
    conn.row_factory = sqlite3.Row
    c = conn.cursor()
    c.execute('SELECT * FROM bills ORDER BY created_at DESC')
    bills = [dict(row) for row in c.fetchall()]
    conn.close()
    return jsonify(bills)

@app.route('/api/stats')
def get_stats():
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    c.execute('SELECT COUNT(*) FROM bills')
    total = c.fetchone()[0]
    c.execute('SELECT COUNT(*) FROM bills WHERE overcharged = 1')
    overcharged = c.fetchone()[0]
    c.execute('SELECT COUNT(*) FROM complaints')
    complaints = c.fetchone()[0]
    conn.close()
    
    return jsonify({
        'total_bills': total,
        'overcharged_bills': overcharged,
        'valid_bills': total - overcharged,
        'total_complaints': complaints
    })

@app.route('/api/complaints', methods=['POST'])
def file_complaint():
    data = request.json
    bill_id = data.get('bill_id')
    patient_name = data.get('patient_name')
    patient_email = data.get('patient_email')
    patient_phone = data.get('patient_phone')
    hospital_name = data.get('hospital_name')
    complaint_details = data.get('complaint_details')
    overcharge_amount = float(data.get('overcharge_amount'))
    
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    c.execute('''INSERT INTO complaints (bill_id, patient_name, patient_email, patient_phone, 
                 hospital_name, complaint_details, overcharge_amount)
                 VALUES (?, ?, ?, ?, ?, ?, ?)''',
              (bill_id, patient_name, patient_email, patient_phone, hospital_name, 
               complaint_details, overcharge_amount))
    complaint_id = c.lastrowid
    conn.commit()
    conn.close()
    
    return jsonify({'success': True, 'complaint_id': complaint_id})

@app.route('/api/complaints')
def get_complaints():
    conn = sqlite3.connect(DB_NAME)
    conn.row_factory = sqlite3.Row
    c = conn.cursor()
    c.execute('SELECT * FROM complaints ORDER BY created_at DESC')
    complaints = [dict(row) for row in c.fetchall()]
    conn.close()
    return jsonify(complaints)

# ============================================================================
# RUN SERVER
# ============================================================================

if __name__ == '__main__':
    init_db()
    print("🚀 Server starting on http://127.0.0.1:5000")
    app.run(debug=True, port=5000)
