from fastapi import FastAPI, HTTPException, Depends, status
from pydantic import BaseModel, EmailStr
from typing import Optional
import os
import requests
from dotenv import load_dotenv

load_dotenv()

app = FastAPI()

SUPADATA_API_KEY = os.getenv("SUPADATA_API_KEY")
SUPADATA_BASE_URL = "https://api.supadata.ai/v1/transcript"

if not SUPADATA_API_KEY:
    raise ValueError("SUPADATA_API_KEY environment variable not set.")

class YouTubeURL(BaseModel):
    url: str

@app.post("/api/captions/process")
async def process_youtube_video(youtube_url: YouTubeURL):
    """
    Fetches available caption languages and video title from a YouTube URL using SupaData API.
    """
    headers = {
        "x-api-key": SUPADATA_API_KEY,
        "Content-Type": "application/json"
    }
    params = {
        "url": youtube_url.url,
        "lang": "en", # Default to English for initial detection
        "text": "true",
        "mode": "auto"
    }

    try:
        response = requests.get(SUPADATA_BASE_URL, headers=headers, params=params)
        response.raise_for_status() # Raise an exception for HTTP errors
        data = response.json()

        if not data or "transcript" not in data:
            raise HTTPException(status_code=404, detail="No transcript found or invalid response from SupaData.")

        # The SupaData API returns the transcript directly, not a list of languages.
        # For MVP, we'll assume English is processed and return a dummy list of languages.
        # In a more advanced version, we'd need to query SupaData for available languages
        # or infer them from the response if the API supports it.
        available_languages = ["en"] # Placeholder

        # Extract video title if available in the response, otherwise use a placeholder
        video_title = data.get("video_title", "Unknown Video Title")

        return {
            "message": "Processing initiated",
            "video_id": "dummy_video_id", # SupaData doesn't return a video_id directly
            "available_languages": available_languages,
            "video_title": video_title
        }

    except requests.exceptions.RequestException as e:
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=f"Error communicating with SupaData API: {e}")
    except Exception as e:
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=f"An unexpected error occurred: {e}")

@app.get("/")
async def root():
    return {"message": "YouTube Caption Summary Backend API"}
