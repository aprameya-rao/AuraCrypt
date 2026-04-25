from fastapi import APIRouter, UploadFile, File
from app.controllers import biometric_controller

router = APIRouter()

@router.post("/extract-kinetic")
async def extract_kinetic_endpoint(file: UploadFile = File(...)):
    """
    Endpoint to receive a user's hand-swipe video and return the normalized matrix.
    """
    return await biometric_controller.process_kinetic_upload(file)

@router.post("/extract-audio")
async def extract_audio_endpoint(file: UploadFile = File(...)):
    """
    Endpoint to receive a user's voice recording and return the binarized matrix.
    """
    return await biometric_controller.process_audio_upload(file)