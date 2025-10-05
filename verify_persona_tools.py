#!/usr/bin/env python3
"""
Verify that the Tavus persona has the correct tool configuration
"""

import requests
import json
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

def verify_persona_tools():
    """Verify that the persona has the fetch_relevant_image tool configured"""
    
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
    
    print(f"🔍 Verifying persona {persona_id} tool configuration...")
    
    try:
        response = requests.get(url, headers=headers)
        
        if response.status_code == 200:
            persona_data = response.json()
            print("✅ Persona retrieved successfully!")
            
            # Check if tools are configured
            layers = persona_data.get('layers', {})
            llm_layer = layers.get('llm', {})
            tools = llm_layer.get('tools', [])
            
            print(f"📋 Found {len(tools)} tools configured:")
            
            fetch_image_tool = None
            for tool in tools:
                if tool.get('type') == 'function':
                    function = tool.get('function', {})
                    name = function.get('name', 'unknown')
                    description = function.get('description', 'no description')
                    print(f"  - {name}: {description}")
                    
                    if name == 'fetch_relevant_image':
                        fetch_image_tool = tool
            
            if fetch_image_tool:
                print("✅ fetch_relevant_image tool is properly configured!")
                print("📋 Tool details:")
                print(json.dumps(fetch_image_tool, indent=2))
                return True
            else:
                print("❌ fetch_relevant_image tool not found!")
                return False
                
        else:
            print(f"❌ Failed to retrieve persona: HTTP {response.status_code}")
            print(f"📋 Error: {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ Error retrieving persona: {e}")
        return False

if __name__ == "__main__":
    print("🔍 Verifying Tavus Persona Tool Configuration")
    print("=" * 60)
    
    success = verify_persona_tools()
    
    if success:
        print("\n✅ Persona is properly configured with tools!")
        print("🎯 You can now start a conversation and ask for images")
    else:
        print("\n❌ Persona tool configuration issue detected")
        print("🔧 Run update_tavus_persona.py to fix this")
