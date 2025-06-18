import React, { useState } from 'react';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Badge } from '@/components/ui/badge';
import { Leaf, User, Mail, Loader2 } from 'lucide-react';
import type { RegistrationRequest } from '@/types';

interface UserRegistrationProps {
  onRegister: (userData: RegistrationRequest) => Promise<void>;
  isLoading?: boolean;
}

export const UserRegistration: React.FC<UserRegistrationProps> = ({
  onRegister,
  isLoading = false
}) => {
  const [formData, setFormData] = useState<RegistrationRequest>({
    name: '',
    email: ''
  });
  const [errors, setErrors] = useState<Partial<RegistrationRequest>>({});

  const validateForm = (): boolean => {
    const newErrors: Partial<RegistrationRequest> = {};

    if (!formData.name.trim()) {
      newErrors.name = 'Name is required';
    } else if (formData.name.trim().length < 2) {
      newErrors.name = 'Name must be at least 2 characters';
    }

    if (!formData.email.trim()) {
      newErrors.email = 'Email is required';
    } else if (!/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(formData.email)) {
      newErrors.email = 'Please enter a valid email address';
    }

    setErrors(newErrors);
    return Object.keys(newErrors).length === 0;
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    
    if (!validateForm()) return;

    try {
      await onRegister(formData);
    } catch (error) {
      console.error('Registration failed:', error);
    }
  };

  const handleInputChange = (field: keyof RegistrationRequest, value: string) => {
    setFormData(prev => ({ ...prev, [field]: value }));
    
    // Clear error when user starts typing
    if (errors[field]) {
      setErrors(prev => ({ ...prev, [field]: undefined }));
    }
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-renewable-50 to-green-100 flex items-center justify-center p-4">
      <Card className="w-full max-w-md shadow-lg border-0 bg-white/95 backdrop-blur">
        <CardHeader className="text-center space-y-4">
          <div className="mx-auto w-16 h-16 bg-renewable-100 rounded-full flex items-center justify-center">
            <Leaf className="w-8 h-8 text-renewable-600" />
          </div>
          
          <div>
            <CardTitle className="text-2xl font-serif text-renewable-800">
              Welcome to Renewable Energy Assistant
            </CardTitle>
            <CardDescription className="mt-2 text-renewable-600">
              Your AI-powered guide to sustainable energy solutions and calculations
            </CardDescription>
          </div>

          <div className="flex justify-center gap-2">
            <Badge variant="renewable" className="text-xs">
              🧮 Math Calculations
            </Badge>
            <Badge variant="renewable" className="text-xs">
              🔋 Energy Analysis
            </Badge>
            <Badge variant="renewable" className="text-xs">
              🌱 Eco Insights
            </Badge>
          </div>
        </CardHeader>

        <CardContent>
          <form onSubmit={handleSubmit} className="space-y-4">
            {/* Name Field */}
            <div>
              <label htmlFor="name" className="block text-sm font-medium text-gray-700 mb-2">
                <User className="w-4 h-4 inline mr-2" />
                Full Name
              </label>
              <Input
                id="name"
                type="text"
                value={formData.name}
                onChange={(e) => handleInputChange('name', e.target.value)}
                placeholder="Enter your full name"
                className={errors.name ? 'border-red-500 focus:ring-red-500' : ''}
                disabled={isLoading}
              />
              {errors.name && (
                <p className="text-red-500 text-xs mt-1">{errors.name}</p>
              )}
            </div>

            {/* Email Field */}
            <div>
              <label htmlFor="email" className="block text-sm font-medium text-gray-700 mb-2">
                <Mail className="w-4 h-4 inline mr-2" />
                Email Address
              </label>
              <Input
                id="email"
                type="email"
                value={formData.email}
                onChange={(e) => handleInputChange('email', e.target.value)}
                placeholder="Enter your email address"
                className={errors.email ? 'border-red-500 focus:ring-red-500' : ''}
                disabled={isLoading}
              />
              {errors.email && (
                <p className="text-red-500 text-xs mt-1">{errors.email}</p>
              )}
            </div>

            {/* Submit Button */}
            <Button
              type="submit"
              variant="renewable"
              size="lg"
              className="w-full"
              disabled={isLoading}
            >
              {isLoading ? (
                <>
                  <Loader2 className="w-4 h-4 mr-2 animate-spin" />
                  Creating Account...
                </>
              ) : (
                <>
                  <Leaf className="w-4 h-4 mr-2" />
                  Start Your Green Journey
                </>
              )}
            </Button>
          </form>

          <div className="mt-6 text-center text-xs text-muted-foreground">
            <p>By registering, you'll get personalized renewable energy insights</p>
            <p className="mt-1">and access to advanced calculation tools.</p>
          </div>
        </CardContent>
      </Card>
    </div>
  );
}; 