from env_utils import set_env_vars
set_env_vars(".env")
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.routers import (
    chat
)
import uvicorn

app = FastAPI(title="Chemistry API", description="API for Chemistry", version="0.1.0")

# allow origins
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(chat.router, prefix="/chat", tags=["chat"]) # Include the validator router

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000) # Run the app