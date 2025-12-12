from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, EmailStr
import hashlib

router = APIRouter(prefix="/auth", tags=["Authentication"])

# Temporary in-memory database
users_db = {}

# Models
class RegisterModel(BaseModel):
    username: str
    email: EmailStr
    password: str

class LoginModel(BaseModel):
    email: EmailStr
    password: str

def hash_password(password: str):
    return hashlib.sha256(password.encode()).hexdigest()

# Register API
@router.post("/register")
def register(user: RegisterModel):
    if user.email in users_db:
        raise HTTPException(status_code=400, detail="Email already registered")
    
    users_db[user.email] = {
        "username": user.username,
        "password": hash_password(user.password)
    }

    return {"message": f"User {user.username} registered successfully!"}

# Login API
@router.post("/login")
def login(user: LoginModel):
    if user.email not in users_db:
        raise HTTPException(status_code=404, detail="User not found")

    hashed = hash_password(user.password)

    if users_db[user.email]["password"] != hashed:
        raise HTTPException(status_code=401, detail="Incorrect password")

    return {"message": "Login successful", "username": users_db[user.email]["username"]}
