from fastapi import FastAPI
from app.api.routes import router

app = FastAPI(title="Biometric Cryptosystem API")

# Include the routes we just created
app.include_router(router, prefix="/api/v1")

@app.get("/")
def health_check():
    return {"status": "System Online"}