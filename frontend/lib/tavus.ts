/**
 * Corrected Tavus API Integration
 * Based on official Tavus documentation and examples
 */

export interface TavusConfig {
  apiKey: string;
  personaId: string;
  replicaId: string;
  callbackUrl?: string;
}


export interface TavusConversation {
  conversation_id: string;
  conversation_url: string; // Changed from daily_room_url to conversation_url
  status: string;
  conversation_name?: string;
  callback_url?: string;
  created_at?: string;
}

export class TavusClient {
  private apiKey: string;
  private personaId: string;
  private replicaId: string;
  private baseUrl = 'https://tavusapi.com/v2';
  private sseConnectionId: string | null = null;
  private callbackUrl: string;

  constructor(config: TavusConfig) {
    this.apiKey = config.apiKey;
    this.personaId = config.personaId;
    this.replicaId = config.replicaId;
this.callbackUrl = config.callbackUrl || 'https://consulting-converter-insertion-maui.trycloudflare.com/api/tavus-webhook';
  }

  setSSEConnectionId(connectionId: string) {
    this.sseConnectionId = connectionId;
  }

  /**
   * Handle tool calls from Tavus - calls the tool call endpoint
   * This function is called when Tavus decides to use a tool
   */
  async handleToolCall(toolName: string, toolParams: any): Promise<any> {
    try {
      console.log('🔧 HANDLING TOOL CALL FROM FRONTEND');
      console.log(`🔧 Tool: ${toolName}`);
      console.log(`🔧 Params:`, toolParams);
      
      const response = await fetch(`${process.env.NEXT_PUBLIC_API_URL || 'http://localhost:5002'}/api/tavus-tool-call`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json'
        },
        body: JSON.stringify({
          tool_name: toolName,
          tool_params: toolParams,
          connection_id: this.sseConnectionId
        })
      });

      if (!response.ok) {
        throw new Error(`Tool call failed: ${response.statusText}`);
      }

      const result = await response.json();
      console.log('✅ Tool call result:', result);
      return result;
      
    } catch (error) {
      console.error('❌ Tool call error:', error);
      throw error;
    }
  }

  /**
   * Call the tool call endpoint when Tavus decides to use a tool
   * This function is called by the frontend when it receives a query from Tavus
   */
  async callTool(toolName: string, toolParams: any): Promise<any> {
    return this.handleToolCall(toolName, toolParams);
  }



  /**
   * Ensure persona has tools configured before creating conversation
   */
  async ensurePersonaHasTools(): Promise<boolean> {
    try {
      console.log('='.repeat(80));
      console.log('🔧 VERIFYING PERSONA TOOLS CONFIGURATION');
      console.log('='.repeat(80));
      console.log(`📡 Fetching persona: ${this.personaId}`);
      console.log(`🔑 API Key: ${this.apiKey.substring(0, 10)}...`);
      
      const response = await fetch(`${this.baseUrl}/personas/${this.personaId}`, {
        method: 'GET',
        headers: {
          'Content-Type': 'application/json',
          'x-api-key': this.apiKey
        }
      });

      console.log(`📊 Response status: ${response.status} ${response.statusText}`);

      if (!response.ok) {
        console.warn('⚠️ Could not verify persona tools:', response.statusText);
        console.log('='.repeat(80));
        return true; // Continue anyway
      }

      const persona = await response.json();
      console.log('📋 Persona data received:');
      console.log(`  - Persona Name: ${persona.persona_name || 'Unknown'}`);
      console.log(`  - Pipeline Mode: ${persona.pipeline_mode || 'Unknown'}`);
      
      const layers = persona.layers || {};
      const llmLayer = layers.llm || {};
      const tools = llmLayer.tools || [];
      
      console.log(`🔧 Found ${tools.length} tools in LLM layer:`);
      tools.forEach((tool: any, index: number) => {
        if (tool.type === 'function') {
          const func = tool.function || {};
          console.log(`  ${index + 1}. ${func.name || 'unnamed'}: ${func.description || 'no description'}`);
        } else {
          console.log(`  ${index + 1}. ${tool.type || 'unknown type'}`);
        }
      });

      const hasFetchImageTool = tools.some((tool: any) => 
        tool.type === 'function' && tool.function?.name === 'fetch_relevant_image'
      );

      if (hasFetchImageTool) {
        console.log('✅ SUCCESS: Persona has fetch_relevant_image tool configured');
        console.log('='.repeat(80));
        return true;
      } else {
        console.warn('❌ WARNING: Persona missing fetch_relevant_image tool - conversation may not work properly');
        console.log('🔧 Run update_tavus_persona.py to fix this');
        console.log('='.repeat(80));
        return false;
      }
    } catch (error) {
      console.warn('❌ ERROR: Could not verify persona tools:', error);
      console.log('='.repeat(80));
      return true; // Continue anyway
    }
  }

  /**
   * Create a new conversation with Tavus
   * Based on official Tavus API documentation
   */
  async createConversation(customGreeting?: string): Promise<TavusConversation> {
    try {
        console.log('='.repeat(80));
        console.log('🚀 CREATING TAVUS CONVERSATION');
        console.log('='.repeat(80));
        
        // Verify persona has tools configured
        console.log('🔧 Step 1: Verifying persona tools...');
        const toolsConfigured = await this.ensurePersonaHasTools();
        
        console.log('🔧 Step 2: Preparing conversation request...');
        const requestBody = {
          persona_id: this.personaId,
          replica_id: this.replicaId,
          custom_greeting: customGreeting || 'Hello! I\'m your ISS guide. Ask me anything about the International Space Station, and I can show you images too!',
          conversational_context: 'You are an expert guide for the International Space Station. You can show users images of different parts of the ISS, astronauts, and space activities. When users ask about visual aspects or want to see something, use the fetch_relevant_image tool to show them relevant images.',
          callback_url: this.callbackUrl, // General webhook endpoint
          properties: {
            max_call_duration: 3600,
            participant_left_timeout: 60,
            enable_recording: false,
            apply_greenscreen: false
          }
          // Note: tools are configured via webhook, not in conversation creation
        };
      
      console.log('📋 Request details:');
      console.log(`  - URL: ${this.baseUrl}/conversations`);
      console.log(`  - Persona ID: ${this.personaId}`);
      console.log(`  - Replica ID: ${this.replicaId}`);
      console.log(`  - API Key: ${this.apiKey.substring(0, 10)}...`);
      console.log(`  - Callback URL: ${requestBody.callback_url}`);
      console.log(`  - Tools configured: ${toolsConfigured ? 'YES' : 'NO'}`);
      console.log(`  - Custom greeting: ${requestBody.custom_greeting.substring(0, 50)}...`);
      
      console.log('🔧 Step 3: Sending API request to Tavus...');
      const response = await fetch(`${this.baseUrl}/conversations`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'x-api-key': this.apiKey
        },
        body: JSON.stringify(requestBody)
      });

      console.log(`📊 API Response: ${response.status} ${response.statusText}`);

      if (!response.ok) {
        let errorMessage = `HTTP ${response.status}: ${response.statusText}`;
        try {
          const errorData = await response.json();
          errorMessage += ` - ${errorData.message || errorData.error || 'Unknown error'}`;
          console.error('❌ Tavus API Error Details:', errorData);
        } catch (e) {
          console.error('❌ Could not parse error response:', e);
        }
        console.log('='.repeat(80));
        throw new Error(`Failed to create conversation: ${errorMessage}`);
      }

      console.log('🔧 Step 4: Processing successful response...');
      const data = await response.json();
      console.log('✅ SUCCESS: Tavus conversation created!');
      console.log('📋 Conversation details:');
      console.log(`  - Conversation ID: ${data.conversation_id}`);
      console.log(`  - Conversation URL: ${data.conversation_url}`);
      console.log(`  - Status: ${data.status}`);
      console.log(`  - Created at: ${data.created_at || 'Unknown'}`);
      
      // Note: Tools are already configured in the persona
      console.log('🎯 Ready to start video chat!');
      console.log('='.repeat(80));
      
      return data;
      
    } catch (error) {
      console.error('❌ Failed to create Tavus conversation:', error);
      throw error;
    }
  }



  /**
   * End the conversation
   */
  async endConversation(conversationId: string): Promise<void> {
    try {
      const response = await fetch(
        `${this.baseUrl}/conversations/${conversationId}`,
        {
          method: 'DELETE',
          headers: {
            'x-api-key': this.apiKey
          }
        }
      );

      if (!response.ok) {
        throw new Error(`Failed to end conversation: ${response.statusText}`);
      }

      console.log('✅ Tavus conversation ended');
      
    } catch (error) {
      console.error('❌ Failed to end conversation:', error);
      throw error;
    }
  }

  getPersonaId(): string {
    return this.personaId;
  }

  getReplicaId(): string {
    return this.replicaId;
  }
}
