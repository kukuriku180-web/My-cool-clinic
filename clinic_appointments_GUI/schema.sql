-- Clinic Appointment System - Database Schema
-- This file defines the database structure
-- Run this file to understand the database structure (it's created automatically by Python)

CREATE TABLE IF NOT EXISTS appointments (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    patient_name TEXT NOT NULL,
    phone TEXT,
    date TEXT NOT NULL,
    time TEXT NOT NULL,
    doctor TEXT NOT NULL,
    service_type TEXT NOT NULL,
    reason TEXT,
    status TEXT DEFAULT 'pending'
);
