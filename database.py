from pymongo import MongoClient

# Connect to MongoDB
client = MongoClient("mongodb://localhost:27017/")
db = client.hospital

# Collections
doctors = db.doctors
patients = db.patients
admins = db.admins  # For admin authentication
appointments = db.appointments

