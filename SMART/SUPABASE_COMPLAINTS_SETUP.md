# Supabase Setup - Add Complaints Table

## 🔧 Quick Setup

1. Go to your Supabase project: https://supabase.com/dashboard
2. Click on **SQL Editor** in the left sidebar
3. Click **New Query**
4. Copy and paste this SQL:

```sql
-- Create Complaints Table
CREATE TABLE complaints (
    id SERIAL PRIMARY KEY,
    bill_id INTEGER REFERENCES bills(id) ON DELETE SET NULL,
    patient_name VARCHAR(255) NOT NULL,
    patient_email VARCHAR(255) NOT NULL,
    patient_phone VARCHAR(50) NOT NULL,
    hospital_name VARCHAR(255) NOT NULL,
    complaint_details TEXT NOT NULL,
    overcharge_amount DECIMAL(10,2) NOT NULL,
    status VARCHAR(50) DEFAULT 'Pending',
    created_at TIMESTAMP DEFAULT NOW()
);
```

5. Click **Run** button
6. Done! ✅

## 📋 What This Does

- Creates a `complaints` table in your database
- Links complaints to bills (optional)
- Stores patient contact info
- Tracks complaint status (Pending/Resolved)
- Records overcharge amount
- Auto-timestamps when complaint is filed

## 🎯 Features Now Working

- ✅ File complaints against hospitals
- ✅ View all complaints
- ✅ Track complaint status
- ✅ Dashboard shows complaint count
- ✅ All data stored in Supabase

## 🔒 Security (Optional)

To enable Row Level Security:

```sql
-- Enable RLS
ALTER TABLE complaints ENABLE ROW LEVEL SECURITY;

-- Allow anyone to read complaints
CREATE POLICY "Allow public read" ON complaints
    FOR SELECT USING (true);

-- Allow anyone to insert complaints
CREATE POLICY "Allow public insert" ON complaints
    FOR INSERT WITH CHECK (true);
```

## ✅ Verification

Test if it works:
1. Open your app
2. Go to Complaints page
3. Fill the form and submit
4. Check Supabase Table Editor → complaints table
5. You should see your complaint!

That's it! Your complaint system is now fully functional with Supabase! 🎉
