import React from 'react';
import { Card, CardContent } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { Bot, User, Leaf, Calculator } from 'lucide-react';
import type { ChatMessage as ChatMessageType } from '@/types';
import { cn } from '@/lib/utils';

interface ChatMessageProps {
  message: ChatMessageType;
}

export const ChatMessage: React.FC<ChatMessageProps> = ({ message }) => {
  const isUser = message.sender === 'user';
  const timestamp = new Date(message.timestamp).toLocaleTimeString([], { 
    hour: '2-digit', 
    minute: '2-digit' 
  });

  return (
    <div className={cn("flex gap-3 max-w-4xl", isUser ? "flex-row-reverse" : "flex-row")}>
      {/* Avatar */}
      <div className={cn(
        "flex-shrink-0 w-8 h-8 rounded-full flex items-center justify-center",
        isUser ? "bg-primary text-primary-foreground" : "bg-renewable-100 text-renewable-700"
      )}>
        {isUser ? (
          <User className="w-4 h-4" />
        ) : (
          <Bot className="w-4 h-4" />
        )}
      </div>

      {/* Message Content */}
      <div className={cn("flex-1 space-y-2", isUser ? "items-end" : "items-start")}>
        <Card className={cn(
          "max-w-[80%]",
          isUser 
            ? "bg-primary text-primary-foreground ml-auto" 
            : "bg-card"
        )}>
          <CardContent className="p-4">
            <div className="space-y-2">
              {/* Main Message */}
              <p className="text-sm leading-relaxed font-serif">
                {message.content}
              </p>

              {/* Math Response Card */}
              {message.mathResponse && (
                <div className="mt-3 p-3 rounded-lg bg-background/10 border">
                  <div className="flex items-center gap-2 mb-2">
                    <Calculator className="w-4 h-4" />
                    <span className="text-sm font-semibold">Mathematical Analysis</span>
                  </div>
                  
                  <div className="space-y-2 text-sm">
                    <div className="flex items-center justify-between">
                      <span className="text-muted-foreground">Result:</span>
                      <Badge variant="renewable" className="font-mono">
                        {message.mathResponse.result}
                      </Badge>
                    </div>
                    
                    <div className="flex items-center justify-between">
                      <span className="text-muted-foreground">Operation:</span>
                      <span className="font-mono text-xs">
                        {message.mathResponse.operation}
                      </span>
                    </div>
                    
                    {message.mathResponse.confidence && (
                      <div className="flex items-center justify-between">
                        <span className="text-muted-foreground">Confidence:</span>
                        <Badge variant={message.mathResponse.confidence > 0.8 ? "renewable" : "secondary"}>
                          {Math.round(message.mathResponse.confidence * 100)}%
                        </Badge>
                      </div>
                    )}
                  </div>

                  {/* Renewable Context */}
                  {message.mathResponse.renewable_context && (
                    <div className="mt-3 p-3 rounded-md bg-renewable-50 border border-renewable-200">
                      <div className="flex items-center gap-2 mb-2">
                        <Leaf className="w-4 h-4 text-renewable-600" />
                        <span className="text-sm font-medium text-renewable-800">
                          Renewable Energy Context
                        </span>
                      </div>
                      <p className="text-sm text-renewable-700 leading-relaxed">
                        {message.mathResponse.renewable_context}
                      </p>
                    </div>
                  )}

                  {/* Environmental Impact */}
                  {message.mathResponse.environmental_impact && (
                    <div className="mt-2 text-xs text-muted-foreground italic">
                      💚 {message.mathResponse.environmental_impact}
                    </div>
                  )}
                </div>
              )}
            </div>
          </CardContent>
        </Card>

        {/* Timestamp */}
        <div className={cn(
          "text-xs text-muted-foreground px-1",
          isUser ? "text-right" : "text-left"
        )}>
          {timestamp}
        </div>
      </div>
    </div>
  );
}; 