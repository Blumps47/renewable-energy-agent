# Renewable Energy Analyst Agent

A full-stack intelligent agent application that provides renewable energy analysis capabilities through a conversational interface. The system combines AI-powered analysis with document retrieval to deliver comprehensive renewable energy insights.

## 🚀 Quick Start

### Prerequisites
- Python 3.10+  
- Node.js 18+ (for frontend)
- OpenAI API Key
- Supabase Account (optional, for database features)

### Backend Setup

1. **Clone and navigate to the project:**
   ```bash
   cd "Agent Development/renewable_agency"
   ```

2. **Create virtual environment:**
   ```bash
   python -m venv venv
   
   # Windows
   venv\Scripts\activate
   
   # macOS/Linux  
   source venv/bin/activate
   ```

3. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

4. **Set up environment variables:**
   ```bash
   cp .env.example .env
   # Edit .env and add your API keys
   ```

5. **Run the backend:**
   ```bash
   cd backend
   python main.py
   ```

   Or with uvicorn directly:
   ```bash
   uvicorn main:app --reload --host localhost --port 8000
   ```

### Testing the Agent

#### Interactive Agent Test
```bash
cd backend
python -m agent.renewable_agent
```

#### Run Test Suite
```bash
cd backend
python run_tests.py
```

#### API Testing with Curl

**Health Check:**
```bash
curl -X GET "http://localhost:8000/api/health"
```

**Chat with Agent:**
```bash
curl -X POST "http://localhost:8000/api/chat" \
  -H "Content-Type: application/json" \
  -d '{"message": "What is 15 + 25?"}'
```

**Register User:**
```bash
curl -X POST "http://localhost:8000/api/register" \
  -H "Content-Type: application/json" \
  -d '{"name": "John Doe", "email": "john@example.com"}'
```

## 🏗️ Architecture

### Backend Structure
```
backend/
├── main.py                 # FastAPI application entry point
├── agent/
│   ├── renewable_agent.py  # PydanticAI agent implementation  
│   ├── models.py          # Pydantic response models
│   └── tools.py           # Agent tools (math operations)
├── tests/
│   ├── test_agent.py      # Agent tests
│   └── test_api.py        # API tests
└── logs/
    └── test_results.log   # Test execution logs
```

### Key Components

#### 🤖 PydanticAI Agent
- **Model:** OpenAI GPT-4o-mini
- **Tools:** Add, subtract, multiply, divide operations
- **Memory:** Conversation history and user preferences
- **Response:** Structured `MathResponse` with renewable energy context

#### 🛠️ Mathematical Tools
- `add_tool(a, b)` - Addition with renewable energy context
- `subtract_tool(a, b)` - Subtraction with energy loss scenarios  
- `multiply_tool(a, b)` - Multiplication for capacity calculations
- `divide_tool(a, b)` - Division for efficiency metrics

#### 📊 API Endpoints
- `GET /api/health` - Health check
- `POST /api/chat` - Chat with agent
- `POST /api/register` - User registration
- `GET /api/conversation/{user_id}` - Conversation history
- `POST /api/user/preferences` - Set user preferences

## 🧪 Testing

### Automated Tests
```bash
# Run all tests
python run_tests.py

# Run specific test files
pytest tests/test_agent.py -v
pytest tests/test_api.py -v
```

### Test Coverage
- ✅ Mathematical operation tools
- ✅ Agent response validation
- ✅ API endpoint functionality
- ✅ User registration and preferences
- ✅ Error handling and edge cases
- ✅ Integration testing

## 🌱 Agent Capabilities

### Mathematical Operations
The agent can perform basic arithmetic with renewable energy context:

**Example Interactions:**
- "What is 25 + 15?" → "40 MW total capacity from combining two solar farms"
- "Calculate 100 - 20" → "80 MW net output after accounting for system losses"  
- "Multiply 10 by 5" → "50 MWh total generation from 10 turbines producing 5 MWh each"
- "Divide 200 by 8" → "25 MW per turbine average capacity"

### User Management
- User registration with name and email
- Conversation history tracking
- User preference storage
- Engagement analytics

### Renewable Energy Context
The agent provides relevant renewable energy context for all calculations:
- Solar panel capacity calculations
- Wind farm output modeling
- Energy storage capacity planning
- Power grid efficiency analysis

## 🎯 Response Format

All agent responses follow the structured `MathResponse` format:

```json
{
  "result": 40.0,
  "operation": "addition", 
  "explanation": "Added 15 and 25 to get 40",
  "renewable_context": "This could represent combining 15 MW and 25 MW of solar capacity for a total of 40 MW",
  "units": "MW",
  "confidence": 1.0,
  "sources": ["calculation"],
  "timestamp": "2024-01-15T10:30:00"
}
```

## 📈 Development Phases

### ✅ Phase 1: Core Infrastructure (Completed)
- Project restructure and dependencies
- PydanticAI agent with math tools
- FastAPI server with endpoints
- Comprehensive test suite

### 🔄 Phase 2: Frontend Development (Next)
- React application with Vite
- shadcn/ui component setup  
- Chat interface components
- Zustand state management

### 🔮 Phase 3: Advanced Features (Future)
- Supabase database integration
- Dropbox document ingestion
- RAG capabilities
- Logfire observability

## 🐛 Troubleshooting

### Common Issues

**Import Errors:**
```bash
# Ensure you're in the backend directory
cd backend
python -c "from agent.renewable_agent import RenewableEnergyAgent"
```

**API Connection Issues:**
```bash
# Check if server is running
curl http://localhost:8000/api/health
```

**Test Failures:**
```bash
# Check test logs
cat logs/test_results.log
```

### Environment Variables Required
```bash
OPENAI_API_KEY=your_openai_api_key_here
# Optional (for future features):
SUPABASE_URL=your_supabase_project_url
SUPABASE_SERVICE_KEY=your_supabase_service_key
```

## 📝 API Documentation

Once the server is running, visit:
- **Interactive Docs:** http://localhost:8000/docs
- **ReDoc:** http://localhost:8000/redoc

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Run tests (`python run_tests.py`)
4. Commit changes (`git commit -m 'Add amazing feature'`)
5. Push to branch (`git push origin feature/amazing-feature`)
6. Open a Pull Request

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 🙏 Acknowledgments

- **PydanticAI** - For the agent framework
- **FastAPI** - For the web framework
- **OpenAI** - For the language model
- **Pydantic** - For data validation
- **pytest** - For testing framework 