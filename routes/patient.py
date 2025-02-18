from fastapi import APIRouter, Depends, HTTPException
from models import Patient
from database import patients
from auth import verify_admin_token
from bson import ObjectId

router = APIRouter()

# Admin can add a patient
@router.post("/add/")
def add_patient(patient: Patient, admin: str = Depends(verify_admin_token)):
    if patient.insurance_type not in ["Standard", "Premium"]:
        raise HTTPException(status_code=400, detail="Invalid insurance type")

    # Create the patient data, use ObjectId for _id in MongoDB
    patient_data = patient.dict()
    inserted_patient = patients.insert_one(patient_data)

    # Return the ID of the newly added patient
    return {"message": "Patient added successfully", "patient_id": str(inserted_patient.inserted_id)}

# Get all patients
@router.get("/all/")
def get_all_patients():
    all_patients = list(patients.find({}, {"_id": 1, "name": 1, "age": 1, "insurance_type": 1, "insurance_validity": 1}))
    for pat in all_patients:
        pat["_id"] = str(pat["_id"])  # Convert ObjectId to string for easy handling
    return all_patients
