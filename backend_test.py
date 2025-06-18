import requests
import unittest
import json
import sys
from datetime import datetime

class PoppyAPITester:
    def __init__(self, base_url="https://b2ff90ae-fef2-4f82-b569-27c97d8741c9.preview.emergentagent.com"):
        self.base_url = base_url
        self.tests_run = 0
        self.tests_passed = 0
        self.session_id = None

    def run_test(self, name, method, endpoint, expected_status, data=None):
        """Run a single API test"""
        url = f"{self.base_url}/{endpoint}"
        headers = {'Content-Type': 'application/json'}
        
        self.tests_run += 1
        print(f"\n🔍 Testing {name}...")
        
        try:
            if method == 'GET':
                response = requests.get(url, headers=headers)
            elif method == 'POST':
                response = requests.post(url, json=data, headers=headers)
            else:
                print(f"❌ Failed - Unsupported method: {method}")
                return False, None

            success = response.status_code == expected_status
            if success:
                self.tests_passed += 1
                print(f"✅ Passed - Status: {response.status_code}")
                try:
                    return success, response.json()
                except:
                    return success, None
            else:
                print(f"❌ Failed - Expected {expected_status}, got {response.status_code}")
                try:
                    print(f"Response: {response.text}")
                except:
                    pass
                return False, None

        except Exception as e:
            print(f"❌ Failed - Error: {str(e)}")
            return False, None

    def test_health_endpoint(self):
        """Test the health check endpoint"""
        success, response = self.run_test(
            "Health Check Endpoint",
            "GET",
            "api/health",
            200
        )
        if success:
            print(f"Health check response: {response}")
        return success

    def test_recommendations_endpoint(self, mood):
        """Test the recommendations endpoint with a mood query"""
        success, response = self.run_test(
            f"Recommendations Endpoint with mood: '{mood}'",
            "POST",
            "api/recommendations",
            200,
            data={"mood": mood, "user_id": "test-user"}
        )
        
        if success:
            # Store session_id for history test
            self.session_id = response.get("session_id")
            
            # Validate response structure
            if "recommendations" not in response:
                print("❌ Failed - 'recommendations' field missing from response")
                return False
                
            if "mood_interpretation" not in response:
                print("❌ Failed - 'mood_interpretation' field missing from response")
                return False
                
            if "session_id" not in response:
                print("❌ Failed - 'session_id' field missing from response")
                return False
                
            # Check recommendations content
            recommendations = response["recommendations"]
            if not recommendations or not isinstance(recommendations, list):
                print("❌ Failed - 'recommendations' should be a non-empty list")
                return False
                
            # Check first recommendation structure
            first_rec = recommendations[0]
            required_fields = ["id", "title", "type", "overview", "genre", "rating", "recommendation_reason"]
            for field in required_fields:
                if field not in first_rec:
                    print(f"❌ Failed - '{field}' field missing from recommendation")
                    return False
            
            # Check streaming availability
            if "streaming_availability" not in first_rec:
                print("❌ Failed - 'streaming_availability' field missing from recommendation")
                return False
                
            streaming_options = first_rec.get("streaming_availability", [])
            if not isinstance(streaming_options, list):
                print("❌ Failed - 'streaming_availability' should be a list")
                return False
                
            # If streaming options exist, check their structure
            if streaming_options:
                first_option = streaming_options[0]
                streaming_fields = ["service", "type", "link", "quality"]
                for field in streaming_fields:
                    if field not in first_option:
                        print(f"❌ Failed - '{field}' field missing from streaming option")
                        return False
                
                print(f"✅ First streaming option: {first_option['service']} ({first_option['type']})")
                if first_option.get("price"):
                    print(f"✅ Price information: {first_option['price']}")
                print(f"✅ Quality: {first_option['quality']}")
            else:
                print("⚠️ Warning: No streaming options available for this recommendation")
            
            print(f"✅ Received {len(recommendations)} recommendations")
            print(f"✅ First recommendation: '{first_rec['title']}' ({first_rec['type']})")
            print(f"✅ Mood interpretation: '{response['mood_interpretation'][:100]}...'")
            
        return success
        
    def test_content_specific_streaming(self):
        """Test content-specific streaming recommendations"""
        test_cases = [
            {
                "mood": "Disney movie for family night",
                "expected_service": "Disney+",
                "content_type": "movie"
            },
            {
                "mood": "Marvel superhero action",
                "expected_service": "Disney+",
                "content_type": "movie"
            },
            {
                "mood": "Binge-worthy Netflix series",
                "expected_service": "Netflix",
                "content_type": "tv"
            },
            {
                "mood": "HBO prestige drama",
                "expected_service": "HBO Max",
                "content_type": "tv"
            }
        ]
        
        success_count = 0
        for test_case in test_cases:
            print(f"\n🔍 Testing content-specific streaming for: '{test_case['mood']}'")
            
            success, response = self.run_test(
                f"Content-Specific Streaming Test: {test_case['mood']}",
                "POST",
                "api/recommendations",
                200,
                data={"mood": test_case['mood'], "user_id": "test-user"}
            )
            
            if success and "recommendations" in response:
                recommendations = response["recommendations"]
                if recommendations:
                    # Check if any recommendation has the expected streaming service
                    found_service = False
                    for rec in recommendations:
                        if rec.get("type") == test_case["content_type"]:
                            streaming_options = rec.get("streaming_availability", [])
                            for option in streaming_options:
                                if option.get("service") == test_case["expected_service"]:
                                    found_service = True
                                    print(f"✅ Found expected streaming service '{test_case['expected_service']}' for '{rec['title']}'")
                                    break
                        if found_service:
                            break
                    
                    if found_service:
                        success_count += 1
                    else:
                        print(f"❌ Failed to find expected streaming service '{test_case['expected_service']}' for '{test_case['mood']}'")
            
        return success_count > 0  # Pass if at least one test case succeeds
        
    def test_poster_images_and_trailers(self):
        """Test that recommendations include poster images and trailer URLs"""
        test_cases = [
            "I want to watch Inception or similar mind-bending movies",
            "Disney animated movies for family night",
            "Marvel superhero action movies",
            "Classic movies from the 80s or 90s"
        ]
        
        success_count = 0
        for mood in test_cases:
            print(f"\n🔍 Testing poster images and trailers for: '{mood}'")
            
            success, response = self.run_test(
                f"Poster Images and Trailers Test: {mood}",
                "POST",
                "api/recommendations",
                200,
                data={"mood": mood, "user_id": "test-user"}
            )
            
            if success and "recommendations" in response:
                recommendations = response["recommendations"]
                if recommendations:
                    # Check if recommendations have poster images and trailer URLs
                    poster_count = 0
                    trailer_count = 0
                    
                    for rec in recommendations:
                        # Check for poster URL
                        if rec.get("poster_url"):
                            poster_count += 1
                            print(f"✅ Found poster image for '{rec['title']}': {rec['poster_url'][:60]}...")
                        else:
                            print(f"⚠️ No poster image for '{rec['title']}'")
                        
                        # Check for trailer URL
                        if rec.get("trailer_url"):
                            trailer_count += 1
                            print(f"✅ Found trailer URL for '{rec['title']}': {rec['trailer_url'][:60]}...")
                        else:
                            print(f"⚠️ No trailer URL for '{rec['title']}'")
                    
                    # Success if at least 50% of recommendations have posters and at least one has a trailer
                    if poster_count >= len(recommendations) / 2:
                        print(f"✅ {poster_count}/{len(recommendations)} recommendations have poster images")
                        if trailer_count > 0:
                            print(f"✅ {trailer_count}/{len(recommendations)} recommendations have trailer URLs")
                            success_count += 1
                        else:
                            print("❌ No trailers found for any recommendations")
                    else:
                        print(f"❌ Only {poster_count}/{len(recommendations)} recommendations have poster images")
            
        return success_count > 0  # Pass if at least one test case succeeds
        
    def test_tmdb_metadata(self):
        """Test that recommendations include real TMDB metadata"""
        test_cases = [
            "I want to watch Inception or similar mind-bending movies",
            "Marvel superhero action movies"
        ]
        
        success_count = 0
        for mood in test_cases:
            print(f"\n🔍 Testing TMDB metadata for: '{mood}'")
            
            success, response = self.run_test(
                f"TMDB Metadata Test: {mood}",
                "POST",
                "api/recommendations",
                200,
                data={"mood": mood, "user_id": "test-user"}
            )
            
            if success and "recommendations" in response:
                recommendations = response["recommendations"]
                if recommendations:
                    # Check if recommendations have proper TMDB metadata
                    metadata_success = True
                    
                    for rec in recommendations:
                        # Check for required metadata fields
                        if not rec.get("genre") or not isinstance(rec.get("genre"), list) or len(rec.get("genre", [])) == 0:
                            print(f"❌ Missing or invalid genres for '{rec['title']}'")
                            metadata_success = False
                        else:
                            print(f"✅ Genres for '{rec['title']}': {', '.join(rec['genre'])}")
                        
                        if not rec.get("rating") or not isinstance(rec.get("rating"), (int, float)):
                            print(f"❌ Missing or invalid rating for '{rec['title']}'")
                            metadata_success = False
                        else:
                            print(f"✅ Rating for '{rec['title']}': {rec['rating']}")
                        
                        if not rec.get("overview") or len(rec.get("overview", "")) < 20:
                            print(f"❌ Missing or too short overview for '{rec['title']}'")
                            metadata_success = False
                        else:
                            print(f"✅ Overview for '{rec['title']}': {rec['overview'][:60]}...")
                    
                    if metadata_success:
                        success_count += 1
                        print(f"✅ All recommendations for '{mood}' have proper TMDB metadata")
                    else:
                        print(f"❌ Some recommendations for '{mood}' are missing TMDB metadata")
            
        return success_count > 0  # Pass if at least one test case succeeds

    def test_history_endpoint(self):
        """Test the recommendations history endpoint"""
        success, response = self.run_test(
            "Recommendations History Endpoint",
            "GET",
            "api/recommendations/history",
            200
        )
        
        if success:
            if "history" not in response:
                print("❌ Failed - 'history' field missing from response")
                return False
                
            history = response["history"]
            if not isinstance(history, list):
                print("❌ Failed - 'history' should be a list")
                return False
                
            print(f"✅ Received history with {len(history)} entries")
            
            # If we have history entries, check the structure of the first one
            if history:
                first_entry = history[0]
                required_fields = ["session_id", "mood_query", "recommendations"]
                for field in required_fields:
                    if field not in first_entry:
                        print(f"❌ Failed - '{field}' field missing from history entry")
                        return False
                
                print(f"✅ First history entry mood: '{first_entry['mood_query']}'")
        
        return success

    def test_feedback_endpoint(self):
        """Test the feedback endpoint"""
        # Create feedback data
        feedback_data = {
            "session_id": self.session_id or "test-session",
            "user_id": "test-user",
            "rating": 5,
            "comment": "Great recommendations!",
            "recommendation_ids": ["test-rec-1", "test-rec-2"]
        }
        
        success, response = self.run_test(
            "Feedback Endpoint",
            "POST",
            "api/feedback",
            200,
            data=feedback_data
        )
        
        if success:
            if "status" not in response or response["status"] != "success":
                print("❌ Failed - Expected 'status': 'success' in response")
                return False
                
            print(f"✅ Feedback submitted successfully")
            
        return success

def run_tests():
    print("=" * 50)
    print("🧪 POPPY API TEST SUITE 🧪")
    print("=" * 50)
    
    tester = PoppyAPITester()
    
    # Test health endpoint
    health_success = tester.test_health_endpoint()
    
    # Test recommendations with different moods
    moods = [
        "I need something cozy for a rainy evening",
        "Action-packed weekend vibes",
        "Something to make me laugh after a long day"
    ]
    
    recommendations_success = False
    for mood in moods:
        if tester.test_recommendations_endpoint(mood):
            recommendations_success = True
            break
    
    # Test content-specific streaming recommendations
    content_specific_success = tester.test_content_specific_streaming()
    
    # Test poster images and trailers
    poster_trailer_success = tester.test_poster_images_and_trailers()
    
    # Test TMDB metadata
    tmdb_metadata_success = tester.test_tmdb_metadata()
    
    # Test history endpoint
    history_success = tester.test_history_endpoint()
    
    # Test feedback endpoint
    feedback_success = tester.test_feedback_endpoint()
    
    # Print summary
    print("\n" + "=" * 50)
    print("📊 TEST SUMMARY")
    print("=" * 50)
    print(f"Total tests run: {tester.tests_run}")
    print(f"Tests passed: {tester.tests_passed}")
    print(f"Success rate: {(tester.tests_passed / tester.tests_run) * 100:.1f}%")
    print("\n📝 ENDPOINT STATUS:")
    print(f"Health Endpoint: {'✅ PASS' if health_success else '❌ FAIL'}")
    print(f"Recommendations Endpoint: {'✅ PASS' if recommendations_success else '❌ FAIL'}")
    print(f"Content-Specific Streaming: {'✅ PASS' if content_specific_success else '❌ FAIL'}")
    print(f"Poster Images and Trailers: {'✅ PASS' if poster_trailer_success else '❌ FAIL'}")
    print(f"TMDB Metadata: {'✅ PASS' if tmdb_metadata_success else '❌ FAIL'}")
    print(f"History Endpoint: {'✅ PASS' if history_success else '❌ FAIL'}")
    print(f"Feedback Endpoint: {'✅ PASS' if feedback_success else '❌ FAIL'}")
    print("=" * 50)
    
    return tester.tests_passed == tester.tests_run

if __name__ == "__main__":
    success = run_tests()
    sys.exit(0 if success else 1)