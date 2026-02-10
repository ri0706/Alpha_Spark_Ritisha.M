# Smart Healthcare Billing Platform

A transparent healthcare pricing verification system that compares hospital charges with government-approved price limits.

## 🎯 Problem Statement

- Healthcare pricing is often unclear, causing patient confusion
- Lack of transparency leads to overcharging and financial stress
- Government defines standard price ranges, but verification is manual
- Need for digital system to tag and verify prices automatically

## ✨ Solution

Smart billing platform that:
- Compares hospital charges with official price limits
- Identifies overcharging instantly
- Improves transparency and builds trust
- Empowers patients to make informed healthcare decisions

## 🏗️ Project Structure

```
SMART/
├── index.html              # Homepage
├── price-checker.html      # Individual price verification
├── verify-bill.html        # Complete bill verification
├── dashboard.html          # Analytics dashboard
├── css/
│   └── style.css          # Main stylesheet
├── js/
│   └── app.js             # Core application logic
└── config/
    └── supabase.js        # Database configuration
```

## 🚀 Setup Instructions

### 1. Supabase Setup

1. Create account at [supabase.com](https://supabase.com)
2. Create new project
3. Go to SQL Editor and run the schema from `config/supabase.js`
4. Get your project URL and anon key from Settings > API

### 2. Configuration

Edit `config/supabase.js`:
```javascript
const SUPABASE_URL = 'your-project-url';
const SUPABASE_ANON_KEY = 'your-anon-key';
```

### 3. Run Application

Open `index.html` in a web browser or use a local server:

```bash
# Using Python
python -m http.server 8000

# Using Node.js
npx serve

# Using VS Code
# Install "Live Server" extension and click "Go Live"
```

## 📊 Database Schema

### Tables

**medicines**
- id, name, category
- govt_min_price, govt_max_price
- unit, created_at

**procedures**
- id, name, category
- govt_min_price, govt_max_price
- created_at

**bills**
- id, patient_name, hospital_name
- bill_date, total_amount
- verified, overcharged, created_at

**bill_items**
- id, bill_id, item_type
- item_id, item_name
- charged_price, govt_max_price
- is_overcharged, created_at

## 🎨 Features

### Price Checker
- Search medicines or procedures
- Compare charged price with govt limits
- Instant overcharge detection

### Bill Verification
- Add multiple bill items
- Verify entire bill at once
- Save verification results
- Calculate total overcharge

### Dashboard
- View all verified bills
- Track overcharging patterns
- Statistics and analytics

## 🛠️ Technologies

- **Frontend**: HTML5, CSS3, JavaScript (ES6+)
- **Database**: Supabase (PostgreSQL)
- **Hosting**: Static hosting (Netlify, Vercel, GitHub Pages)

## 🔒 Security

- All data stored securely in Supabase
- Row Level Security (RLS) can be enabled
- No sensitive data in frontend code
- API keys use anon key (public access)

## 📱 Responsive Design

- Mobile-first approach
- Works on all screen sizes
- Clean, modern UI

## 🤝 Contributing

1. Fork the repository
2. Create feature branch
3. Commit changes
4. Push to branch
5. Open pull request

## 📄 License

MIT License - feel free to use for any purpose

## 🆘 Support

For issues or questions:
- Check Supabase documentation
- Review browser console for errors
- Ensure database tables are created correctly

## 🎯 Future Enhancements

- Hospital comparison feature
- Price trend analysis
- Mobile app version
- PDF bill upload with OCR
- Email notifications
- Multi-language support
