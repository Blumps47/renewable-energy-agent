# Renewable Energy AI Agent Ecosystem

A comprehensive AI-powered platform designed to assist with renewable energy development tasks, from project planning to implementation and optimization.

## 🌟 Overview

This project implements an intelligent agent ecosystem using Pydantic AI, Supabase, and advanced RAG (Retrieval-Augmented Generation) capabilities to provide expert assistance in renewable energy development.

## 🏗️ Architecture

### Core Components
- **Single Agent (Phase 1)**: Domain expert for renewable energy
- **Agent Swarm (Phase 2)**: Specialized agents for different aspects
- **RAG System**: Document ingestion and contextual search
- **Meta Prompting**: Dynamic agent coordination

### Technology Stack
- **AI Framework**: Pydantic AI
- **Database**: Supabase (PostgreSQL + Vector Storage)
- **Document Source**: Dropbox API
- **Language**: Python 3.11+
- **Vector Database**: pgvector (via Supabase)

## 🚀 Quick Start

### Prerequisites
- Python 3.11+
- Supabase account and project
- Dropbox API access
- OpenAI API key (or other LLM provider)

### Installation

```bash
# Clone the repository
git clone <repository-url>
cd renewable-energy-ai-agents

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Set up environment variables
cp .env.example .env
# Edit .env with your API keys and configuration
```

### Configuration

Create a `.env` file with the following variables:

```env
SUPABASE_URL=your_supabase_url
SUPABASE_KEY=your_supabase_anon_key
SUPABASE_SERVICE_KEY=your_supabase_service_key
DROPBOX_ACCESS_TOKEN=your_dropbox_token
OPENAI_API_KEY=your_openai_key
```

## 📁 Project Structure

```
renewable-energy-ai-agents/
├── src/
│   ├── agents/                 # Agent implementations
│   ├── core/                   # Core utilities and base classes
│   ├── database/              # Database models and operations
│   ├── rag/                   # RAG system implementation
│   ├── integrations/          # External service integrations
│   └── meta_prompting/        # Meta prompting system
├── tests/                     # Test suite
├── docs/                      # Documentation
├── scripts/                   # Utility scripts
├── requirements.txt           # Python dependencies
├── .env.example              # Environment variables template
├── PRD.txt                   # Product Requirements Document
└── README.md                 # This file
```

## 🎯 Features

### Phase 1 (Current)
- [x] Core renewable energy agent
- [x] Supabase database integration
- [x] Basic document ingestion from Dropbox
- [x] Simple RAG implementation
- [x] Natural language query processing

### Phase 2 (Planned)
- [ ] Multi-agent architecture
- [ ] Specialized domain agents
- [ ] Advanced meta prompting
- [ ] Inter-agent communication
- [ ] Enhanced document processing

## 🔧 Development

### Running the Application

```bash
# Start the main agent
python src/main.py

# Run with specific configuration
python src/main.py --config config/development.yaml
```

### Testing

```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=src tests/

# Run specific test category
pytest tests/agents/
```

### Database Setup

```bash
# Initialize database schema
python scripts/init_database.py

# Seed with sample data
python scripts/seed_data.py
```

## 📚 Documentation

- [PRD.txt](PRD.txt) - Complete Product Requirements Document
- [Architecture Guide](docs/architecture.md) - Detailed system architecture
- [API Documentation](docs/api.md) - API reference
- [Development Guide](docs/development.md) - Setup and development workflow

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- Pydantic AI team for the excellent framework
- Supabase for the robust backend platform
- Renewable energy community for inspiration and domain expertise

## 📞 Support

For questions and support, please open an issue or contact the development team.

---

**Status**: 🚧 Under Active Development
**Version**: 0.1.0-alpha
**Last Updated**: 2024 