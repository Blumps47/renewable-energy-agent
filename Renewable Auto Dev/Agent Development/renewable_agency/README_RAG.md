# Renewable Energy RAG System 🌱⚡

A comprehensive Retrieval-Augmented Generation (RAG) system for renewable energy project analysis and due diligence. This system enables AI-powered conversations with your project documents, providing contextual insights and expert analysis.

## 🚀 Features

### Core RAG Capabilities
- **Document Intelligence**: Upload and process PDFs, DOCX, and text files
- **Contextual Search**: Vector similarity search with project-specific filtering
- **Multi-tenant Security**: Row-level security ensuring data isolation
- **Source Attribution**: Every response includes document citations and relevance scores
- **Cross-project Analysis**: Compare and analyze across multiple projects

### Document Sources
- **Dropbox Integration**: Sync documents from Dropbox folders
- **Google Drive Integration**: Sync documents from Google Drive folders  
- **Direct Upload**: Upload files directly through the web interface
- **Batch Processing**: Process multiple documents simultaneously

### AI Agent Features
- **Enhanced Chat**: Context-aware conversations with document knowledge
- **Project Insights**: AI-generated analysis and recommendations
- **Executive Summaries**: Automated project summaries for stakeholders
- **Risk Assessment**: Identify and analyze project risks from documents
- **Financial Analysis**: Extract and analyze financial data from documents

## 🏗️ Architecture

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   React Frontend │    │  FastAPI Backend │    │   Supabase DB   │
│                 │    │                 │    │                 │
│ • Document UI   │◄──►│ • RAG Engine    │◄──►│ • Vector Store  │
│ • Chat Interface│    │ • AI Agent      │    │ • Documents     │
│ • Project Mgmt  │    │ • API Routes    │    │ • Projects      │
└─────────────────┘    └─────────────────┘    └─────────────────┘
                                │
                                ▼
                       ┌─────────────────┐
                       │  External APIs  │
                       │                 │
                       │ • OpenAI        │
                       │ • Dropbox       │
                       │ • Google Drive  │
                       └─────────────────┘
```

## 📋 Prerequisites

- Python 3.9+
- Node.js 16+
- Supabase account
- OpenAI API key
- (Optional) Dropbox/Google Drive API credentials

## 🛠️ Installation

### 1. Backend Setup

```bash
# Navigate to backend directory
cd Agent\ Development/renewable_agency/backend

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Set up environment variables
cp .env.template .env
# Edit .env with your actual credentials
```

### 2. Database Setup

```bash
# In Supabase SQL Editor, run:
# Agent Development/renewable_agency/backend/database_schema.sql

# This creates:
# - Tables with RLS policies
# - Vector extension setup
# - Indexes for performance
# - Storage bucket configuration
```

### 3. Frontend Setup

```bash
# Navigate to frontend directory
cd Agent\ Development/renewable_agency/frontend

# Install dependencies
npm install

# Start development server
npm run dev
```

### 4. Start Backend Server

```bash
# In backend directory
cd Agent\ Development/renewable_agency/backend

# Start FastAPI server
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

## 🔧 Configuration

### Environment Variables

Create `.env` file in the backend directory:

```env
# Core AI Services
OPENAI_API_KEY=your-openai-api-key

# Database & Storage
SUPABASE_URL=your-supabase-url
SUPABASE_SERVICE_KEY=your-supabase-service-key

# Authentication
JWT_SECRET=your-jwt-secret

# Optional: External Services
DROPBOX_APP_KEY=your-dropbox-key
GOOGLE_DRIVE_CLIENT_ID=your-google-client-id
```

### Supabase Configuration

1. **Create Project**: Set up new Supabase project
2. **Enable Extensions**: Enable `vector` extension
3. **Run Schema**: Execute `database_schema.sql`
4. **Storage Bucket**: Create `documents` bucket
5. **RLS Policies**: Ensure Row Level Security is enabled

## 📚 API Documentation

### Core Endpoints

#### Project Management
- `POST /api/rag/projects` - Create project
- `GET /api/rag/projects` - List projects
- `GET /api/rag/projects/{id}` - Get project details
- `PUT /api/rag/projects/{id}` - Update project
- `DELETE /api/rag/projects/{id}` - Delete project

#### Document Management
- `POST /api/rag/documents/upload` - Upload document
- `POST /api/rag/documents/sync/dropbox` - Sync from Dropbox
- `POST /api/rag/documents/sync/google-drive` - Sync from Google Drive
- `GET /api/rag/documents` - List documents
- `DELETE /api/rag/documents/{id}` - Delete document

#### RAG Queries
- `POST /api/rag/query` - Query documents
- `POST /api/rag/chat/enhanced` - Enhanced chat with RAG
- `POST /api/rag/projects/insights` - Generate project insights
- `POST /api/rag/projects/summary` - Generate project summary

### Example Usage

#### Upload and Process Document

```python
import requests

# Upload document
files = {'file': open('project_report.pdf', 'rb')}
data = {'project_id': 'your-project-id'}
headers = {'Authorization': 'Bearer your-jwt-token'}

response = requests.post(
    'http://localhost:8000/api/rag/documents/upload',
    files=files,
    data=data,
    headers=headers
)
```

#### Query Documents

```python
query_data = {
    "query": "What are the main environmental risks?",
    "project_ids": ["project-id-1", "project-id-2"],
    "limit": 5,
    "similarity_threshold": 0.7
}

response = requests.post(
    'http://localhost:8000/api/rag/query',
    json=query_data,
    headers=headers
)
```

#### Enhanced Chat

```python
chat_data = {
    "message": "Analyze the financial viability of this solar project",
    "project_ids": ["project-id"],
    "use_rag": True,
    "conversation_history": [
        {"role": "user", "content": "Previous question"},
        {"role": "assistant", "content": "Previous response"}
    ]
}

response = requests.post(
    'http://localhost:8000/api/rag/chat/enhanced',
    json=chat_data,
    headers=headers
)
```

## 🔒 Security Features

### Multi-tenant Architecture
- **Row Level Security (RLS)**: Database-level data isolation
- **JWT Authentication**: Secure API access
- **User-specific Data**: Each user only sees their own projects/documents

### Data Protection
- **Encrypted Storage**: Documents stored securely in Supabase
- **API Rate Limiting**: Prevents abuse and ensures fair usage
- **Input Validation**: Comprehensive request validation
- **Error Handling**: Secure error responses without data leakage

## 🧪 Testing

### Run Backend Tests

```bash
cd Agent\ Development/renewable_agency/backend
pytest tests/ -v
```

### Test Coverage

```bash
pytest --cov=. tests/
```

### Manual Testing

1. **Document Upload**: Test file upload and processing
2. **RAG Queries**: Verify search accuracy and relevance
3. **Multi-tenant**: Ensure user data isolation
4. **Error Handling**: Test edge cases and error scenarios

## 🚀 Deployment

### Production Environment

1. **Environment Variables**: Set production values
2. **Database**: Use production Supabase instance
3. **SSL/TLS**: Enable HTTPS
4. **Rate Limiting**: Configure appropriate limits
5. **Monitoring**: Set up logging and monitoring

### Docker Deployment

```dockerfile
# Dockerfile example
FROM python:3.9-slim

WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt

COPY . .
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
```

## 📊 Monitoring & Analytics

### Key Metrics
- **Document Processing**: Success rates, processing times
- **Query Performance**: Response times, accuracy scores
- **User Engagement**: Query frequency, project activity
- **System Health**: API response times, error rates

### Logging
- **Structured Logging**: JSON format for easy parsing
- **Error Tracking**: Comprehensive error logging
- **Performance Metrics**: Query times and resource usage
- **Audit Trail**: User actions and data access

## 🔧 Troubleshooting

### Common Issues

1. **Document Processing Fails**
   - Check file format compatibility
   - Verify OpenAI API key and credits
   - Review file size limits

2. **Vector Search Returns No Results**
   - Check similarity threshold settings
   - Verify embeddings were generated
   - Review query phrasing

3. **Authentication Errors**
   - Verify JWT token validity
   - Check Supabase RLS policies
   - Confirm user permissions

### Debug Mode

```bash
# Enable debug logging
export DEBUG=true
export LOG_LEVEL=DEBUG

# Run with verbose output
uvicorn main:app --reload --log-level debug
```

## 🤝 Contributing

1. Fork the repository
2. Create feature branch (`git checkout -b feature/amazing-feature`)
3. Commit changes (`git commit -m 'Add amazing feature'`)
4. Push to branch (`git push origin feature/amazing-feature`)
5. Open Pull Request

### Development Guidelines
- Follow PEP 8 style guide
- Add comprehensive tests
- Update documentation
- Use type hints
- Handle errors gracefully

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 🆘 Support

- **Documentation**: Check this README and API docs
- **Issues**: Create GitHub issue for bugs/features
- **Email**: Contact development team
- **Discord**: Join our community server

## 🎯 Roadmap

### Phase 1 (Current)
- ✅ Core RAG implementation
- ✅ Document processing pipeline
- ✅ Multi-tenant security
- ✅ Basic UI components

### Phase 2 (Next)
- 🔄 Advanced analytics dashboard
- 🔄 Real-time collaboration
- 🔄 Mobile app support
- 🔄 Advanced AI models

### Phase 3 (Future)
- 📋 Workflow automation
- 📋 Third-party integrations
- 📋 Advanced reporting
- 📋 Enterprise features

---

**Built with ❤️ for the renewable energy community** 