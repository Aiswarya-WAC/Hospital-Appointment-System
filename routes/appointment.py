from fastapi import APIRouter, HTTPException
from models import AppointmentBook, AppointmentCancel, InsuranceValidation
from database import doctors, patients, appointments
from bson import ObjectId
from datetime import datetime, timedelta

router = APIRouter()

@router.post("/book/")
def book_appointment(appointment: AppointmentBook):
    # Validate patient
    patient = patients.find_one({"_id": ObjectId(appointment.patient_id)})
    if not patient:
        raise HTTPException(status_code=404, detail="Patient not found")

    # Validate doctor and availability
    doctor = doctors.find_one({"_id": ObjectId(appointment.doctor_id)})
    if not doctor:
        raise HTTPException(status_code=404, detail="Doctor not found")

    if appointment.appointment_time not in doctor["available_slots"]:
        raise HTTPException(status_code=400, detail="Selected time slot is not available")

    # Validate insurance
    if patient["insurance_type"] != appointment.insurance_type:
        raise HTTPException(status_code=400, detail="Insurance type mismatch")
    
    if not patient["insurance_validity"]:
        raise HTTPException(status_code=400, detail="Insurance is not valid")

    # Set priority
    priority = "High" if appointment.insurance_type == "Premium" or appointment.is_emergency else "Normal"

    # Create appointment
    appointment_data = {
        "patient_id": appointment.patient_id,
        "doctor_id": appointment.doctor_id,
        "appointment_time": appointment.appointment_time,
        "status": "confirmed",
        "priority": priority,
        "symptoms": appointment.symptoms,
        "preferred_language": appointment.preferred_language,
        "created_at": datetime.utcnow(),
        "follow_up_suggested": (datetime.utcnow() + timedelta(days=7)).strftime("%Y-%m-%d")
    }

    # Insert appointment and update doctor's slots
    result = appointments.insert_one(appointment_data)
    
    # Remove booked slot from available slots
    doctors.update_one(
        {"_id": ObjectId(appointment.doctor_id)},
        {"$pull": {"available_slots": appointment.appointment_time}}
    )

    return {
        "status": "confirmed",
        "appointment_id": str(result.inserted_id),
        "doctor": doctor["name"],
        "patient": patient["name"],
        "appointment_time": appointment.appointment_time,
        "priority": priority,
        "follow_up_suggested": appointment_data["follow_up_suggested"]
    }

from datetime import datetime


@router.post("/cancel/")
def cancel_appointment(cancellation: AppointmentCancel):
    # Fetch the appointment from the database
    appointment = appointments.find_one({"_id": ObjectId(cancellation.appointment_id)})
    if not appointment:
        raise HTTPException(status_code=404, detail="Appointment not found")
    
    # Check if cancellation_time is already a datetime object or a string
    if isinstance(cancellation.cancellation_time, str):
        try:
            # Convert the cancellation time string to a datetime object
            cancellation_time = datetime.strptime(cancellation.cancellation_time, "%Y-%m-%dT%H:%M:%S")
        except ValueError:
            raise HTTPException(status_code=400, detail="Invalid cancellation time format")
    elif isinstance(cancellation.cancellation_time, datetime):
        cancellation_time = cancellation.cancellation_time
    else:
        raise HTTPException(status_code=400, detail="Invalid cancellation time type")

    # Fetch the appointment time and convert it to a datetime object
    appointment_time_str = appointment["appointment_time"]
    try:
        # Convert the appointment time from string to datetime by adding today's date
        appointment_time = datetime.strptime(appointment_time_str, "%I:%M %p")  # e.g., '5:00 PM'
        appointment_time = appointment_time.replace(year=cancellation_time.year,
                                                     month=cancellation_time.month,
                                                     day=cancellation_time.day)
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid appointment time format")

    # Check if cancellation is within 1 hour of the appointment time
    time_difference = appointment_time - cancellation_time
    cancellation_fee = 100 if time_difference <= timedelta(hours=1) else 0

    # Return the slot to the doctor's available slots
    doctors.update_one(
        {"_id": ObjectId(appointment['doctor_id'])},
        {"$push": {"available_slots": appointment['appointment_time']}}
    )

    # Remove the appointment from the database
    appointments.delete_one({"_id": ObjectId(cancellation.appointment_id)})

    return {
        "status": "cancelled",
        "cancellation_fee": cancellation_fee
    }

@router.get("/appointments/")
def get_all_appointments():
    # Fetch all appointments from the database
    all_appointments = appointments.find()  # This retrieves all appointments

    # If no appointments are found, return an appropriate response
    if not all_appointments:
        raise HTTPException(status_code=404, detail="No appointments found")

    # Convert MongoDB cursor to a list of dictionaries, and prepare the response
    appointment_list = []
    for appointment in all_appointments:
        # Convert ObjectId to string for JSON compatibility
        appointment_data = {
            "appointment_id": str(appointment["_id"]),
            "patient_id": appointment["patient_id"],
            "doctor_id": appointment["doctor_id"],
            "appointment_time": appointment["appointment_time"],
            "status": appointment["status"],
            "priority": appointment["priority"],
            "symptoms": appointment["symptoms"],
            "preferred_language": appointment["preferred_language"],
            "created_at": appointment["created_at"],
            "follow_up_suggested": appointment["follow_up_suggested"]
        }
        appointment_list.append(appointment_data)

    return {"appointments": appointment_list}
