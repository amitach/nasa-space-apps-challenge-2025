#!/usr/bin/env python3
"""
Update Tavus persona with EXACT tool format from official documentation
Based on: https://docs.tavus.io/sections/conversational-video-interface/persona/llm-tool#example-configuration
"""

import requests
import json
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

def update_tavus_tool_exact():
    """Update the Tavus persona with the exact tool format from documentation"""
    
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
    
    # EXACT tool configuration from Tavus documentation
    # This matches their example exactly
    tools_config = [
        {
            "op": "replace",
            "path": "/layers/llm/tools",
            "value": [
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
        }
    ]
    
    print(f"🔧 Updating persona {persona_id} with EXACT Tavus documentation format...")
    print(f"📡 URL: {url}")
    print(f"🔑 API Key: {api_key[:10]}...")
    print("📋 Tool configuration (exact from docs):")
    print(json.dumps(tools_config[0]["value"][0], indent=2))
    
    try:
        response = requests.patch(url, headers=headers, json=tools_config)
        
        print(f"📊 Response status: {response.status_code}")
        
        if response.status_code == 200:
            print("✅ Successfully updated persona with exact tool format!")
            persona_data = response.json()
            
            # Verify the tool was updated correctly
            tools = persona_data.get('layers', {}).get('llm', {}).get('tools', [])
            print(f"📋 Updated persona has {len(tools)} tools:")
            for i, tool in enumerate(tools):
                if tool.get('type') == 'function':
                    func = tool.get('function', {})
                    print(f"  {i+1}. {func.get('name')}: {func.get('description')}")
                    params = func.get('parameters', {})
                    print(f"     Type: {params.get('type')}")
                    print(f"     Properties: {list(params.get('properties', {}).keys())}")
                    print(f"     Required: {params.get('required', [])}")
            
            return True
        else:
            print(f"❌ Failed to update persona: HTTP {response.status_code}")
            try:
                error_data = response.json()
                print(f"📋 Error details: {json.dumps(error_data, indent=2)}")
            except:
                print(f"📋 Error text: {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ Error updating persona: {e}")
        return False

if __name__ == "__main__":
    print("🔧 Updating Tavus Tool with EXACT Documentation Format")
    print("=" * 60)
    
    success = update_tavus_tool_exact()
    
    if success:
        print("\n✅ Tool updated with exact Tavus documentation format!")
        print("🎯 Try starting a new conversation and asking for images")
        print("💡 The tool should now work exactly as per Tavus docs")
    else:
        print("\n❌ Failed to update tool configuration")
        print("🔍 Check the error details above")
