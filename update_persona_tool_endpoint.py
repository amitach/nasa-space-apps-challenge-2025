#!/usr/bin/env python3
"""
Update Tavus persona to use the new tool call endpoint
"""

import os
import requests
import json

# Load environment variables from frontend directory
from dotenv import load_dotenv
load_dotenv('frontend/.env.local')

TAVUS_API_KEY = os.getenv('NEXT_PUBLIC_TAVUS_API_KEY')
TAVUS_PERSONA_ID = os.getenv('NEXT_PUBLIC_TAVUS_PERSONA_ID')
NEW_TOOL_ENDPOINT = "https://consulting-converter-insertion-maui.trycloudflare.com/api/tavus-tool-call"

def get_tavus_tools():
    """Get the tool configuration for Tavus"""
    return [
        {
            "type": "function",
            "function": {
                "name": "fetch_relevant_image",
                "description": "Fetch relevant ISS images based on a search query. Use this when the user asks about specific parts of the ISS, astronauts, space activities, or wants to see images.",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "query": {
                            "type": "string",
                            "description": "The search query for ISS images, e.g. 'Cupola module', 'astronauts working', 'spacewalk'"
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

def update_persona_tool_endpoint(persona_id, api_key, new_endpoint):
    """Update persona to use the new tool call endpoint"""
    url = f"https://tavusapi.com/v2/personas/{persona_id}"
    headers = {
        "Content-Type": "application/json",
        "x-api-key": api_key
    }
    
    # First, get the current persona to see its structure
    print(f"🔍 Fetching current persona: {persona_id}")
    get_response = requests.get(url, headers=headers)
    
    if get_response.status_code != 200:
        print(f"❌ Failed to fetch persona: {get_response.status_code}")
        print(f"Error: {get_response.text}")
        return False
    
    persona_data = get_response.json()
    print(f"✅ Current persona fetched successfully")
    print(f"📋 Persona structure: {json.dumps(persona_data, indent=2)}")
    
    # Check if callback_url exists, if not, add it
    if 'callback_url' in persona_data:
        patch_data = [
            {
                "op": "replace",
                "path": "/callback_url",
                "value": new_endpoint
            }
        ]
    else:
        patch_data = [
            {
                "op": "add",
                "path": "/callback_url",
                "value": new_endpoint
            }
        ]
    
    print(f"🔧 Updating persona callback URL to: {new_endpoint}")
    print(f"📡 URL: {url}")
    print(f"🔑 API Key: {api_key[:10]}...")
    print(f"📋 Patch data: {json.dumps(patch_data, indent=2)}")

    response = requests.patch(url, headers=headers, data=json.dumps(patch_data))
    
    if response.status_code == 200:
        print("✅ Successfully updated persona callback URL!")
        updated_persona = response.json()
        print(f"📋 New callback URL: {updated_persona.get('callback_url', 'Not found')}")
        return True
    else:
        print(f"❌ Failed to update persona: HTTP {response.status_code}")
        print("📋 Error:", response.text)
        return False

def verify_persona_tools(persona_id, api_key):
    """Verify the persona has the correct tool configuration"""
    url = f"https://tavusapi.com/v2/personas/{persona_id}"
    headers = {
        "Content-Type": "application/json",
        "x-api-key": api_key
    }

    print(f"🔍 Verifying persona {persona_id} tool configuration...")
    response = requests.get(url, headers=headers)

    if response.status_code == 200:
        persona_data = response.json()
        print("✅ Persona retrieved successfully!")
        
        # Check callback URL
        callback_url = persona_data.get('callback_url', 'Not found')
        print(f"📡 Callback URL: {callback_url}")
        
        # Check tools
        llm_tools = persona_data.get('layers', {}).get('llm', {}).get('tools', [])
        
        print(f"📋 Found {len(llm_tools)} tools configured:")
        found_tool = None
        for tool in llm_tools:
            if tool.get('type') == 'function' and tool.get('function', {}).get('name') == 'fetch_relevant_image':
                found_tool = tool
            print(f"  - {tool.get('function', {}).get('name', 'Unnamed tool')}: {tool.get('function', {}).get('description', 'No description')}")

        if found_tool:
            print("✅ fetch_relevant_image tool is properly configured!")
            return True
        else:
            print("❌ fetch_relevant_image tool NOT found in persona configuration.")
            return False
    else:
        print(f"❌ Failed to retrieve persona: HTTP {response.status_code}")
        print("📋 Error:", response.text)
        return False

if __name__ == "__main__":
    print("🔧 Updating Tavus Persona Tool Call Endpoint")
    print("=" * 60)

    if not TAVUS_API_KEY or not TAVUS_PERSONA_ID:
        print("❌ Missing TAVUS_API_KEY or TAVUS_PERSONA_ID in environment variables")
        print("🔍 Please set them in your .env.local file or environment")
        exit(1)

    print(f"🎯 Updating persona {TAVUS_PERSONA_ID}")
    print(f"🔗 New tool call endpoint: {NEW_TOOL_ENDPOINT}")
    
    # Update the callback URL
    if update_persona_tool_endpoint(TAVUS_PERSONA_ID, TAVUS_API_KEY, NEW_TOOL_ENDPOINT):
        print("\n✅ Persona callback URL updated successfully!")
        
        # Verify the update
        print("\n🔍 Verifying persona configuration...")
        if verify_persona_tools(TAVUS_PERSONA_ID, TAVUS_API_KEY):
            print("\n🎯 Persona is properly configured!")
            print("💡 The persona will now use the dedicated tool call endpoint")
            print("🚀 Try starting a new conversation and asking for images!")
        else:
            print("\n⚠️ Persona tools verification failed")
    else:
        print("\n❌ Failed to update persona callback URL")
        print("🔍 Check your API key and persona ID")
