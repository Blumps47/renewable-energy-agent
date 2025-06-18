# 🌱 Renewable Energy Assistant - Frontend

A beautiful, modern React frontend for the Renewable Energy Assistant AI chatbot, built with cutting-edge technologies.

## ✨ **Features**

### 🎨 **Modern UI/UX**
- **shadcn/ui** components for consistent, accessible interface
- **TailwindCSS** for responsive, utility-first styling
- **Lucide React** icons for beautiful iconography
- **Serif fonts** (Georgia, Cambria) for elegant typography
- **Renewable energy theme** with green color palette

### 🔧 **Technical Stack**
- **React 18** with TypeScript for type safety
- **Vite** for fast development and building
- **Zustand** for lightweight state management
- **Axios** for API communication
- **Real-time chat interface** with auto-scroll
- **Local storage persistence** for user data

### 🤖 **AI Integration**
- **Seamless backend integration** with FastAPI
- **Mathematical calculations** with renewable energy context
- **Structured responses** with confidence scores
- **Error handling** and connection status monitoring

## 🚀 **Quick Start**

### Prerequisites
- Node.js 16+ 
- npm or yarn
- Backend server running on `http://localhost:8000`

### Installation
```bash
# Install dependencies
npm install

# Start development server
npm run dev

# Build for production
npm run build

# Preview production build
npm run preview
```

## 📱 **User Interface**

### 🔐 **User Registration**
- Beautiful welcome screen with renewable energy branding
- Form validation with real-time feedback
- Automatic user persistence with Zustand

### 💬 **Chat Interface**
- **Clean, modern chat layout**
- **Auto-resizing input** with keyboard shortcuts
- **Message bubbles** with timestamps
- **Mathematical analysis cards** with:
  - Calculation results
  - Operation details
  - Confidence scores
  - Renewable energy context
  - Environmental impact

### 🎛️ **Features**
- **Connection status** indicator
- **Export conversations** to JSON
- **Clear conversation** history
- **Responsive design** for all devices
- **Loading states** and error handling

## 🛠️ **Development**

### Project Structure
```
frontend/
├── src/
│   ├── components/           # React components
│   │   ├── ui/              # shadcn/ui components
│   │   ├── ChatInterface.tsx
│   │   ├── ChatMessage.tsx
│   │   ├── ChatInput.tsx
│   │   └── UserRegistration.tsx
│   ├── stores/              # Zustand state management
│   │   └── appStore.ts
│   ├── services/            # API service layer
│   │   └── api.ts
│   ├── types/               # TypeScript definitions
│   │   └── index.ts
│   ├── lib/                 # Utility functions
│   │   └── utils.ts
│   ├── App.tsx             # Main application
│   ├── main.tsx            # Entry point
│   └── index.css           # Global styles
├── package.json
├── tailwind.config.js      # TailwindCSS configuration
├── vite.config.ts          # Vite configuration
└── tsconfig.json           # TypeScript configuration
```

### Key Components

#### **ChatInterface** 
Main chat component with:
- Message rendering
- API integration  
- Connection monitoring
- Export/clear functionality

#### **ChatMessage**
Individual message component featuring:
- User/assistant styling
- Math response cards
- Renewable energy context
- Confidence indicators

#### **UserRegistration**
Onboarding component with:
- Form validation
- Beautiful welcome screen
- Registration flow

### State Management (Zustand)
```typescript
// Global state includes:
- user: User | null
- currentConversation: Conversation | null
- conversations: Conversation[]
- isLoading: boolean
- error: string | null

// Actions include:
- setUser, updateUserPreferences
- addConversation, updateConversation
- addMessage
- setLoading, setError, clearError
```

## 🎨 **Styling & Theming**

### TailwindCSS Configuration
- **Custom renewable energy colors** (green palette)
- **Serif font family** integration
- **shadcn/ui compatibility**
- **Responsive breakpoints**
- **Dark mode support** (prepared)

### Custom CSS Classes
```css
.renewable-gradient     # Green gradient background
.chat-bubble           # Message bubble styling
.loading-dots          # Animated loading indicator
```

## 🔌 **API Integration**

### Endpoints Used
- `GET /api/health` - Health check
- `POST /api/register` - User registration
- `POST /api/chat` - Send messages
- `GET /api/conversation/{user_id}` - Get history
- `POST /api/user/preferences` - Update preferences

### Error Handling
- **Network error** detection
- **Connection status** monitoring
- **User-friendly error** messages
- **Automatic retry** functionality

## 📦 **Build & Deployment**

### Development
```bash
npm run dev          # Start dev server (http://localhost:3000)
npm run lint         # Run ESLint
```

### Production
```bash
npm run build        # Build for production
npm run preview      # Preview production build
```

### Environment Variables
The app expects the backend to be running on `http://localhost:8000`. 
To change this, update the `baseURL` in `src/services/api.ts`.

## 🧪 **Testing**

### Manual Testing Checklist
- [ ] User registration flow
- [ ] Chat message sending/receiving
- [ ] Mathematical calculations display
- [ ] Connection status updates
- [ ] Export functionality
- [ ] Responsive design
- [ ] Error states
- [ ] Loading states

## 🎯 **Future Enhancements**

### Planned Features
- [ ] **Dark mode** toggle
- [ ] **Conversation history** sidebar
- [ ] **Message search** functionality
- [ ] **File upload** for energy data
- [ ] **Charts and graphs** for calculations
- [ ] **Real-time notifications**
- [ ] **Progressive Web App** features
- [ ] **Voice input** support

### Technical Improvements
- [ ] **Unit testing** with Jest/React Testing Library
- [ ] **E2E testing** with Cypress
- [ ] **Bundle analysis** and optimization
- [ ] **PWA** service worker
- [ ] **WebSocket** for real-time updates

## 🤝 **Contributing**

1. **Fork the repository**
2. **Create feature branch** (`git checkout -b feature/amazing-feature`)
3. **Commit changes** (`git commit -m 'Add amazing feature'`)
4. **Push to branch** (`git push origin feature/amazing-feature`)
5. **Open Pull Request**

## 📄 **License**

This project is part of the Renewable Energy Assistant application.

---

**Built with ❤️ for a sustainable future** 🌍✨ 