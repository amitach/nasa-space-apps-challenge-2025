#!/usr/bin/env python3
"""
Fix Tavus tool configuration to match official documentation exactly
Based on: https://docs.tavus.io/sections/conversational-video-interface/persona/llm-tool
"""

import requests
import json
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

def fix_tavus_tool():
    """Fix the Tavus tool configuration to match official documentation"""
    
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
    
    # Tool configuration based on official Tavus documentation
    # This matches the exact format from the docs
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
    
    print(f"🔧 Fixing persona {persona_id} tool configuration...")
    print(f"📡 URL: {url}")
    print(f"🔑 API Key: {api_key[:10]}...")
    print("📋 Tool configuration:")
    print(json.dumps(tools_config[0]["value"][0], indent=2))
    
    try:
        response = requests.patch(url, headers=headers, json=tools_config)
        
        if response.status_code == 200:
            print("✅ Successfully fixed persona tool configuration!")
            persona_data = response.json()
            
            # Verify the tool was updated correctly
            tools = persona_data.get('layers', {}).get('llm', {}).get('tools', [])
            print(f"📋 Updated persona has {len(tools)} tools:")
            for i, tool in enumerate(tools):
                if tool.get('type') == 'function':
                    func = tool.get('function', {})
                    print(f"  {i+1}. {func.get('name')}: {func.get('description')}")
                    print(f"     Parameters: {func.get('parameters', {}).get('properties', {}).keys()}")
                    print(f"     Required: {func.get('parameters', {}).get('required', [])}")
            
            return True
        else:
            print(f"❌ Failed to fix persona: HTTP {response.status_code}")
            print(f"📋 Error: {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ Error fixing persona: {e}")
        return False

if __name__ == "__main__":
    print("🔧 Fixing Tavus Tool Configuration")
    print("=" * 60)
    
    success = fix_tavus_tool()
    
    if success:
        print("\n✅ Tool configuration fixed!")
        print("🎯 Try starting a new conversation and asking for images")
    else:
        print("\n❌ Failed to fix tool configuration")
        print("🔍 Check your API key and persona ID")
