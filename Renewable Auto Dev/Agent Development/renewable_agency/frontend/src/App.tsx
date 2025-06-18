import React, { useEffect, useState } from 'react';
import { UserRegistration } from './components/UserRegistration';
import { ChatInterface } from './components/ChatInterface';
import { useAppStore, useUser } from './stores/appStore';
import { apiService } from './services/api';
import type { RegistrationRequest } from './types';
import './index.css';

const App: React.FC = () => {
  const user = useUser();
  const { setUser, setLoading, setError, clearError } = useAppStore();
  const [isInitialized, setIsInitialized] = useState(false);

  useEffect(() => {
    // Initialize app - check if user exists in local storage
    const initializeApp = async () => {
      try {
        setLoading(true);
        
        // Check if we have a stored user
        const storedUser = localStorage.getItem('renewable-energy-app-store');
        if (storedUser) {
          const parsedStore = JSON.parse(storedUser);
          if (parsedStore.state?.user) {
            // User exists in storage, no need to register again
            setIsInitialized(true);
            setLoading(false);
            return;
          }
        }
        
        // No user found, will show registration
        setIsInitialized(true);
      } catch (error) {
        console.error('App initialization error:', error);
        setError('Failed to initialize application');
      } finally {
        setLoading(false);
      }
    };

    initializeApp();
  }, [setLoading, setError]);

  const handleUserRegistration = async (userData: RegistrationRequest) => {
    try {
      setLoading(true);
      clearError();

      // Register user with backend
      const response = await apiService.registerUser(userData);
      
      if (response.success && response.data) {
        // Store user in global state (will be persisted by zustand)
        setUser(response.data);
        console.log('User registered successfully:', response.data);
      } else {
        throw new Error(response.error || 'Registration failed');
      }
    } catch (error: any) {
      console.error('Registration error:', error);
      setError(error.message || 'Failed to register user. Please try again.');
      throw error; // Re-throw to handle in UserRegistration component
    } finally {
      setLoading(false);
    }
  };

  // Show loading state while initializing
  if (!isInitialized) {
    return (
      <div className="min-h-screen bg-gradient-to-br from-renewable-50 to-green-100 flex items-center justify-center">
        <div className="text-center">
          <div className="w-16 h-16 bg-renewable-100 rounded-full flex items-center justify-center mx-auto mb-4 animate-pulse">
            <div className="w-8 h-8 bg-renewable-600 rounded-full animate-spin"></div>
          </div>
          <p className="text-renewable-700 font-serif">Loading Renewable Energy Assistant...</p>
        </div>
      </div>
    );
  }

  // Show registration if no user
  if (!user) {
    return (
      <UserRegistration 
        onRegister={handleUserRegistration}
        isLoading={false}
      />
    );
  }

  // Show main chat interface
  return <ChatInterface />;
};

export default App; 