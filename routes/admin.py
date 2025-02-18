from fastapi import APIRouter, HTTPException, Depends
from models import AdminLogin
from auth import create_access_token
from database import admins

router = APIRouter()

# Dummy admin account (for testing)
DUMMY_ADMIN = {"username": "admin", "password": "admin123"}

# Admin login
@router.post("/login/")
def admin_login(admin: AdminLogin):
    if admin.username == DUMMY_ADMIN["username"] and admin.password == DUMMY_ADMIN["password"]:
        token = create_access_token({"sub": admin.username})
        return {"access_token": token, "token_type": "bearer"}
    raise HTTPException(status_code=401, detail="Invalid credentials")
