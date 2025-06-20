import React, { useEffect, useRef, useState } from 'react';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Badge } from '@/components/ui/badge';
import { ChatMessage } from './ChatMessage';
import { ChatInput } from './ChatInput';
import { useAppStore, useUser, useCurrentConversation, useLoading, useError } from '@/stores/appStore';
import { apiService } from '@/services/api';
import { 
  Leaf, 
  MessageCircle, 
  Trash2, 
  Download,
  Loader2,
  AlertCircle,
  RefreshCw
} from 'lucide-react';
import type { ChatMessage as ChatMessageType, Conversation } from '@/types';

export const ChatInterface: React.FC = () => {
  const messagesEndRef = useRef<HTMLDivElement>(null);
  const user = useUser();
  const currentConversation = useCurrentConversation();
  const isLoading = useLoading();
  const error = useError();
  
  const { 
    addMessage, 
    setLoading, 
    setError, 
    clearError,
    setCurrentConversation,
    addConversation 
  } = useAppStore();

  const [isConnected, setIsConnected] = useState(false);

  // Scroll to bottom when new messages arrive
  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [currentConversation?.messages]);

  // Check API connection on mount
  useEffect(() => {
    checkConnection();
  }, []);

  const checkConnection = async () => {
    try {
      console.log('🔍 Checking API connection...');
      const response = await apiService.healthCheck();
      console.log('✅ API connection successful:', response);
      setIsConnected(true);
      clearError();
    } catch (error) {
      console.error('❌ API connection failed:', error);
      setIsConnected(false);
      setError('Failed to connect to the server. Please check if the backend is running.');
    }
  };

  // Create a new conversation if none exists
  const createNewConversation = (): Conversation => {
    const newConversation: Conversation = {
      id: `conv_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`,
      userId: user?.id || 'anonymous',
      messages: [],
      createdAt: new Date(),
      updatedAt: new Date(),
    };
    return newConversation;
  };

  const handleSendMessage = async (messageContent: string) => {
    console.log('🚀 Starting message send...');
    console.log('📝 Message:', messageContent);
    console.log('👤 User:', user);
    console.log('💬 Current Conversation:', currentConversation);
    
    if (!user || !messageContent.trim()) return;

    try {
      setLoading(true);
      clearError();

      // Create conversation if none exists
      let conversation = currentConversation;
      if (!conversation) {
        conversation = createNewConversation();
        addConversation(conversation);
        console.log('📁 Created new conversation:', conversation);
      }

      // Add user message
      const userMessage: ChatMessageType = {
        id: `msg_${Date.now()}_user`,
        content: messageContent,
        sender: 'user',
        timestamp: new Date(),
      };
      addMessage(userMessage);
      console.log('📤 Added user message:', userMessage);

      // Send to API
      console.log('📡 Making API request with data:', {
        message: messageContent,
        userId: user.user_id,
        conversationId: conversation.id,
      });
      
      const response = await apiService.sendMessage({
        message: messageContent,
        userId: user.user_id,
        conversationId: conversation.id,
      });

      console.log('✅ API Response received:', response);
      console.log('📊 Response structure:', JSON.stringify(response, null, 2));
      console.log('🔍 Response.success:', response.success);
      console.log('🔍 Response.data:', response.data);

      if (response.success && response.data) {
        // The backend returns: { response: "...", math_response: {...} }
        const responseData = response.data;
        console.log('🔍 Parsing response data:', responseData);
        console.log('🔍 responseData.response:', responseData.response);
        console.log('🔍 responseData.math_response:', responseData.math_response);
        
        let content = '';
        
        // Use the main response first
        if (responseData.response) {
          content = responseData.response;
          console.log('✅ Using main response:', content);
        }
        // Fallback to math_response.renewable_context if main response is empty
        else if (responseData.math_response?.renewable_context && responseData.math_response.renewable_context !== 'N/A') {
          content = responseData.math_response.renewable_context;
          console.log('✅ Using renewable_context:', content);
        }
        // Fallback to math_response.explanation
        else if (responseData.math_response?.explanation && responseData.math_response.explanation !== 'N/A') {
          content = responseData.math_response.explanation;
          console.log('✅ Using explanation:', content);
        }
        else {
          content = 'I received your message but couldn\'t generate a proper response. Please try asking about renewable energy topics or math calculations.';
          console.log('⚠️ Using fallback message:', content);
        }
        
        // Add calculation details if available from math_response
        const mathData = responseData.math_response;
        if (mathData?.operation && mathData.operation !== 'N/A' && mathData.operation !== 'information' && mathData.result !== undefined) {
          content += `\n\nCalculation: ${mathData.operation} = ${mathData.result}`;
          if (mathData.units) {
            content += ` ${mathData.units}`;
          }
        }

        // Add assistant response
        const assistantMessage: ChatMessageType = {
          id: `msg_${Date.now()}_assistant`,
          content: content,
          sender: 'assistant',
          timestamp: new Date(),
          mathResponse: mathData,
        };
        addMessage(assistantMessage);
      } else {
        console.log('❌ Response not successful or no data');
        console.log('❌ Response.success:', response.success);
        console.log('❌ Response.error:', response.error);
        console.log('❌ Full response:', response);
        throw new Error(response.error || 'Failed to get response');
      }
    } catch (error: any) {
      console.error('🚨 Error sending message:', error);
      console.error('🚨 Error stack:', error.stack);
      console.error('🚨 Error message:', error.message);
      setError(error.message || 'Failed to send message');
      
      // Add error message
      const errorMessage: ChatMessageType = {
        id: `msg_${Date.now()}_error`,
        content: `I apologize, but I encountered an error: ${error.message}. Please try again.`,
        sender: 'assistant',
        timestamp: new Date(),
      };
      addMessage(errorMessage);
    } finally {
      setLoading(false);
    }
  };

  const handleClearConversation = () => {
    if (currentConversation) {
      const clearedConversation: Conversation = {
        ...currentConversation,
        messages: [],
        updatedAt: new Date(),
      };
      setCurrentConversation(clearedConversation);
    }
  };

  const handleExportConversation = () => {
    if (!currentConversation || currentConversation.messages.length === 0) return;

    const exportData = {
      conversation: currentConversation,
      exported_at: new Date().toISOString(),
      user: user?.name || 'Anonymous User',
    };

    const blob = new Blob([JSON.stringify(exportData, null, 2)], {
      type: 'application/json',
    });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = `renewable-energy-chat-${new Date().toISOString().split('T')[0]}.json`;
    document.body.appendChild(a);
    a.click();
    document.body.removeChild(a);
    URL.revokeObjectURL(url);
  };

  const messages = currentConversation?.messages || [];
  const hasMessages = messages.length > 0;

  return (
    <div className="flex flex-col h-screen bg-gradient-to-br from-renewable-50 to-green-50">
      {/* Header */}
      <div className="border-b bg-white/95 backdrop-blur shadow-sm">
        <div className="max-w-4xl mx-auto px-4 py-3">
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-3">
              <div className="w-10 h-10 bg-renewable-100 rounded-full flex items-center justify-center">
                <Leaf className="w-5 h-5 text-renewable-600" />
              </div>
              <div>
                <h1 className="text-lg font-serif font-semibold text-renewable-800">
                  Renewable Energy Assistant
                </h1>
                <div className="flex items-center gap-2 text-sm text-muted-foreground">
                  <Badge variant={isConnected ? "renewable" : "destructive"} className="text-xs">
                    {isConnected ? "🟢 Connected" : "🔴 Disconnected"}
                  </Badge>
                  {user && (
                    <span>• Welcome, {user.name}</span>
                  )}
                </div>
              </div>
            </div>

            <div className="flex items-center gap-2">
              {!isConnected && (
                <Button 
                  variant="outline" 
                  size="sm" 
                  onClick={checkConnection}
                  disabled={isLoading}
                >
                  <RefreshCw className="w-4 h-4 mr-2" />
                  Retry Connection
                </Button>
              )}
              
              {hasMessages && (
                <>
                  <Button 
                    variant="outline" 
                    size="sm" 
                    onClick={handleExportConversation}
                  >
                    <Download className="w-4 h-4 mr-2" />
                    Export
                  </Button>
                  <Button 
                    variant="outline" 
                    size="sm" 
                    onClick={handleClearConversation}
                  >
                    <Trash2 className="w-4 h-4 mr-2" />
                    Clear
                  </Button>
                </>
              )}
            </div>
          </div>
        </div>
      </div>
      
      {/* Error Display */}
      {error && (
        <div className="bg-red-50 border-b border-red-200 px-4 py-3">
          <div className="max-w-4xl mx-auto flex items-center gap-2 text-red-700">
            <AlertCircle className="w-4 h-4" />
            <span className="text-sm">{error}</span>
            <Button variant="ghost" size="sm" onClick={clearError} className="ml-auto">
              ✕
            </Button>
          </div>
        </div>
      )}

      {/* Messages Area */}
      <div className="flex-1 overflow-y-auto p-4">
        <div className="max-w-4xl mx-auto space-y-6">
          {!hasMessages ? (
            <div className="text-center py-12">
              <Card className="max-w-md mx-auto bg-white/70 backdrop-blur">
                <CardHeader>
                  <div className="w-16 h-16 bg-renewable-100 rounded-full flex items-center justify-center mx-auto mb-4">
                    <MessageCircle className="w-8 h-8 text-renewable-600" />
                  </div>
                  <CardTitle className="text-center font-serif text-renewable-800">
                    Start Your Conversation
                  </CardTitle>
                </CardHeader>
                <CardContent>
                  <p className="text-sm text-muted-foreground text-center mb-4">
                    I'm here to help you with renewable energy calculations, 
                    sustainability insights, and mathematical analysis.
                  </p>
                  <div className="flex flex-wrap justify-center gap-2 text-xs">
                    <Badge variant="outline">Solar Panel Calculations</Badge>
                    <Badge variant="outline">Wind Energy Analysis</Badge>
                    <Badge variant="outline">Math Operations</Badge>
                    <Badge variant="outline">Carbon Footprint</Badge>
                  </div>
                </CardContent>
              </Card>
            </div>
          ) : (
            <>
              {messages.map((message) => (
                <ChatMessage key={message.id} message={message} />
              ))}
              
              {/* Loading indicator */}
              {isLoading && (
                <div className="flex gap-3 max-w-4xl">
                  <div className="flex-shrink-0 w-8 h-8 rounded-full bg-renewable-100 text-renewable-700 flex items-center justify-center">
                    <Loader2 className="w-4 h-4 animate-spin" />
                  </div>
                  <Card className="bg-card">
                    <CardContent className="p-4">
                      <div className="flex items-center gap-2 text-sm text-muted-foreground">
                        <span className="loading-dots">Thinking</span>
                      </div>
                    </CardContent>
                  </Card>
                </div>
              )}
            </>
          )}
          <div ref={messagesEndRef} />
        </div>
      </div>

      {/* Input Area */}
      <ChatInput
        onSendMessage={handleSendMessage}
        isLoading={isLoading}
        disabled={!isConnected}
        placeholder={
          !isConnected 
            ? "Please check your connection to start chatting..." 
            : "Ask me about renewable energy or math calculations..."
        }
      />
    </div>
  );
}; 