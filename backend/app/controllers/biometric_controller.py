import os
import tempfile
import numpy as np
from fastapi import UploadFile, Form, HTTPException
from fastapi.concurrency import run_in_threadpool

from app.services.video_processor import kinetic_service
from app.services.audio_processor import audio_service
from app.services.crypto_service import crypto_service
from app.services.bch_encoder import bch_encoder
from app.services.bch_decoder import bch_decoder

# ==========================================
# MOCK DATABASE (Replace with SQLite later)
# ==========================================
# Stores username as key, and the 4216-bit Locked Data array as value
MOCK_DB = {} 
# ==========================================

async def _extract_biometrics(video_file: UploadFile, audio_file: UploadFile) -> np.ndarray:
    """Helper function to extract and merge the 4216-bit biometric key."""
    # 1. Process Video
    video_temp_path = ""
    try:
        # THE FIX: Grab the actual extension (.webm, .mp4, etc)
        file_ext = os.path.splitext(video_file.filename)[1] or ".mp4"
        
        with tempfile.NamedTemporaryFile(delete=False, suffix=file_ext) as temp_video:
            content = await video_file.read()
            temp_video.write(content)
            video_temp_path = temp_video.name
            
        kinetic_array = await run_in_threadpool(kinetic_service.process_video, video_temp_path)
    finally:
        if os.path.exists(video_temp_path):
            os.remove(video_temp_path)

    # 2. Process Audio
    audio_bytes = await audio_file.read()
    audio_array = await run_in_threadpool(audio_service.extract_binary_features, audio_bytes)

    # 3. Combine and Pad to strictly 4216 bits
    master_key = await run_in_threadpool(
        crypto_service.create_master_biometric_key, kinetic_array, audio_array
    )
    return master_key

async def enroll_user(username: str, password: str, video_file: UploadFile, audio_file: UploadFile):
    """
    Phase 1: Generates the Master Key, hashes the password, encodes it, 
    locks it via XOR, and stores it in the database.
    """
    if username in MOCK_DB:
        raise HTTPException(status_code=400, detail="User already exists.")

    try:
        # 1. Get 4216-bit Biometric Key (B)
        biometric_key = await _extract_biometrics(video_file, audio_file)

        # 2. Generate 256-bit TitanHash of the password
        password_hash = await run_in_threadpool(crypto_service.titan_hash_password, password)

        # 3. Bloat hash into 4216-bit Codeword (C) using BCH
        codeword = await run_in_threadpool(bch_encoder.encode, password_hash)

        # 4. The Lock: XOR the Codeword and the Biometric Key
        locked_data = np.bitwise_xor(codeword, biometric_key)

        # 5. Save to Database (Convert to list for mock DB storage, or BLOB for SQLite)
        MOCK_DB[username] = locked_data.tolist()

        return {"status": "success", "message": f"User {username} securely enrolled."}

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Enrollment failed: {str(e)}")

async def login_user(username: str, password: str, video_file: UploadFile, audio_file: UploadFile):
    """
    Phase 2: Extracts new biometrics, XORs with database lock, 
    decodes the noise, and verifies the restored password hash.
    """
    if username not in MOCK_DB:
        raise HTTPException(status_code=404, detail="User not found.")

    try:
        # 1. Get the NEW 4216-bit Biometric Key (B') - Contains ~6% noise
        new_biometric_key = await _extract_biometrics(video_file, audio_file)

        # 2. Fetch the Locked Data from the database
        locked_data = np.array(MOCK_DB[username], dtype=np.uint8)

        # 3. The Unlock: XOR the Locked Data with the new Biometrics
        # Result = Corrupted Codeword (C')
        corrupted_codeword = np.bitwise_xor(locked_data, new_biometric_key)

        live_password_hash_debug = await run_in_threadpool(crypto_service.titan_hash_password, password)
        pure_codeword_debug = await run_in_threadpool(bch_encoder.encode, live_password_hash_debug)
        actual_noise_vector = np.bitwise_xor(corrupted_codeword, pure_codeword_debug)
        total_errors = np.sum(actual_noise_vector)
        print(f"\n=============================================")
        print(f"DIAGNOSTIC: Actual Biometric Errors: {total_errors} / 4876")
        print(f"Max Allowed by GF(2^14): {bch_decoder.t}")
        print(f"=============================================\n")
        # ------------------------------
        # 4. The Math Magic: Decode to strip noise and restore the 256-bit hash
        try:
            restored_hash = await run_in_threadpool(bch_decoder.decode, corrupted_codeword)
        except ValueError as e:
            # If noise > 10%, the decoder throws a ValueError. Access Denied.
            raise HTTPException(status_code=401, detail=f"Biometric verification failed: {str(e)}")

        # 5. Hash the typed password to compare
        live_password_hash = await run_in_threadpool(crypto_service.titan_hash_password, password)

        # 6. Final Security Check
        if np.array_equal(restored_hash, live_password_hash):
            return {"status": "success", "message": "Access Granted. Identity verified."}
        else:
            raise HTTPException(status_code=401, detail="Invalid password.")

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Login processing error: {str(e)}")