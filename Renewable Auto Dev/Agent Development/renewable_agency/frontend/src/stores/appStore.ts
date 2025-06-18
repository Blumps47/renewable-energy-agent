import { create } from 'zustand';
import { devtools, persist } from 'zustand/middleware';
import type { 
  AppState, 
  User, 
  Conversation, 
  ChatMessage, 
  UserPreferences 
} from '../types';

interface AppActions {
  // User actions
  setUser: (user: User | null) => void;
  updateUserPreferences: (preferences: UserPreferences) => void;
  
  // Conversation actions
  setCurrentConversation: (conversation: Conversation | null) => void;
  addConversation: (conversation: Conversation) => void;
  updateConversation: (conversation: Conversation) => void;
  
  // Message actions
  addMessage: (message: ChatMessage) => void;
  
  // UI state actions
  setLoading: (loading: boolean) => void;
  setError: (error: string | null) => void;
  clearError: () => void;
  
  // Utility actions
  reset: () => void;
}

type AppStore = AppState & AppActions;

const initialState: AppState = {
  user: null,
  currentConversation: null,
  conversations: [],
  isLoading: false,
  error: null,
};

export const useAppStore = create<AppStore>()(
  devtools(
    persist(
      (set, get) => ({
        ...initialState,
        
        // User actions
        setUser: (user) => set({ user }, false, 'setUser'),
        
        updateUserPreferences: (preferences) =>
          set(
            (state) => ({
              user: state.user
                ? { ...state.user, preferences: { ...state.user.preferences, ...preferences } }
                : null,
            }),
            false,
            'updateUserPreferences'
          ),
        
        // Conversation actions
        setCurrentConversation: (conversation) =>
          set({ currentConversation: conversation }, false, 'setCurrentConversation'),
        
        addConversation: (conversation) =>
          set(
            (state) => ({
              conversations: [conversation, ...state.conversations],
              currentConversation: conversation,
            }),
            false,
            'addConversation'
          ),
        
        updateConversation: (updatedConversation) =>
          set(
            (state) => ({
              conversations: state.conversations.map((conv) =>
                conv.id === updatedConversation.id ? updatedConversation : conv
              ),
              currentConversation:
                state.currentConversation?.id === updatedConversation.id
                  ? updatedConversation
                  : state.currentConversation,
            }),
            false,
            'updateConversation'
          ),
        
        // Message actions
        addMessage: (message) =>
          set(
            (state) => {
              if (!state.currentConversation) return state;
              
              const updatedConversation = {
                ...state.currentConversation,
                messages: [...state.currentConversation.messages, message],
                updatedAt: new Date(),
              };
              
              return {
                currentConversation: updatedConversation,
                conversations: state.conversations.map((conv) =>
                  conv.id === updatedConversation.id ? updatedConversation : conv
                ),
              };
            },
            false,
            'addMessage'
          ),
        
        // UI state actions
        setLoading: (isLoading) => set({ isLoading }, false, 'setLoading'),
        setError: (error) => set({ error }, false, 'setError'),
        clearError: () => set({ error: null }, false, 'clearError'),
        
        // Utility actions
        reset: () => set(initialState, false, 'reset'),
      }),
      {
        name: 'renewable-energy-app-store',
        partialize: (state) => ({
          user: state.user,
          conversations: state.conversations,
          currentConversation: state.currentConversation,
        }),
      }
    ),
    {
      name: 'renewable-energy-app',
    }
  )
);

// Selectors for better performance
export const useUser = () => useAppStore((state) => state.user);
export const useCurrentConversation = () => useAppStore((state) => state.currentConversation);
export const useConversations = () => useAppStore((state) => state.conversations);
export const useLoading = () => useAppStore((state) => state.isLoading);
export const useError = () => useAppStore((state) => state.error); 