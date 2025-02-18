from fastapi import FastAPI
from routes import admin, doctor, patient

app = FastAPI()

# Include Routers
from routes import appointment

app.include_router(appointment.router, prefix="/api/appointment", tags=["Appointment"])
from routes import insurance  # Import the insurance router
app.include_router(insurance.router, prefix="/api/insurance", tags=["Insurance"])

app.include_router(admin.router, prefix="/api/admin", tags=["Admin"])
app.include_router(doctor.router, prefix="/api/doctor", tags=["Doctor"])
app.include_router(patient.router, prefix="/api/patient", tags=["Patient"])

@app.get("/")
def home():
    return {"message": "Welcome to the Hospital Appointment System"}
