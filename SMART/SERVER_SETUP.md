# Simple Backend Setup

## 🚀 Quick Start (3 Steps)

```bash
# 1. Install Flask
pip install Flask Flask-CORS

# 2. Run server
python server.py
```

Server runs on: **http://127.0.0.1:5000**

## ✅ That's it!

- Database auto-creates on first run
- Sample data included
- All APIs ready to use

## 🔌 API Endpoints

- `GET /api/medicines` - All medicines
- `GET /api/procedures` - All procedures
- `GET /api/search?q=name&type=medicine` - Search
- `POST /api/check-price` - Check price
- `POST /api/verify-bill` - Verify bill
- `GET /api/bills` - All bills
- `GET /api/stats` - Statistics

## 📝 Update Frontend

Change API calls from Supabase to Flask:

```javascript
// Instead of Supabase, use fetch:
const API_URL = 'http://127.0.0.1:5000/api';

// Example:
fetch(`${API_URL}/medicines`)
  .then(res => res.json())
  .then(data => console.log(data));
```
