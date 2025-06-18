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
TMDB_API_KEY = os.getenv("TMDB_API_KEY")

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

def get_genre_names(genre_ids, content_type="movie"):
    """Convert TMDB genre IDs to readable genre names"""
    movie_genres = {
        28: "Action", 12: "Adventure", 16: "Animation", 35: "Comedy", 80: "Crime",
        99: "Documentary", 18: "Drama", 10751: "Family", 14: "Fantasy", 36: "History",
        27: "Horror", 10402: "Music", 9648: "Mystery", 10749: "Romance", 878: "Science Fiction",
        10770: "TV Movie", 53: "Thriller", 10752: "War", 37: "Western"
    }
    
    tv_genres = {
        10759: "Action & Adventure", 16: "Animation", 35: "Comedy", 80: "Crime",
        99: "Documentary", 18: "Drama", 10751: "Family", 10762: "Kids", 9648: "Mystery",
        10763: "News", 10764: "Reality", 10765: "Sci-Fi & Fantasy", 10766: "Soap",
        10767: "Talk", 10768: "War & Politics", 37: "Western"
    }
    
    genre_map = tv_genres if content_type == "tv" else movie_genres
    return [genre_map.get(gid, "Unknown") for gid in genre_ids[:3]]  # Limit to 3 genres

async def search_tmdb_content(title: str, content_type: str = "movie"):
    """Search for content on TMDB and get detailed information including poster and trailer"""
    try:
        base_url = "https://api.themoviedb.org/3"
        search_url = f"{base_url}/search/{content_type}"
        
        params = {
            "api_key": TMDB_API_KEY,
            "query": title,
            "language": "en-US",
            "page": 1,
            "include_adult": False
        }
        
        print(f"Searching TMDB for: {title} ({content_type})")
        response = requests.get(search_url, params=params, timeout=10)
        
        if response.status_code == 200:
            data = response.json()
            results = data.get("results", [])
            
            if results:
                # Get the first (most relevant) result
                content = results[0]
                content_id = content.get("id")
                
                # Get additional details including trailers
                details_url = f"{base_url}/{content_type}/{content_id}"
                details_params = {
                    "api_key": TMDB_API_KEY,
                    "language": "en-US",
                    "append_to_response": "videos,credits"
                }
                
                details_response = requests.get(details_url, params=details_params, timeout=10)
                
                if details_response.status_code == 200:
                    details_data = details_response.json()
                    
                    # Extract trailer URL
                    trailer_url = None
                    videos = details_data.get("videos", {}).get("results", [])
                    for video in videos:
                        if video.get("site") == "YouTube" and video.get("type") in ["Trailer", "Teaser"]:
                            trailer_url = f"https://www.youtube.com/watch?v={video.get('key')}"
                            break
                    
                    # Extract cast information
                    cast = details_data.get("credits", {}).get("cast", [])
                    cast_names = [actor.get("name") for actor in cast[:5]]  # Top 5 cast members
                    
                    # Build the response
                    tmdb_result = {
                        "id": str(content_id),
                        "title": content.get("title" if content_type == "movie" else "name", title),
                        "overview": content.get("overview", f"An engaging {content_type} that perfectly matches your mood."),
                        "genre_ids": content.get("genre_ids", []),
                        "vote_average": content.get("vote_average", 7.0),
                        "poster_path": content.get("poster_path"),
                        "backdrop_path": content.get("backdrop_path"),
                        "trailer_url": trailer_url,
                        "cast": cast_names,
                        "release_date": content.get("release_date" if content_type == "movie" else "first_air_date", ""),
                        "runtime": details_data.get("runtime") if content_type == "movie" else None,
                        "episode_count": details_data.get("number_of_episodes") if content_type == "tv" else None
                    }
                    
                    print(f"Found TMDB content: {tmdb_result['title']} with poster: {tmdb_result['poster_path']}")
                    if trailer_url:
                        print(f"Found trailer: {trailer_url}")
                    
                    return tmdb_result
                else:
                    print(f"TMDB details error: {details_response.status_code}")
            else:
                print(f"No TMDB results found for: {title}")
        else:
            print(f"TMDB search error: {response.status_code}")
            
    except Exception as e:
        print(f"TMDB search error for {title}: {e}")
    
    # Return fallback data if TMDB fails
    return {
        "id": str(uuid.uuid4()),
        "title": title,
        "overview": f"An engaging {content_type} that perfectly matches your mood.",
        "genre_ids": [18, 35] if content_type == "movie" else [18, 10765],
        "vote_average": 7.0 + (hash(title) % 30) / 10,
        "poster_path": None,
        "backdrop_path": None,
        "trailer_url": None,
        "cast": [],
        "release_date": "",
        "runtime": None,
        "episode_count": None
    }

async def get_streaming_availability(title: str, content_type: str = "movie"):
    """Get streaming availability from RapidAPI Streaming Availability API"""
    try:
        # Try to get content by title first - search for shows
        search_url = f"https://{RAPIDAPI_HOST}/shows/search/title"
        headers = {
            "X-RapidAPI-Key": RAPIDAPI_KEY,
            "X-RapidAPI-Host": RAPIDAPI_HOST
        }
        
        # Search for the title
        search_params = {
            "title": title,
            "country": "us",
            "series_granularity": "show" if content_type == "tv" else None,
            "show_type": content_type,
            "output_language": "en"
        }
        
        # Remove None values
        search_params = {k: v for k, v in search_params.items() if v is not None}
        
        print(f"Searching for streaming availability: {title} ({content_type})")
        
        # Make the API call
        response = requests.get(search_url, headers=headers, params=search_params, timeout=15)
        
        if response.status_code == 200:
            data = response.json()
            streaming_info = []
            
            # Check if we got results
            if data and len(data) > 0:
                # Get the first result (most relevant)
                show_data = data[0]
                streaming_options = show_data.get("streamingOptions", {})
                
                # Get US streaming options
                us_options = streaming_options.get("us", [])
                
                # Process streaming services
                seen_services = set()
                for option in us_options[:5]:  # Limit to top 5 services
                    service_info = option.get("service", {})
                    service_name = service_info.get("name", "Unknown")
                    service_id = service_info.get("id", service_name.lower())
                    
                    # Avoid duplicates
                    if service_id not in seen_services:
                        seen_services.add(service_id)
                        
                        # Map service types
                        option_type = option.get("type", "subscription")
                        
                        streaming_info.append({
                            "service": service_name,
                            "type": option_type,
                            "link": option.get("link", ""),
                            "quality": option.get("quality", "HD"),
                            "price": option.get("price", {}).get("formatted", "") if option.get("price") else ""
                        })
                
                print(f"Found {len(streaming_info)} streaming options for {title}")
                return streaming_info
            else:
                print(f"No streaming results found for: {title}")
                
        elif response.status_code == 429:
            print("Rate limit reached for streaming API")
        elif response.status_code == 404:
            print(f"Streaming API endpoint not found - trying alternative approach")
        else:
            print(f"Streaming API error: {response.status_code} - {response.text}")
            
    except Exception as e:
        print(f"Streaming availability error for {title}: {e}")
    
    # Return intelligent mock data based on content type and title
    mock_services = []
    
    # Smart mock data based on title patterns
    title_lower = title.lower()
    
    # Disney content
    if any(word in title_lower for word in ["disney", "pixar", "marvel", "star wars", "moana", "frozen", "toy story", "coco", "encanto", "lion king"]):
        mock_services.append({"service": "Disney+", "type": "subscription", "link": "https://disneyplus.com", "quality": "4K", "price": ""})
        
    # Netflix originals and popular content
    if any(word in title_lower for word in ["netflix", "stranger things", "the crown", "wednesday", "squid game", "dark", "money heist"]):
        mock_services.append({"service": "Netflix", "type": "subscription", "link": "https://netflix.com", "quality": "4K", "price": ""})
    elif content_type == "tv":
        mock_services.append({"service": "Netflix", "type": "subscription", "link": "https://netflix.com", "quality": "4K", "price": ""})
        
    # HBO content
    if any(word in title_lower for word in ["hbo", "game of thrones", "succession", "euphoria", "house of dragon", "last of us"]):
        mock_services.append({"service": "HBO Max", "type": "subscription", "link": "https://hbomax.com", "quality": "4K", "price": ""})
        
    # Amazon Prime content
    if any(word in title_lower for word in ["amazon", "prime", "rings of power", "boys", "marvelous", "grand tour"]):
        mock_services.append({"service": "Prime Video", "type": "subscription", "link": "https://primevideo.com", "quality": "4K", "price": ""})
    
    # Add Netflix as default if no specific matches and it's not already added
    if not any(service["service"] == "Netflix" for service in mock_services):
        mock_services.append({"service": "Netflix", "type": "subscription", "link": "https://netflix.com", "quality": "HD", "price": ""})
    
    # Add Hulu for TV content
    if content_type == "tv" and not any(service["service"] == "Hulu" for service in mock_services):
        mock_services.append({"service": "Hulu", "type": "subscription", "link": "https://hulu.com", "quality": "HD", "price": ""})
    
    # Add rental option for movies
    if content_type == "movie":
        mock_services.append({"service": "Amazon Prime", "type": "rent", "link": "https://primevideo.com", "quality": "4K", "price": "$3.99"})
        mock_services.append({"service": "Apple TV", "type": "rent", "link": "https://tv.apple.com", "quality": "4K", "price": "$4.99"})
    
    return mock_services[:4]  # Return top 4 options

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
            streaming_info = await get_streaming_availability(title, content_type)
            
            if tmdb_data:
                # Get genre names
                genre_names = get_genre_names(tmdb_data.get("genre_ids", []), content_type)
                
                # Build poster and backdrop URLs
                poster_url = None
                backdrop_url = None
                if tmdb_data.get("poster_path"):
                    poster_url = f"https://image.tmdb.org/t/p/w500{tmdb_data['poster_path']}"
                if tmdb_data.get("backdrop_path"):
                    backdrop_url = f"https://image.tmdb.org/t/p/w1280{tmdb_data['backdrop_path']}"
                
                recommendation = Recommendation(
                    id=tmdb_data["id"],
                    title=tmdb_data["title"],
                    type=content_type,
                    overview=tmdb_data["overview"],
                    genre=genre_names,
                    rating=tmdb_data["vote_average"],
                    poster_url=poster_url,
                    backdrop_url=backdrop_url,
                    trailer_url=tmdb_data.get("trailer_url"),
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