import os
import tempfile
from fastapi import UploadFile, HTTPException
from app.services.video_processor import KineticBiometricService

# Instantiate our service
kinetic_service = KineticBiometricService()

async def process_kinetic_upload(file: UploadFile):
    """
    Validates the video file and orchestrates the biometric extraction.
    """
    # 1. Security Check: Ensure it's actually a video file
    if not file.content_type.startswith("video/"):
        raise HTTPException(status_code=400, detail="Invalid file type. Video required.")

    temp_path = ""
    try:
        # 2. Save file temporarily to disk (OpenCV cannot read raw FastAPI byte streams)
        with tempfile.NamedTemporaryFile(delete=False, suffix=".mp4") as temp_video:
            content = await file.read()
            temp_video.write(content)
            temp_path = temp_video.name

        # 3. The Handoff: Pass the file path to our pure Python math service
        final_1d_matrix = kinetic_service.process_video(temp_path)

        # 4. Return success (Convert a small sample to list so JSON can serialize it)
        return {
            "status": "success",
            "message": "Kinetic biometric extracted and normalized.",
            "matrix_size": final_1d_matrix.shape[0],
            "data_sample": final_1d_matrix[:5].tolist() # Just the first 5 coordinates for verification
        }

    except ValueError as e:
        # Caught an expected error (e.g., "No hands detected")
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        # Caught an unexpected backend crash
        raise HTTPException(status_code=500, detail="Internal processing error.")
    finally:
        # 5. Cleanup: NEVER leave biometric video files sitting on the server
        if os.path.exists(temp_path):
            os.remove(temp_path)