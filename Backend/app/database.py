# ============================================================
# FILE: backend/app/database.py
# ============================================================
#
# WHAT IS THIS FILE?
# ------------------
# This file creates your database. Think of a database like
# a collection of Excel sheets. Each "table" = one sheet.
# Each row in the sheet = one record (one user, one alert, etc.)
#
# This file creates 4 tables:
#   1. users        → everyone who can log in
#   2. transactions → every payment that gets checked
#   3. alerts       → every violation that gets detected
#   4. audit_logs   → a record of every action ever taken
#
# HOW TO RUN THIS FILE:
# ---------------------
# Open your terminal, go to the backend/ folder, and type:
#     python app/database.py
#
# You will see:
#     Creating database tables...
#     + users
#     + transactions
#     + alerts
#     + audit_logs
#     Done! Database file: complianceiq.db
#
# A file called complianceiq.db will appear in your backend/ folder.
# That file IS your database. Everything gets stored inside it.
# You only need to run this file ONCE.
# ============================================================

import os
import uuid
from datetime import datetime

from dotenv import load_dotenv
from sqlalchemy import (
    Boolean, Column, DateTime, Enum,
    Float, Integer, String, Text, create_engine,
)
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

# Load the .env file so we can read DATABASE_URL
# (We create the .env file in a later step)
load_dotenv()

# ── DATABASE CONNECTION ─────────────────────────────────────────────────────
# We use SQLite — it stores everything in ONE local file (complianceiq.db).
# No installation needed. Perfect for development.
DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./complianceiq.db")

engine = create_engine(
    DATABASE_URL,
    connect_args={"check_same_thread": False},
    # ^ This line is required for SQLite only. Remove it if you switch
    #   to PostgreSQL later.
)

# SessionLocal is what you use to read/write the database.
# Think of it like opening a spreadsheet, making changes, then closing it.
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Base is the parent class all your table definitions will inherit from.
Base = declarative_base()


# ── TABLE 1: users ──────────────────────────────────────────────────────────
# Stores every person who can log into the system.
#
# IMPORTANT: We NEVER store plain passwords.
# We store a "hash" — a scrambled version that cannot be reversed.
# Even if someone steals the database, they can't find the passwords.
class User(Base):
    __tablename__ = "users"

    # id: a unique ID auto-generated for each user
    # Looks like: "3f2a1b4c-5d6e-7f8a-9b0c-1d2e3f4a5b6c"
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))

    # email and hashed_password: login credentials
    email = Column(String, unique=True, nullable=False, index=True)
    hashed_password = Column(String, nullable=False)

    # role: controls what this person can do
    #   analyst → can only VIEW alerts
    #   officer → can VIEW + RESOLVE alerts + generate reports
    #   admin   → full control (manage users, view audit logs, etc.)
    role = Column(
        Enum("analyst", "officer", "admin", name="user_role"),
        default="analyst",
        nullable=False,
    )

    # is_active: if False, this person cannot log in
    # (admins use this to disable accounts without deleting them)
    is_active = Column(Boolean, default=True)

    # failed_login_count: after 5 wrong passwords, we lock the account
    failed_login_count = Column(Integer, default=0)
    locked_until = Column(DateTime, nullable=True)

    # timestamps
    created_at = Column(DateTime, default=datetime.utcnow)
    last_login_at = Column(DateTime, nullable=True)


# ── TABLE 2: transactions ───────────────────────────────────────────────────
# Stores every financial transaction submitted for compliance checking.
#
# In a real fintech app, these would stream in from the payment platform.
# In our project, we submit them manually through the dashboard or API.
class Transaction(Base):
    __tablename__ = "transactions"

    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))

    # The actual transaction data
    sender_account = Column(String, nullable=False)
    receiver_account = Column(String, nullable=False)
    amount = Column(Float, nullable=False)           # Amount in Indian Rupees
    transaction_type = Column(
        Enum("transfer", "payment", "withdrawal", "deposit", name="tx_type"),
        default="transfer",
    )

    # These 3 fields are what the ML model uses to detect violations:
    hour_of_day = Column(Integer, nullable=True)
    # 0 = midnight, 14 = 2pm. Transfers at 2am are more suspicious.

    tx_count_7d = Column(Integer, default=1)
    # How many times has this sender transacted this week?
    # 4 transfers each just below ₹10L in one week = structuring pattern.

    kyc_verified = Column(Boolean, default=True)
    # Is the RECEIVER's account KYC verified?
    # KYC = Know Your Customer (government ID verification).

    # Result of the compliance check:
    status = Column(
        Enum("pending", "clean", "flagged", name="tx_status"),
        default="pending",
    )
    # pending → just submitted, not checked yet
    # clean   → checked, no violations found
    # flagged → checked, violations found, an Alert row was created

    # The ML model's suspicion score (0.0 to 1.0)
    risk_score = Column(Float, nullable=True)

    submitted_at = Column(DateTime, default=datetime.utcnow)
    checked_at = Column(DateTime, nullable=True)


# ── TABLE 3: alerts ─────────────────────────────────────────────────────────
# Created whenever a transaction is flagged.
# This is what appears on the compliance officer's dashboard.
class Alert(Base):
    __tablename__ = "alerts"

    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))

    # Which transaction triggered this alert
    transaction_id = Column(String, nullable=False, index=True)

    # How serious is this?
    risk_level = Column(
        Enum("low", "medium", "high", name="risk_level"),
        nullable=False,
    )

    # What kind of violation?
    # Examples: "structuring", "kyc_bypass", "suspicious_overnight"
    violation_type = Column(String, nullable=False)

    # Which exact law was broken?
    # Example: "RBI KYC Master Direction 2023 — Section 16(3)"
    regulation_cited = Column(String, nullable=True)

    # The full alert explanation (written by the AI or rule engine)
    ai_explanation = Column(Text, nullable=True)

    # The top 3 SHAP feature importances, stored as a JSON string
    # Example: '[{"feature":"amount","shap_value":0.41,"impact":"increases_risk"}]'
    # The frontend reads this and draws the SHAP bar chart.
    shap_features_json = Column(Text, nullable=True)

    # Alert lifecycle:
    status = Column(
        Enum("open", "resolved", "escalated", name="alert_status"),
        default="open",
        nullable=False,
    )
    # open      → needs attention from a compliance officer
    # resolved  → officer has reviewed and closed it
    # escalated → needs senior review

    # Filled in when an officer closes the alert:
    resolved_by = Column(String, nullable=True)   # user ID of the officer
    resolved_at = Column(DateTime, nullable=True)
    resolution_notes = Column(Text, nullable=True)

    created_at = Column(DateTime, default=datetime.utcnow)


# ── TABLE 4: audit_logs ─────────────────────────────────────────────────────
# An IMMUTABLE record of every significant action in the system.
# "Immutable" = once written, NEVER updated or deleted. Not even by admins.
# Regulators can ask to see this log as proof the system is working correctly.
#
# Examples of what gets logged:
#   "admin@company.com logged in from IP 103.x.x.x at 09:14am"
#   "officer@company.com resolved alert a3f2-... at 10:32am"
#   "admin@company.com deactivated user john@company.com at 2:15pm"
class AuditLog(Base):
    __tablename__ = "audit_logs"

    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))

    # Who did it? (stores their user ID)
    # None = system did it automatically
    user_id = Column(String, nullable=True, index=True)

    # Short code for what happened — keep these consistent
    # Examples: "login_success", "login_failed", "alert_resolved",
    #           "user_created", "user_deactivated"
    action = Column(String, nullable=False, index=True)

    # Human-readable description
    detail = Column(Text, nullable=True)

    # Their IP address (useful for security investigations)
    ip_address = Column(String, nullable=True)

    # When it happened (stored in UTC time)
    timestamp = Column(DateTime, default=datetime.utcnow, nullable=False)


# ── get_db() ─────────────────────────────────────────────────────────────────
# This function is used by EVERY API route that needs the database.
# FastAPI calls it automatically — you just add it to your route function.
#
# HOW TO USE IT IN A ROUTE (copy this pattern exactly):
#
#   from fastapi import Depends
#   from app.database import get_db
#   from sqlalchemy.orm import Session
#
#   @router.get("/alerts")
#   def list_alerts(db: Session = Depends(get_db)):
#       alerts = db.query(Alert).all()
#       return alerts
#
# The try/finally ensures the connection is ALWAYS closed after each
# request, even if the route crashes with an error.
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


# ── CREATE ALL TABLES ────────────────────────────────────────────────────────
# This block ONLY runs when you type: python app/database.py
# It will NOT run when this file is imported by other files.
if __name__ == "__main__":
    print("Creating database tables...")
    Base.metadata.create_all(bind=engine)
    print("Tables created:")
    for table_name in Base.metadata.tables.keys():
        print(f"  + {table_name}")
    print(f"\nDone! Database file: complianceiq.db")
    print("Next step: run   uvicorn app.main:app --reload")
