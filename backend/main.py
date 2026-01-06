
import os
from fastapi import FastAPI, Form, HTTPException
from fastapi.responses import FileResponse, RedirectResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel
from typing import List, Optional
from database import add_user, get_user, get_all_users
from auth import router as auth_router  # your auth routes
# ----------------------
# Directories
# ----------------------
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
FRONTEND_DIR = os.path.join(BASE_DIR, "..", "frontend")
STATIC_DIR = os.path.join(FRONTEND_DIR, "static")

# ----------------------
# FastAPI app
# ----------------------
app = FastAPI(
    title="ParentSpark API",
    description="Backend for dating website for single parents",
)
app.mount("/static", StaticFiles(directory=STATIC_DIR), name="static")

# ----------------------
# User Model
# ----------------------
class User(BaseModel):
    email: str
    password: str

# ----------------------
# HTML Pages
# ----------------------
@app.get("/")
@app.get("/home.html")
def home():
    return FileResponse(os.path.join(FRONTEND_DIR, "home.html"))

@app.get("/login.html")
def login_page():
    return FileResponse(os.path.join(FRONTEND_DIR, "login.html"))

@app.get("/register.html")
def register_page():
    return FileResponse(os.path.join(FRONTEND_DIR, "register.html"))

@app.get("/profile.html")
def profile():
    return FileResponse(os.path.join(FRONTEND_DIR, "profile.html"))

@app.get("/profile-detail.html")
def profile_detail():
    return FileResponse(os.path.join(FRONTEND_DIR, "profile_detail.html"))


@app.get("/comingup.html")
def comingup():
    return FileResponse(os.path.join(FRONTEND_DIR, "comingup.html"))
# ----------------------
# API Endpoints
# ----------------------

# GET → Read all users
@app.get("/all_users")
def get_users():
    return {"users": get_all_users()}


@app.post("/login")
def login(email: str = Form(...), password: str = Form(...)):
    user = get_user(email)
    if user and user["password"] == password:
        return RedirectResponse(url=f"/profile.html?user={email}", status_code=303)
    raise HTTPException(status_code=400, detail="Invalid credentials")

# POST → Register a new user
@app.post("/register_user")
def create_user(email: str = Form(...), password: str = Form(...)):
    print(f"Registering user: {email}")
    if not add_user(email, password):
        raise HTTPException(status_code=400, detail="User already exists")
    return RedirectResponse(url=f"/profile.html?user={email}", status_code=303)

@app.post("/feedback_suggestion")
async def feedback_suggestion(message: str = Form(...)):
    # Mock suggestion for testing
    suggested_text = f"Mock AI Suggestion: Try improving this: '{message[:30]}...'"
    return {"suggestion": suggested_text}

@app.post("/feedback_submit")
async def feedback_submit(message: str = Form(...)):
    try:
        return JSONResponse({"received": message})
    except Exception as exc:
        import traceback
        traceback.print_exc()
        return JSONResponse({"error": str(exc)}, status_code=500)

# Include auth router
app.include_router(auth_router)
