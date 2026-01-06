# auth.py
from fastapi import APIRouter, HTTPException, Form
from pydantic import BaseModel, EmailStr
import sqlite3
import hashlib

router = APIRouter(prefix="/auth", tags=["Authentication"])

DB_FILE = "users.db"  # SQLite database file

# ----------------------
# Models
# ----------------------
class RegisterModel(BaseModel):
    username: str
    email: EmailStr
    password: str

class LoginModel(BaseModel):
    email: EmailStr
    password: str

# ----------------------
# Helper functions
# ----------------------
def hash_password(password: str) -> str:
    return hashlib.sha256(password.encode()).hexdigest()

def create_users_table():
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()
    c.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT NOT NULL,
            email TEXT UNIQUE NOT NULL,
            password TEXT NOT NULL
        )
    """)
    conn.commit()
    conn.close()

create_users_table()  # Ensure table exists

# ----------------------
# Routes
# ----------------------
@router.post("/register")
def register(user: RegisterModel):
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()
    hashed = hash_password(user.password)
    try:
        c.execute(
            "INSERT INTO users (username, email, password) VALUES (?, ?, ?)",
            (user.username, user.email, hashed)
        )
        conn.commit()
    except sqlite3.IntegrityError:
        conn.close()
        raise HTTPException(status_code=400, detail="Email already registered")
    
    conn.close()
    return {"message": f"User {user.username} registered successfully!"}

@router.post("/login")
def login(user: LoginModel):
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()
    c.execute("SELECT username, password FROM users WHERE email=?", (user.email,))
    row = c.fetchone()
    conn.close()

    if not row:
        raise HTTPException(status_code=404, detail="User not found")

    username, stored_password = row
    if stored_password != hash_password(user.password):
        raise HTTPException(status_code=401, detail="Incorrect password")

    return {"message": "Login successful", "username": username}
