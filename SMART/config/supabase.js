// Supabase Configuration
const SUPABASE_URL = 'https://pipjgakwyvonfjoprhpp.supabase.co';
const SUPABASE_ANON_KEY = 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6InBpcGpnYWt3eXZvbmZqb3ByaHBwIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NzA3MTEyOTgsImV4cCI6MjA4NjI4NzI5OH0.73nFgCmkuMZm_zXIISsp3lhsVcm8Tcx2fBInnyiW1vE';

const { createClient } = supabase;
const supabaseClient = createClient(SUPABASE_URL, SUPABASE_ANON_KEY);

// Database Schema Setup (Run these in Supabase SQL Editor)
/*
-- Medicines Table
CREATE TABLE medicines (
    id SERIAL PRIMARY KEY,
    name VARCHAR(255) NOT NULL,
    category VARCHAR(100),
    govt_min_price DECIMAL(10,2) NOT NULL,
    govt_max_price DECIMAL(10,2) NOT NULL,
    unit VARCHAR(50),
    created_at TIMESTAMP DEFAULT NOW()
);

-- Medical Procedures Table
CREATE TABLE procedures (
    id SERIAL PRIMARY KEY,
    name VARCHAR(255) NOT NULL,
    category VARCHAR(100),
    govt_min_price DECIMAL(10,2) NOT NULL,
    govt_max_price DECIMAL(10,2) NOT NULL,
    created_at TIMESTAMP DEFAULT NOW()
);

-- Bills Table
CREATE TABLE bills (
    id SERIAL PRIMARY KEY,
    patient_name VARCHAR(255) NOT NULL,
    hospital_name VARCHAR(255) NOT NULL,
    bill_date DATE NOT NULL,
    total_amount DECIMAL(10,2) NOT NULL,
    verified BOOLEAN DEFAULT FALSE,
    overcharged BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMP DEFAULT NOW()
);

-- Bill Items Table
CREATE TABLE bill_items (
    id SERIAL PRIMARY KEY,
    bill_id INTEGER REFERENCES bills(id) ON DELETE CASCADE,
    item_type VARCHAR(50) NOT NULL, -- 'medicine' or 'procedure'
    item_id INTEGER NOT NULL,
    item_name VARCHAR(255) NOT NULL,
    charged_price DECIMAL(10,2) NOT NULL,
    govt_max_price DECIMAL(10,2) NOT NULL,
    is_overcharged BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMP DEFAULT NOW()
);

-- Complaints Table (No Foreign Key - bill_id is optional)
CREATE TABLE complaints (
    id SERIAL PRIMARY KEY,
    bill_id INTEGER,
    patient_name VARCHAR(255) NOT NULL,
    patient_email VARCHAR(255) NOT NULL,
    patient_phone VARCHAR(50) NOT NULL,
    hospital_name VARCHAR(255) NOT NULL,
    complaint_details TEXT NOT NULL,
    overcharge_amount DECIMAL(10,2) NOT NULL,
    status VARCHAR(50) DEFAULT 'Pending',
    created_at TIMESTAMP DEFAULT NOW()
);

-- Insert Sample Data
INSERT INTO medicines (name, category, govt_min_price, govt_max_price, unit) VALUES
('Paracetamol 500mg', 'Pain Relief', 2.00, 5.00, 'tablet'),
('Amoxicillin 250mg', 'Antibiotic', 5.00, 12.00, 'capsule'),
('Metformin 500mg', 'Diabetes', 3.00, 8.00, 'tablet'),
('Atorvastatin 10mg', 'Cholesterol', 8.00, 20.00, 'tablet'),
('Omeprazole 20mg', 'Gastric', 4.00, 10.00, 'capsule');

INSERT INTO procedures (name, category, govt_min_price, govt_max_price) VALUES
('Blood Test - Complete', 'Diagnostic', 200.00, 500.00),
('X-Ray Chest', 'Imaging', 300.00, 800.00),
('ECG', 'Cardiac', 150.00, 400.00),
('Ultrasound Abdomen', 'Imaging', 500.00, 1500.00),
('General Consultation', 'Consultation', 200.00, 600.00);
*/
