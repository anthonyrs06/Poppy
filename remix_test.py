#!/usr/bin/env python3
"""
Quick test script for Poppy's Remix functionality
"""

import requests
import json

API_BASE_URL = "https://b2ff90ae-fef2-4f82-b569-27c97d8741c9.preview.emergentagent.com"

def test_remix_functionality():
    print("🎲 TESTING POPPY'S REMIX FEATURE 🎲")
    print("=" * 50)
    
    # Step 1: Get an initial recommendation
    print("\n1. Getting initial recommendation...")
    initial_response = requests.post(f"{API_BASE_URL}/api/recommendations", 
                                   json={"mood": "Action thriller for weekend night"})
    
    if initial_response.status_code == 200:
        data = initial_response.json()
        if data['recommendations']:
            original = data['recommendations'][0]
            print(f"✅ Original: {original['title']} ({', '.join(original['genre'])})")
            print(f"   Reason: {original['recommendation_reason'][:100]}...")
            
            # Step 2: Test remix logic
            print("\n2. Testing remix...")
            remix_prompt = f"I liked the idea of \"{original['title']}\" but want something different. Give me something similar but not the same - same vibe and genres ({', '.join(original['genre'])}) but a different movie/show. {original['recommendation_reason']}"
            
            remix_response = requests.post(f"{API_BASE_URL}/api/recommendations",
                                         json={"mood": remix_prompt})
            
            if remix_response.status_code == 200:
                remix_data = remix_response.json()
                if remix_data['recommendations']:
                    remixed = remix_data['recommendations'][0]
                    print(f"✅ Remixed: {remixed['title']} ({', '.join(remixed['genre'])})")
                    
                    # Verify it's different
                    if remixed['title'].lower() != original['title'].lower():
                        print("✅ SUCCESS: Remix provided a different recommendation!")
                        
                        # Check genre overlap
                        original_genres = set(g.lower() for g in original['genre'])
                        remixed_genres = set(g.lower() for g in remixed['genre'])
                        overlap = original_genres.intersection(remixed_genres)
                        
                        if overlap:
                            print(f"✅ Genre consistency maintained: {overlap}")
                        else:
                            print("⚠️  Warning: No genre overlap, but may still be contextually similar")
                        
                        return True
                    else:
                        print("❌ FAIL: Remix returned the same recommendation")
                        return False
                else:
                    print("❌ FAIL: No remixed recommendations returned")
                    return False
            else:
                print(f"❌ FAIL: Remix API error {remix_response.status_code}")
                return False
        else:
            print("❌ FAIL: No initial recommendations returned")
            return False
    else:
        print(f"❌ FAIL: Initial API error {initial_response.status_code}")
        return False

if __name__ == "__main__":
    success = test_remix_functionality()
    print("\n" + "=" * 50)
    if success:
        print("🎉 REMIX FEATURE TEST PASSED!")
        print("Users can successfully get alternative recommendations!")
    else:
        print("💥 REMIX FEATURE TEST FAILED!")
        print("Check the API implementation.")
    print("=" * 50)