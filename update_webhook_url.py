#!/usr/bin/env python3
"""
Update Tavus persona with public webhook URL
"""

import requests
import json
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

def update_webhook_url():
    """Update the Tavus persona with the public webhook URL"""
    
    api_key = os.getenv('NEXT_PUBLIC_TAVUS_API_KEY')
    persona_id = os.getenv('NEXT_PUBLIC_TAVUS_PERSONA_ID')
public_webhook_url = "https://consulting-converter-insertion-maui.trycloudflare.com/api/tavus-webhook"
    
    if not api_key or not persona_id:
        print("❌ Missing TAVUS_API_KEY or TAVUS_PERSONA_ID in environment variables")
        return False
    
    url = f"https://tavusapi.com/v2/personas/{persona_id}"
    
    headers = {
        'Content-Type': 'application/json',
        'x-api-key': api_key
    }
    
    # Update the persona with the public webhook URL
    update_config = [
        {
            "op": "replace",
            "path": "/layers/llm/tools/0/function/description",
            "value": f"Fetches relevant ISS images based on a search query. Use this when the user asks about specific parts of the ISS, astronauts, space activities, or wants to see images. Webhook URL: {public_webhook_url}"
        }
    ]
    
    print(f"🔧 Updating persona {persona_id} with public webhook URL...")
    print(f"📡 Public webhook URL: {public_webhook_url}")
    
    try:
        response = requests.patch(url, headers=headers, json=update_config)
        
        if response.status_code == 200:
            print("✅ Successfully updated persona with public webhook URL!")
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
    print("🌐 Updating Tavus Persona with Public Webhook URL")
    print("=" * 60)
    
    success = update_webhook_url()
    
    if success:
        print("\n✅ Persona updated with public webhook URL!")
        print("🎯 Tavus can now reach our webhook from the internet")
        print("💡 Try starting a new conversation and asking for images!")
    else:
        print("\n❌ Failed to update persona")
        print("🔍 Check your API key and persona ID")
