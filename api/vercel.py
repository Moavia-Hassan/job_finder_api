from fastapi import FastAPI
from app.integrated_api import app
from fastapi.middleware.cors import CORSMiddleware
import os

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# This is needed for Vercel serverless functions
# It makes the app importable by the Vercel runtime
app = app 