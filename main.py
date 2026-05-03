from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from pydantic import BaseModel
from sqlalchemy import Column, Integer, String, DateTime, create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
import datetime
import pandas as pd
import os
import json # Added for logging formatting

# --- DATABASE ---
DATABASE_URL = "sqlite:///./prescriptions.db"
engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

class Prescription(Base):
    __tablename__ = "prescriptions"
    prescription_id = Column(Integer, primary_key=True, index=True)
    appointment_id = Column(Integer)
    patient_id = Column(Integer)
    doctor_id = Column(Integer)
    medication = Column(String)
    dosage = Column(String)
    days = Column(Integer)
    issued_at = Column(DateTime)

Base.metadata.create_all(bind=engine)

# --- COMPLIANCE LOGGING (PII MASKING) ---
def log_compliance_event(message, data):
    # Masking the patient_id for security compliance
    masked_data = data.copy()
    if "patient_id" in masked_data:
        masked_data["patient_id"] = "***"
    
    log_entry = {
        "timestamp": str(datetime.datetime.utcnow()),
        "event": message,
        "details": masked_data
    }
    # This prints directly to Docker/Terminal logs
    print(f"COMPLIANCE_LOG: {json.dumps(log_entry)}")

# --- APP SETUP ---
app = FastAPI()
templates = Jinja2Templates(directory="templates")

# --- SEEDING DATA ---
@app.on_event("startup")
def seed_data():
    db = SessionLocal()
    if db.query(Prescription).first() is None:
        csv_path = "hms_prescriptions_indian.csv"
        if os.path.exists(csv_path):
            df = pd.read_csv(csv_path)
            for _, row in df.iterrows():
                p = Prescription(
                    prescription_id=int(row['prescription_id']),
                    appointment_id=int(row['appointment_id']),
                    patient_id=int(row['patient_id']),
                    doctor_id=int(row['doctor_id']),
                    medication=str(row['medication']),
                    dosage=str(row['dosage']),
                    days=int(row['days']),
                    issued_at=pd.to_datetime(row['issued_at'])
                )
                db.add(p)
            db.commit()
            print("SUCCESS: CSV Data Seeded (220 records).")
    db.close()

# --- ROUTES ---

@app.get("/", response_class=HTMLResponse)
async def serve_frontend(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})

@app.get("/v1/prescriptions")
def get_prescriptions():
    db = SessionLocal()
    data = db.query(Prescription).order_by(Prescription.prescription_id.desc()).all()
    db.close()
    return data

class PrescriptionCreate(BaseModel):
    appointment_id: int
    patient_id: int
    doctor_id: int
    medication: str
    dosage: str
    days: int

@app.post("/v1/prescriptions")
async def create_prescription(payload: PrescriptionCreate):
    db = SessionLocal()
    new_presc = Prescription(**payload.dict(), issued_at=datetime.datetime.utcnow())
    db.add(new_presc)
    db.commit()
    db.refresh(new_presc)
    
    # --- TRIGGER THE LOG MESSAGE ---
    log_compliance_event("PRESCRIPTION_CREATED", payload.dict())
    
    db.close()
    return new_presc