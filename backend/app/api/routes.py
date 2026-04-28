from fastapi import APIRouter, UploadFile, File, Form
from app.controllers import biometric_controller

router = APIRouter()

@router.post("/enroll")
async def enroll_endpoint(
    username: str = Form(...),
    password: str = Form(...),
    video_file: UploadFile = File(...),
    audio_file: UploadFile = File(...)
):
    """
    Signs up a new user using their 3-factor authentication data.
    """
    return await biometric_controller.enroll_user(
        username=username, 
        password=password, 
        video_file=video_file, 
        audio_file=audio_file
    )

@router.post("/login")
async def login_endpoint(
    username: str = Form(...),
    password: str = Form(...),
    video_file: UploadFile = File(...),
    audio_file: UploadFile = File(...)
):
    """
    Authenticates a returning user via the Fuzzy Commitment Scheme.
    """
    return await biometric_controller.login_user(
        username=username, 
        password=password, 
        video_file=video_file, 
        audio_file=audio_file
    )