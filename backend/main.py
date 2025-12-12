import os
from fastapi import FastAPI, Form, HTTPException
from fastapi.responses import FileResponse, RedirectResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel
from typing import List, Optional
from auth import router as auth_router  # your auth routes
from openai import OpenAI
#client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

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

# In-memory users list
users: List[User] = []

# ----------------------
# HTML Pages
# ----------------------
@app.get("/home.html")
def home():
    return FileResponse(os.path.join(FRONTEND_DIR, "home.html"))

@app.get("/login.html")
def serve_login():
    return FileResponse(os.path.join(FRONTEND_DIR, "login.html"))

@app.get("/register.html")
def serve_register():
    return FileResponse(os.path.join(FRONTEND_DIR, "register.html"))

@app.get("/comingup.html")
def comingup():
    return FileResponse(os.path.join(FRONTEND_DIR, "comingup.html"))
# ----------------------
# API Endpoints
# ----------------------

@app.get("/")
def read_root():
    return FileResponse(os.path.join(FRONTEND_DIR, "index.html"))

# GET → Read all users
@app.get("/all_users")
def get_users():
    return {"users": [user.email for user in users]}

# POST → Register a new user
@app.post("/register_user")
def create_user(email: str = Form(...), password: str = Form(...)):
    print(f"Registering user: {email}")
    if any(user.email == email for user in users):
        raise HTTPException(status_code=400, detail="User already exists")
    users.append(User(email=email, password=password))
    return {"message": "User created successfully", "email": email}

# PUT → Update user
@app.put("/update_user")
def update_user(
    email: str = Form(...),
    new_email: Optional[str] = Form(None),
    new_password: Optional[str] = Form(None)
):
    for user in users:
        if user.email == email:
            if new_email:
                if any(x.email == new_email for x in users):
                    raise HTTPException(status_code=400, detail="New email already exists")
                user.email = new_email
            if new_password:
                user.password = new_password
            return {"message": "User updated successfully", "email": user.email}
    raise HTTPException(status_code=404, detail="User not found")

# DELETE → Delete user
@app.delete("/delete_user")
def delete_user(email: str = Form(...)):
    for user in users:
        if user.email == email:
            users.remove(user)
            return {"message": "User deleted successfully"}
    raise HTTPException(status_code=404, detail="User not found")

# Login (still POST)
@app.post("/login")
def login(email: str = Form(...), password: str = Form(...)):
    for user in users:
        if user.email == email and user.password == password:
            return RedirectResponse(url="home.html", status_code=303)
    raise HTTPException(status_code=400, detail="Invalid credentials")


# In-memory feedback storage
feedback_list = []


# @app.post("/feedback_suggestion")
# async def feedback_suggestion(message: str = Form(...)):
#     try:
#         # Save incoming feedback locally
#         feedback_list.append(message)

#         # If OpenAI client is configured with a sensible ASCII key, call it; otherwise fall back
#         key = os.getenv("OPENAI_API_KEY")
#         key_ok = bool(key) and all(ord(c) < 128 for c in key)
#         if client and key_ok:
#             response = client.chat.completions.create(
#                 model="gpt-4o-mini",
#                 messages=[
#                     {"role": "system", "content": "You generate short helpful feedback suggestions."},
#                     {"role": "user", "content": message}
#                 ]
#             )
#             # Try to extract the suggestion from the OpenAI response
#             suggestion = response.choices[0].message["content"]
#             return JSONResponse({"suggestion": suggestion})

#         # Fallback behavior when API key / client not available
#         suggested_text = f"Suggested improvement: Try to be more specific about '{message[:30]}...'"
#         return JSONResponse({"suggestion": suggested_text})

#     except Exception as exc:
#         # Log full traceback to server logs for debugging
#         import traceback
#         traceback.print_exc()
#         return JSONResponse({"error": str(exc)}, status_code=500)



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
