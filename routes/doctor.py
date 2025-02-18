from fastapi import APIRouter, Depends, HTTPException
from models import Doctor
from database import doctors
from auth import verify_admin_token
from bson import ObjectId

router = APIRouter()

# Admin can add a doctor
@router.post("/add/")
def add_doctor(doctor: Doctor, admin: str = Depends(verify_admin_token)):
    doctor_data = doctor.dict()
    inserted_doc = doctors.insert_one(doctor_data)
    return {"message": "Doctor added successfully", "doctor_id": str(inserted_doc.inserted_id)}

# Get all doctors
@router.get("/all/")
def get_all_doctors():
    all_doctors = list(doctors.find({}, {"_id": 1, "name": 1, "specialization": 1, "available_slots": 1}))
    for doc in all_doctors:
        doc["_id"] = str(doc["_id"])
    return all_doctors


# Check doctor availability
@router.get("/availability/{doctor_id}")
def check_doctor_availability(doctor_id: str):
    doctor = doctors.find_one({"_id": ObjectId(doctor_id)}, {"available_slots": 1})
    if not doctor:
        raise HTTPException(status_code=404, detail="Doctor not found")
    return {"doctor_id": doctor_id, "available_slots": doctor["available_slots"]}
