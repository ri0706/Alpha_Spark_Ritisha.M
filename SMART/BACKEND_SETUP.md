# Django Backend Setup Guide

## 📦 Installation

```bash
# Install Django
pip install -r requirements.txt

# Initialize database with sample data
python backend.py init

# Start server
python backend.py runserver
```

Server runs on: `http://127.0.0.1:8000`

## 🔌 API Endpoints

### Medicines & Procedures
- `GET /api/medicines/` - Get all medicines
- `GET /api/procedures/` - Get all procedures
- `GET /api/search/?q=name&type=medicine` - Search items

### Price Checking
- `POST /api/check-price/` - Check single price
  ```json
  {
    "item_name": "Paracetamol 500mg",
    "item_type": "medicine",
    "charged_price": 5.00,
    "save_to_db": true
  }
  ```

### Bill Verification
- `POST /api/verify-bill/` - Verify complete bill
  ```json
  {
    "patient_name": "John Doe",
    "hospital_name": "City Hospital",
    "bill_date": "2024-01-15",
    "items": [
      {
        "name": "Paracetamol 500mg",
        "type": "medicine",
        "price": 5.00
      }
    ]
  }
  ```

### Dashboard
- `GET /api/bills/` - Get all bills
- `GET /api/bills/<id>/` - Get bill details
- `GET /api/stats/` - Get statistics

## 🗄️ Database

SQLite database: `healthcare_billing.db`

### Tables
- `medicines` - Medicine catalog with govt prices
- `procedures` - Medical procedures with govt prices
- `bills` - Verified bills
- `bill_items` - Individual bill items

## 🔧 Configuration

All configuration in single file: `backend.py`

- Database: SQLite (can switch to PostgreSQL/MySQL)
- CORS: Enabled for all origins
- CSRF: Exempt for API endpoints
- Debug: Enabled (disable in production)

## 🚀 Production Deployment

```bash
# Use gunicorn
pip install gunicorn
gunicorn backend:application --bind 0.0.0.0:8000

# Or use uwsgi
pip install uwsgi
uwsgi --http :8000 --wsgi-file backend.py
```

## 📝 Notes

- Single-file Django app for simplicity
- All models, views, and URLs in one file
- Auto-creates database on first run
- Includes sample data for testing
