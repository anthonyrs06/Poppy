import os
import asyncio
import uuid
import json
from datetime import datetime
from typing import List, Optional, Dict, Any

from fastapi import FastAPI, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from pydantic import BaseModel, Field
from motor.motor_asyncio import AsyncIOMotorClient, AsyncIOMotorDatabase
from dotenv import load_dotenv
import requests
from emergentintegrations.llm.chat import LlmChat, UserMessage

load_dotenv()

app = FastAPI(title="Poppy - AI Entertainment Discovery")

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Database setup
MONGO_URL = os.getenv("MONGO_URL", "mongodb://localhost:27017")
DB_NAME = os.getenv("DB_NAME", "poppy_database")

# API Keys
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
RAPIDAPI_KEY = os.getenv("RAPIDAPI_KEY")
RAPIDAPI_HOST = os.getenv("RAPIDAPI_HOST")

# MongoDB client
client = AsyncIOMotorClient(MONGO_URL)
db: AsyncIOMotorDatabase = client[DB_NAME]

# Pydantic models
class MoodQuery(BaseModel):
    mood: str = Field(..., description="User's mood or vibe description")
    user_id: Optional[str] = Field(None, description="Optional user ID for personalization")

class Recommendation(BaseModel):
    id: str
    title: str
    type: str  # movie or tv
    overview: str
    genre: List[str]
    rating: float
    poster_url: Optional[str]
    backdrop_url: Optional[str]
    trailer_url: Optional[str]
    streaming_availability: List[Dict[str, Any]] = []
    recommendation_reason: str

class RecommendationResponse(BaseModel):
    recommendations: List[Recommendation]
    mood_interpretation: str
    session_id: str

# LLM Chat instance
async def get_recommendation_chat(session_id: str):
    """Create a new LLM chat instance for recommendations"""
    return LlmChat(
        api_key=GEMINI_API_KEY,
        session_id=session_id,
        system_message="""You are Poppy, an expert entertainment curator who understands user moods and vibes to provide personalized movie and TV show recommendations. 

When users describe their mood, vibe, or situation (like 'cozy rainy evening', 'action-packed weekend', 'need something to cry to', 'fun family night'), you should:

1. Interpret their emotional state and context
2. Provide 5 specific movie/TV recommendations that match their vibe
3. For each recommendation, explain briefly why it matches their mood

Your response should be in this exact JSON format:
{
  "mood_interpretation": "Brief interpretation of the user's mood and what they're looking for",
  "recommendations": [
    {
      "title": "Movie/Show Title",
      "type": "movie" or "tv",
      "reason": "Why this matches their vibe in 1-2 sentences"
    }
  ]
}

Be creative, empathetic, and focus on the emotional connection between the user's mood and the content. Consider factors like pacing, tone, themes, and overall feeling of the content."""
    ).with_model("gemini", "gemini-2.0-flash").with_max_tokens(2048)

async def search_tmdb_content(title: str, content_type: str = "movie"):
    """Search for content on TMDB"""
    try:
        # Using TMDB API (free tier, no API key needed for basic search)
        base_url = "https://api.themoviedb.org/3"
        search_url = f"{base_url}/search/{content_type}"
        
        # Note: For production, you should get a free TMDB API key
        # For now, using the demo data approach
        params = {
            "query": title,
            "api_key": "demo"  # In production, use real API key
        }
        
        # For MVP, return mock data to demonstrate the concept
        return {
            "id": str(uuid.uuid4()),
            "title": title,
            "overview": f"An engaging {content_type} that perfectly matches your mood.",
            "genre_ids": [18, 35] if content_type == "movie" else [18, 10765],
            "vote_average": 7.5 + (hash(title) % 30) / 10,  # Generate realistic rating
            "poster_path": f"/demo-poster-{hash(title) % 10}.jpg",
            "backdrop_path": f"/demo-backdrop-{hash(title) % 10}.jpg"
        }
    except Exception as e:
        print(f"TMDB search error: {e}")
        return None

async def get_streaming_availability(title: str):
    """Get streaming availability from RapidAPI"""
    try:
        url = f"https://{RAPIDAPI_HOST}/search/title"
        headers = {
            "X-RapidAPI-Key": RAPIDAPI_KEY,
            "X-RapidAPI-Host": RAPIDAPI_HOST
        }
        params = {"title": title, "country": "us"}
        
        response = requests.get(url, headers=headers, params=params, timeout=10)
        
        if response.status_code == 200:
            data = response.json()
            streaming_info = []
            
            if data.get("result") and len(data["result"]) > 0:
                services = data["result"][0].get("streamingOptions", {}).get("us", [])
                for service in services[:3]:  # Limit to top 3 services
                    streaming_info.append({
                        "service": service.get("service", {}).get("name", "Unknown"),
                        "type": service.get("type", "subscription"),
                        "link": service.get("link", "")
                    })
            
            return streaming_info
        else:
            print(f"Streaming API error: {response.status_code}")
            return []
    except Exception as e:
        print(f"Streaming availability error: {e}")
        # Return mock data for demo
        return [
            {"service": "Netflix", "type": "subscription", "link": "https://netflix.com"},
            {"service": "Hulu", "type": "subscription", "link": "https://hulu.com"}
        ]

# API Routes
@app.get("/api/health")
async def health_check():
    return {"status": "healthy", "service": "Poppy AI Entertainment Discovery"}

@app.post("/api/recommendations", response_model=RecommendationResponse)
async def get_recommendations(mood_query: MoodQuery):
    """Get AI-powered entertainment recommendations based on user mood"""
    try:
        session_id = str(uuid.uuid4())
        
        # Get LLM recommendations
        chat = await get_recommendation_chat(session_id)
        user_message = UserMessage(text=mood_query.mood)
        
        llm_response = await chat.send_message(user_message)
        
        # Parse LLM response
        try:
            # Clean the response to extract JSON
            response_text = llm_response.strip()
            if response_text.startswith("```json"):
                response_text = response_text[7:]
            if response_text.endswith("```"):
                response_text = response_text[:-3]
            
            llm_data = json.loads(response_text)
        except json.JSONDecodeError:
            # Fallback if JSON parsing fails
            llm_data = {
                "mood_interpretation": f"I understand you're looking for something that matches your '{mood_query.mood}' vibe.",
                "recommendations": [
                    {"title": "The Grand Budapest Hotel", "type": "movie", "reason": "A whimsical, beautifully crafted film perfect for your mood."},
                    {"title": "Avatar: The Last Airbender", "type": "tv", "reason": "An epic adventure with heart and stunning visuals."},
                    {"title": "Spirited Away", "type": "movie", "reason": "A magical journey that captures wonder and emotion."},
                    {"title": "Ted Lasso", "type": "tv", "reason": "Heartwarming comedy that lifts spirits and inspires."},
                    {"title": "Your Name", "type": "movie", "reason": "A beautiful animated film about connection and fate."}
                ]
            }
        
        # Fetch additional data for each recommendation
        recommendations = []
        for rec in llm_data.get("recommendations", [])[:5]:  # Limit to 5
            title = rec.get("title", "")
            content_type = rec.get("type", "movie")
            
            # Search TMDB for metadata
            tmdb_data = await search_tmdb_content(title, content_type)
            
            # Get streaming availability
            streaming_info = await get_streaming_availability(title)
            
            if tmdb_data:
                recommendation = Recommendation(
                    id=tmdb_data["id"],
                    title=tmdb_data["title"],
                    type=content_type,
                    overview=tmdb_data["overview"],
                    genre=["Drama", "Comedy"] if content_type == "movie" else ["Drama", "Sci-Fi"],
                    rating=tmdb_data["vote_average"],
                    poster_url=f"https://image.tmdb.org/t/p/w500{tmdb_data['poster_path']}" if tmdb_data.get("poster_path") else None,
                    backdrop_url=f"https://image.tmdb.org/t/p/w1280{tmdb_data['backdrop_path']}" if tmdb_data.get("backdrop_path") else None,
                    trailer_url=f"https://www.youtube.com/watch?v=demo-{hash(title) % 1000}",
                    streaming_availability=streaming_info,
                    recommendation_reason=rec.get("reason", "Perfect match for your current vibe!")
                )
                recommendations.append(recommendation)
        
        # Store user query and recommendations in database
        await db.recommendations.insert_one({
            "session_id": session_id,
            "user_id": mood_query.user_id,
            "mood_query": mood_query.mood,
            "mood_interpretation": llm_data.get("mood_interpretation", ""),
            "recommendations": [rec.dict() for rec in recommendations],
            "created_at": datetime.utcnow()
        })
        
        return RecommendationResponse(
            recommendations=recommendations,
            mood_interpretation=llm_data.get("mood_interpretation", ""),
            session_id=session_id
        )
        
    except Exception as e:
        print(f"Recommendation error: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to get recommendations: {str(e)}")

@app.get("/api/recommendations/history")
async def get_recommendation_history(user_id: Optional[str] = None, limit: int = 10):
    """Get user's recommendation history"""
    try:
        query = {}
        if user_id:
            query["user_id"] = user_id
        
        history = await db.recommendations.find(query).sort("created_at", -1).limit(limit).to_list(length=limit)
        
        # Convert ObjectId to string for JSON serialization
        for item in history:
            item["_id"] = str(item["_id"])
            
        return {"history": history}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get history: {str(e)}")

@app.post("/api/feedback")
async def submit_feedback(request: Request):
    """Submit user feedback on recommendations"""
    try:
        feedback_data = await request.json()
        feedback_data["created_at"] = datetime.utcnow()
        
        await db.feedback.insert_one(feedback_data)
        return {"status": "success", "message": "Feedback submitted successfully"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to submit feedback: {str(e)}")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8001)