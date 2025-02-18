from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime

class Doctor(BaseModel):
    name: str
    specialization: str
    available_slots: List[str]  # Now only contains time slots like "10:30 AM"

class Patient(BaseModel):
    name: str
    age: int
    insurance_type: str
    insurance_validity: bool

class AppointmentBook(BaseModel):
    patient_id: str
    doctor_id: str
    appointment_time: str
    is_emergency: bool = False
    insurance_type: str
    symptoms: List[str]
    preferred_language: str
    previous_appointment_id: Optional[str] = None

class AppointmentCancel(BaseModel):
    appointment_id: str
    cancellation_time: datetime

class InsuranceValidation(BaseModel):
    insurance_type: str
    patient_id: str
# Model for Admin Login
class AdminLogin(BaseModel):
    username: str
    password: str
