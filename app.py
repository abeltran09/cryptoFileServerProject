from fastapi import FastAPI, Request, Form, HTTPException, Depends
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
import hashlib
import json
import os
from typing import Optional
from dataHandler import load_data, save_data
import auth

app = FastAPI()

# Set up templates directory
templates = Jinja2Templates(directory="templates")


@app.get("/change-password", response_class=HTMLResponse)
async def password_form(request: Request, username: str, temp_token: str):
    # Load user data
    data = load_data()

    # Validate username and token
    if username not in data["users"]:
        return templates.TemplateResponse("error.html", {
            "request": request,
            "message": "User not found"
        })

    if data["users"][username]["temp_token"] != temp_token:
        return templates.TemplateResponse("error.html", {
            "request": request,
            "message": "Invalid or expired token"
        })

    # Render password change form
    return templates.TemplateResponse("change_password.html", {
        "request": request,
        "username": username,
        "temp_token": temp_token
    })


@app.post("/change-password", response_class=HTMLResponse)
async def change_password(
        request: Request,
        username: str = Form(...),
        temp_token: str = Form(...),
        old_password: str = Form(...),
        password: str = Form(...),
        confirm_password: str = Form(...)
                        ):

    # Load user data
    data = load_data()

    # Validate user exists
    if username not in data["users"]:
        return templates.TemplateResponse("change_password.html", {
            "request": request,
            "username": username,
            "temp_token": temp_token,
            "error": "User not found"
        })

    # Validate token
    if data["users"][username]["temp_token"] != temp_token:
        return templates.TemplateResponse("change_password.html", {
            "request": request,
            "username": username,
            "temp_token": temp_token,
            "error": "Invalid or expired token"
        })

    # Verify old password
    if not auth.verify_password(old_password, data["users"][username]["hashed_password"]):
        return templates.TemplateResponse("change_password.html", {
            "request": request,
            "username": username,
            "temp_token": temp_token,
            "error": "Current password is incorrect"
        })

    # Validate new password
    if password != confirm_password:
        return templates.TemplateResponse("change_password.html", {
            "request": request,
            "username": username,
            "temp_token": temp_token,
            "error": "New passwords do not match"
        })

    if len(password) < 8:
        return templates.TemplateResponse("change_password.html", {
            "request": request,
            "username": username,
            "temp_token": temp_token,
            "error": "New password must be at least 8 characters"
        })

    # Hash the new password
    new_password_hash = auth.hash_password(password)

    # Update user data
    data["users"][username]["hashed_password"] = new_password_hash
    data["users"][username]["temp_token"] = ""  # Clear temporary token

    # Save updated data
    save_data(data)

    # Redirect to success page
    return RedirectResponse(url="/password-success", status_code=303)


@app.get("/password-success", response_class=HTMLResponse)
async def success_page(request: Request):
    return templates.TemplateResponse("success.html", {"request": request})