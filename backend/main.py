# from fastapi import FastAPI, UploadFile, File
import uvicorn
from backend.auth.auth_routes import router as auth_router

from fastapi import FastAPI
from backend.database.config import engine, Base
from backend.database import models  # 👈 Ye import sabse zaroori hai!
from backend.auth.auth_routes import router as auth_router

# 👈 Ye line tables create karti hai agar wo nahi bane hue
Base.metadata.create_all(bind=engine)

app = FastAPI()

app.include_router(auth_router)

@app.get("/")
def root():
    return {"message": "Server is running"}


if __name__ == "__main__":
    uvicorn.run(app, host="127.0.0.1", port=8000)