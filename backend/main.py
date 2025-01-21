from fastapi import FastAPI, HTTPException, Depends, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
import requests
from pydantic import BaseModel, Field
from typing import List, Optional
import os
from googleapiclient.discovery import build
from functools import lru_cache
import asyncio
from aiohttp import ClientSession
from datetime import timedelta
from fastapi_cache import FastAPICache
from fastapi_cache.decorator import cache
from fastapi_cache.backends.redis import RedisBackend
import redis


# Environment variables
class Settings:
    LASTFM_API_KEY: str = os.getenv("LASTFM_API_KEY", "ac71390adc02161b0bd5ae9a52fe0f9f")
    LASTFM_USERNAME: str = os.getenv("LASTFM_USERNAME", "Ganastaer")
    YOUTUBE_API_KEY: str = os.getenv("YOUTUBE_API_KEY", "AIzaSyBoXIHVZZb7mQqMVVosYlC9epDVrTqpgbU")
    BASE_URL: str = "http://ws.audioscrobbler.com/2.0/"
    REDIS_URL: str = os.getenv("REDIS_URL", "redis://localhost")


settings = Settings()


# Pydantic models
class SongRecommendation(BaseModel):
    name: str = Field(..., description="Name of the song")
    artist: str = Field(..., description="Artist name")
    url: str = Field(..., description="Last.fm URL")
    playcount: int = Field(default=1, description="Number of plays")
    youtube_id: Optional[str] = Field(None, description="YouTube video ID")

    class Config:
        schema_extra = {
            "example": {
                "name": "Bohemian Rhapsody",
                "artist": "Queen",
                "url": "https://last.fm/music/Queen/_/Bohemian+Rhapsody",
                "playcount": 1000,
                "youtube_id": "fJ9rUzIMcZQ"
            }
        }


app = FastAPI(
    title="Music Recommendation API",
    description="API for music recommendations using Last.fm and YouTube",
    version="1.0.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Cache setup
@app.on_event("startup")
async def startup():
    redis_instance = redis.from_url(settings.REDIS_URL, encoding="utf8", decode_responses=True)
    FastAPICache.init(RedisBackend(redis_instance), prefix="fastapi-cache")


# YouTube API client with caching
@lru_cache(maxsize=100)
def get_youtube_client():
    return build('youtube', 'v3', developerKey=settings.YOUTUBE_API_KEY)


async def get_youtube_video_id(session: ClientSession, song_name: str, artist: str) -> Optional[str]:
    try:
        youtube = get_youtube_client()
        search_query = f"{song_name} {artist} official audio"

        request = youtube.search().list(
            part="id",
            q=search_query,
            type="video",
            videoEmbeddable="true",
            maxResults=1
        )

        response = await asyncio.to_thread(request.execute)
        return response['items'][0]['id']['videoId'] if response.get('items') else None
    except Exception as e:
        print(f"YouTube API error: {str(e)}")
        return None


@app.get("/recommendations",
         response_model=List[SongRecommendation],
         summary="Get music recommendations",
         response_description="List of recommended songs with YouTube links")
@cache(expire=timedelta(minutes=30))
async def get_recommendations(limit: int = 10):
    async with ClientSession() as session:
        try:
            params = {
                "method": "user.getrecenttracks",
                "user": settings.LASTFM_USERNAME,
                "api_key": settings.LASTFM_API_KEY,
                "format": "json",
                "limit": limit
            }

            async with session.get(settings.BASE_URL, params=params) as response:
                data = await response.json()
                tracks = data["recenttracks"]["track"]

                # Create tasks for fetching YouTube IDs
                tasks = [get_youtube_video_id(session, track["name"], track["artist"]["#text"])
                         for track in tracks]
                youtube_ids = await asyncio.gather(*tasks)

                recommendations = [
                    SongRecommendation(
                        name=track["name"],
                        artist=track["artist"]["#text"],
                        url=track["url"],
                        playcount=int(track.get("playcount", 1)),
                        youtube_id=youtube_id
                    )
                    for track, youtube_id in zip(tracks, youtube_ids)
                ]

                return recommendations

        except Exception as e:
            raise HTTPException(status_code=500, detail=str(e))


@app.get("/search",
         summary="Search for songs",
         response_description="List of songs matching the search query")
@cache(expire=timedelta(minutes=30))
async def search_songs(query: str, limit: int = 10):
    async with ClientSession() as session:
        try:
            params = {
                "method": "track.search",
                "track": query,
                "api_key": settings.LASTFM_API_KEY,
                "format": "json",
                "limit": limit
            }

            async with session.get(settings.BASE_URL, params=params) as response:
                data = await response.json()
                tracks = data["results"]["trackmatches"]["track"]

                # Create tasks for fetching YouTube IDs
                tasks = [get_youtube_video_id(session, track["name"], track["artist"])
                         for track in tracks]
                youtube_ids = await asyncio.gather(*tasks)

                # Add YouTube IDs to tracks
                for track, youtube_id in zip(tracks, youtube_ids):
                    track['youtube_id'] = youtube_id

                return tracks

        except Exception as e:
            raise HTTPException(status_code=500, detail=str(e))


# Error handling middleware
@app.middleware("http")
async def error_handling(request: Request, call_next):
    try:
        return await call_next(request)
    except Exception as e:
        return JSONResponse(
            status_code=500,
            content={"detail": f"Internal server error: {str(e)}"}
        )