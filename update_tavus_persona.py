#!/usr/bin/env python3
"""
Update Tavus persona with tool calling configuration
Based on official Tavus documentation: https://docs.tavus.io/sections/conversational-video-interface/persona/llm-tool
"""

import requests
import json
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

def update_persona_tools():
    """Update the Tavus persona with our fetch_relevant_image tool"""
    
    api_key = os.getenv('NEXT_PUBLIC_TAVUS_API_KEY')
    persona_id = os.getenv('NEXT_PUBLIC_TAVUS_PERSONA_ID')
    
    if not api_key or not persona_id:
        print("❌ Missing TAVUS_API_KEY or TAVUS_PERSONA_ID in environment variables")
        return False
    
    url = f"https://tavusapi.com/v2/personas/{persona_id}"
    
    headers = {
        'Content-Type': 'application/json',
        'x-api-key': api_key
    }
    
    # Tool configuration based on Tavus documentation
    tools_config = [
        {
            "op": "replace",
            "path": "/layers/llm/tools",
            "value": [
                {
                    "type": "function",
                    "function": {
                        "name": "fetch_relevant_image",
                        "description": "Fetches relevant ISS images based on a search query. Use this when the user asks about specific parts of the ISS, astronauts, space activities, or wants to see images.",
                        "parameters": {
                            "type": "object",
                            "properties": {
                                "query": {
                                    "type": "string",
                                    "description": "Natural language search query for ISS images (e.g., 'Cupola module', 'astronauts working', 'spacewalk')"
                                },
                                "top_k": {
                                    "type": "number",
                                    "description": "Number of top images to retrieve (default: 5, max: 10)"
                                }
                            },
                            "required": ["query"]
                        }
                    }
                }
            ]
        }
    ]
    
    print(f"🔧 Updating persona {persona_id} with tool configuration...")
    print(f"📡 URL: {url}")
    print(f"🔑 API Key: {api_key[:10]}...")
    
    try:
        response = requests.patch(url, headers=headers, json=tools_config)
        
        if response.status_code == 200:
            print("✅ Successfully updated persona with tool configuration!")
            print("📋 Response:", response.json())
            return True
        else:
            print(f"❌ Failed to update persona: HTTP {response.status_code}")
            print(f"📋 Error: {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ Error updating persona: {e}")
        return False

if __name__ == "__main__":
    print("🚀 Updating Tavus Persona with Tool Configuration")
    print("=" * 60)
    
    success = update_persona_tools()
    
    if success:
        print("\n✅ Persona updated successfully!")
        print("🎯 The persona now has the fetch_relevant_image tool configured")
        print("💡 You can now start a conversation and ask for images!")
    else:
        print("\n❌ Failed to update persona")
        print("🔍 Check your API key and persona ID")
