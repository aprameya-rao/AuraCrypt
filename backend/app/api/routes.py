from fastapi import APIRouter, UploadFile, File
from app.controllers import biometric_controller

router = APIRouter()

@router.post("/extract-kinetic")
async def extract_kinetic_endpoint(file: UploadFile = File(...)):
    """
    Endpoint to receive a user's hand-swipe video and return the normalized matrix.
    """
    return await biometric_controller.process_kinetic_upload(file)