export interface User {
  user_id: string;
  name: string;
  email: string;
  interests?: string[];
  registered_at?: string;
  preferences?: UserPreferences;
}

export interface UserPreferences {
  theme?: 'light' | 'dark';
  notifications?: boolean;
  energyUnits?: 'metric' | 'imperial';
}

export interface MathResponse {
  result: number;
  operation: string;
  explanation: string;
  renewable_context: string;
  confidence: number;
  environmental_impact?: string;
}

export interface ChatMessage {
  id: string;
  content: string;
  sender: 'user' | 'assistant';
  timestamp: Date;
  mathResponse?: MathResponse;
}

export interface Conversation {
  id: string;
  userId: string;
  messages: ChatMessage[];
  createdAt: Date;
  updatedAt: Date;
}

export interface ApiResponse<T = any> {
  success: boolean;
  data?: T;
  error?: string;
  message?: string;
}

export interface ChatRequest {
  message: string;
  userId: string;
  conversationId?: string;
}

export interface RegistrationRequest {
  name: string;
  email: string;
}

export interface AppState {
  user: User | null;
  currentConversation: Conversation | null;
  conversations: Conversation[];
  isLoading: boolean;
  error: string | null;
} 