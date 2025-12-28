from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from api.routes import router as api_router
import os

app = FastAPI(title="Video AI Backend")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://127.0.0.1:8080", "http://localhost:8080"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

outputs_dir = os.path.abspath(os.path.join(os.getcwd(), "..", "outputs"))
app.mount("/outputs", StaticFiles(directory=outputs_dir), name="outputs")

app.include_router(api_router, prefix="/api")