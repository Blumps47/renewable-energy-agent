import axios from 'axios';
import type {
  ApiResponse,
  ChatRequest,
  RegistrationRequest,
  User,
  Conversation,
  UserPreferences,
  MathResponse,
} from '../types';

// Create axios instance with base configuration
const api = axios.create({
  baseURL: '/api',
  timeout: 30000,
  headers: {
    'Content-Type': 'application/json',
  },
});

// Request interceptor for debugging
api.interceptors.request.use(
  (config) => {
    console.log(`🚀 ${config.method?.toUpperCase()} ${config.url}`, config.data);
    return config;
  },
  (error) => {
    console.error('Request error:', error);
    return Promise.reject(error);
  }
);

// Response interceptor for error handling
api.interceptors.response.use(
  (response) => {
    console.log(`✅ ${response.config.method?.toUpperCase()} ${response.config.url}`, response.data);
    return response;
  },
  (error) => {
    console.error('API Error:', error.response?.data || error.message);
    return Promise.reject(error);
  }
);

export const apiService = {
  // Health check
  async healthCheck(): Promise<ApiResponse> {
    try {
      const response = await api.get('/health');
      return response.data;
    } catch (error: any) {
      throw new Error(error.response?.data?.message || 'Health check failed');
    }
  },

  // User registration
  async registerUser(userData: RegistrationRequest): Promise<ApiResponse<User>> {
    try {
      const response = await api.post('/register', userData);
      return response.data;
    } catch (error: any) {
      throw new Error(error.response?.data?.message || 'Registration failed');
    }
  },

  // Chat with agent
  async sendMessage(chatData: ChatRequest): Promise<ApiResponse<{ response: string; math_response?: MathResponse }>> {
    try {
      const response = await api.post('/chat', chatData);
      return response.data;
    } catch (error: any) {
      throw new Error(error.response?.data?.message || 'Failed to send message');
    }
  },

  // Get conversation history
  async getConversation(userId: string): Promise<ApiResponse<Conversation[]>> {
    try {
      const response = await api.get(`/conversation/${userId}`);
      return response.data;
    } catch (error: any) {
      throw new Error(error.response?.data?.message || 'Failed to get conversation');
    }
  },

  // Update user preferences
  async updateUserPreferences(userId: string, preferences: UserPreferences): Promise<ApiResponse> {
    try {
      const response = await api.post('/user/preferences', { user_id: userId, ...preferences });
      return response.data;
    } catch (error: any) {
      throw new Error(error.response?.data?.message || 'Failed to update preferences');
    }
  },
};

export default apiService; 