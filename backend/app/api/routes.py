import time
from datetime import datetime
from fastapi import APIRouter, UploadFile, File, Form, HTTPException
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
    # 1. TIMESTAMP: When the network request officially hits FastAPI
    start_time = time.perf_counter()
    timestamp_str = datetime.now().strftime("%H:%M:%S.%f")[:-3]
    
    print(f"\n" + "="*60)
    print(f"📝 AURACRYPT PROFILER: NEW ENROLLMENT EVENT")
    print("="*60)
    print(f"User:           {username}")
    print(f"Time Received:  {timestamp_str}")
    print("-" * 60)

    try:
        # 2. EXECUTION: Await the heavy lifting from the controller
        response = await biometric_controller.enroll_user(
            username=username, 
            password=password, 
            video_file=video_file, 
            audio_file=audio_file
        )
        
        # 3. TIMESTAMP: When the backend is completely finished
        end_time = time.perf_counter()
        total_api_latency = (end_time - start_time) * 1000
        
        print("-" * 60)
        print(f"✅ ENROLLMENT SUCCESSFUL")
        print(f"TOTAL API ROUND-TRIP: {total_api_latency:.2f} ms")
        print("="*60 + "\n")
        
        return response

    except Exception as e:
        # Log the failure time
        end_time = time.perf_counter()
        total_api_latency = (end_time - start_time) * 1000
        
        print("-" * 60)
        print(f"❌ ENROLLMENT FAILED: {str(e)}")
        print(f"TOTAL API ROUND-TRIP: {total_api_latency:.2f} ms")
        print("="*60 + "\n")
        
        raise HTTPException(status_code=400, detail=str(e))


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
    # 1. TIMESTAMP: When the network request officially hits FastAPI
    start_time = time.perf_counter()
    timestamp_str = datetime.now().strftime("%H:%M:%S.%f")[:-3]
    
    print(f"\n" + "="*60)
    print(f"🚀 AURACRYPT PROFILER: NEW LOGIN EVENT")
    print("="*60)
    print(f"User:           {username}")
    print(f"Time Received:  {timestamp_str}")
    print("-" * 60)

    try:
        # 2. EXECUTION: Await the heavy lifting from the controller
        response = await biometric_controller.login_user(
            username=username, 
            password=password, 
            video_file=video_file, 
            audio_file=audio_file
        )
        
        # 3. TIMESTAMP: When the backend is completely finished
        end_time = time.perf_counter()
        total_api_latency = (end_time - start_time) * 1000
        
        print("-" * 60)
        print(f"TOTAL API ROUND-TRIP: {total_api_latency:.2f} ms")
        print("="*60 + "\n")
        
        return response

    except Exception as e:
        # If the login fails (e.g., Uncorrectable Error Pattern), we still want to log the failure time!
        end_time = time.perf_counter()
        total_api_latency = (end_time - start_time) * 1000
        
        print("-" * 60)
        print(f"❌ AUTHENTICATION FAILED: {str(e)}")
        print(f"TOTAL API ROUND-TRIP: {total_api_latency:.2f} ms")
        print("="*60 + "\n")
        
        raise HTTPException(status_code=400, detail=str(e))