from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel, Field
from database import patients
from bson import ObjectId
from typing import Optional

router = APIRouter()

# Pydantic model for the request body
class InsuranceValidation(BaseModel):
    patient_id: str = Field(..., description="The patient ID (MongoDB ObjectId)")
    insurance_type: str
    # Make insurance_validity required (remove Optional)

    # Custom validator for patient_id to ensure it's an ObjectId
    @classmethod
    def validate_patient_id(cls, value: str):
        try:
            return ObjectId(value)  # Try converting string to ObjectId
        except Exception as e:
            raise ValueError(f"Invalid patient_id format: {e}")
            
    class Config:
        json_encoders = {ObjectId: str}  # Ensure ObjectId is serialized as string

@router.post("/validate_insurance")
def validate_insurance(request: InsuranceValidation):
    # Convert the patient_id to ObjectId
    patient_id = ObjectId(request.patient_id)

    patient = patients.find_one({"_id": patient_id})

    if not patient:
        raise HTTPException(status_code=404, detail="Patient not found")

    if patient.get("insurance_type", "").lower() != request.insurance_type.lower():
        raise HTTPException(status_code=400, detail="Insurance type does not match")

    priority = "High" if request.insurance_type.lower() == "premium" else "Low"

    return {
        "patient_id": str(patient["_id"]),
        "insurance_type": patient["insurance_type"],
        "priority": priority,
        "insurance_validity": patient["insurance_validity"]
    }
