from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from app.api.routes import router

app = FastAPI(title="Biometric Cryptosystem API")

# --- 1. Standard CORS Configuration ---
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Matches your Vite frontend URL
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# --- 2. WebAssembly Security Headers Middleware ---
@app.middleware("http")
async def add_security_headers(request: Request, call_next):
    response = await call_next(request)
    # Explicitly allows the frontend (running in require-corp isolation) to read this response
    response.headers["Cross-Origin-Resource-Policy"] = "cross-origin"
    return response

# --- 3. Routes ---
# Include the routes we just created
app.include_router(router, prefix="/api/v1")

@app.get("/")
def health_check():
    return {"status": "System Online"}