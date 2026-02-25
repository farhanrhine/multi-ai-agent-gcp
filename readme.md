# 🤖 Multi-AI Agent using Groq & Tavily

A production-ready multi-AI agent application that combines **Groq LLM**, **Tavily Search**, and **LangGraph** for intelligent task execution. Built with **FastAPI** backend and **Streamlit** frontend, deployable on **AWS ECS** or **GCP Cloud Run**.

---

## 🌟 Features

✨ **Multi-Model Support** - Switch between various Groq models (Qwen, Llama, Mixtral, Gemma)
🔍 **Web Search Integration** - Tavily Search for real-time information retrieval
🏗️ **Agent Architecture** - LangGraph-based multi-agent system
⚡ **FastAPI Backend** - High-performance REST API
🎨 **Streamlit Frontend** - Interactive user interface
🐳 **Docker Ready** - Multi-stage optimized Docker builds
☁️ **Cloud Deployment** - AWS ECS, GCP Cloud Run, and AWS/GCP Kubernetes support
🔌 **CI/CD Pipeline** - Jenkins automation with SonarQube integration

---

## 📋 Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                     User Interface                           │
│              (Streamlit Frontend - Port 8501)               │
└────────────────────┬────────────────────────────────────────┘
                     │ HTTP Requests
                     ▼
┌─────────────────────────────────────────────────────────────┐
│                   FastAPI Backend                            │
│         (REST API - Port 9999 /chat endpoint)               │
└────────────┬──────────────────────────┬──────────────────────┘
             │                          │
             ▼                          ▼
      ┌─────────────┐          ┌──────────────┐
      │  Groq LLM   │          │ Tavily Search│
      │  Models     │          │  Integration │
      └─────────────┘          └──────────────┘
             ▲                          ▲
             └──────────┬───────────────┘
                        │
                ┌───────▼────────┐
                │  LangGraph     │
                │  Multi-Agent   │
                └────────────────┘
```

---

## 🚀 Quick Start

### Prerequisites

- Python 3.12+
- uv package manager (or pip)
- Docker & Docker Compose (for containerized deployment)
- Groq API Key ([Get one here](https://console.groq.com))
- Tavily API Key ([Get one here](https://tavily.com))

### Installation

#### 1. Clone Repository

```bash
git clone https://github.com/farhanrhine/multi-ai-agent-gcp.git
cd multi-ai-agent-gcp
```

#### 2. Setup Environment

```bash
# Copy environment template
cp .env.example .env

# Edit .env with your API keys
nano .env  # or use your preferred editor
```

**Required environment variables:**
```env
GROQ_API_KEY=gsk_your_groq_api_key_here
TAVILY_API_KEY=tvly-dev_your_tavily_api_key_here
```

#### 3. Install Dependencies

**Using uv (recommended):**
```bash
uv sync
```

**Using pip:**
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -e .
```

#### 4. Run Application

```bash
python main.py
```

Access the application:
- 🎨 **Streamlit UI**: http://localhost:8501
- ⚙️ **FastAPI Docs**: http://localhost:9999/docs
- 🔌 **API Endpoint**: http://localhost:9999/chat

---

## 🐳 Docker Deployment

### Build Docker Image

```bash
docker build -t multi-ai-agent:latest .
```

### Run with Docker

```bash
docker run -it \
  -p 8501:8501 \
  -p 9999:9999 \
  -e GROQ_API_KEY=your_key_here \
  -e TAVILY_API_KEY=your_key_here \
  multi-ai-agent:latest
```

### Using Docker Compose (Local Development)

```bash
# Start all services
docker-compose up -d

# View logs
docker-compose logs -f app

# Stop services
docker-compose down
```

This starts:
- 🎨 **App** (Streamlit + FastAPI): http://localhost:8501
- 🔧 **Jenkins** (CI/CD): http://localhost:8080
- 📊 **SonarQube** (Code Quality): http://localhost:9000

---

## 📚 API Usage

### Chat Endpoint

**POST** `/chat`

Request:
```json
{
  "model_name": "llama-3.3-70b-versatile",
  "system_prompt": "You are a helpful assistant",
  "messages": ["What is the weather today?"],
  "allow_search": true
}
```

Response:
```json
{
  "response": "..."
}
```

### Supported Models

- `qwen/qwen3-32b`
- `qwen/qwen3-72b`
- `llama-3.3-70b-versatile`
- `mixtral-8x7b-32768`
- `gemma2-9b-it`

---

## ☁️ Cloud Deployment

### AWS ECS Fargate

Refer to [FULL_DOCUMENTATION.md](FULL_DOCUMENTATION.md#step-5--final-deployment-stage-with-cloud-provider-and-jenkins) for:
1. Create ECR repository and ECS cluster
2. Configure Jenkins pipeline
3. Deploy to ECS Fargate
4. Set environment variables

### GCP Cloud Run

Refer to [FULL_DOCUMENTATION.md](FULL_DOCUMENTATION.md#option-b-gcp-cloud-run-deployment) for:
1. Create Artifact Registry and Cloud Run service
2. Configure Google Cloud SDK
3. Deploy via Jenkins
4. Manage environment variables

### GCP GKE

For advanced Kubernetes deployments, see Kubernetes manifests in documentation.

---

## 🔄 CI/CD Pipeline

### Jenkins Setup

The project includes automated CI/CD with Jenkins:

1. **GitHub Integration** - Automatic builds on push
2. **Code Quality** - SonarQube analysis
3. **Docker Build** - Multi-stage optimized builds
4. **Registry Push** - AWS ECR or GCP Artifact Registry
5. **Cloud Deploy** - Automatic deployment to ECS or Cloud Run

**Setup instructions**: See [JENKINS_SETUP.md](JENKINS_SETUP.md)

---

## 📖 Documentation

- 📘 **[FULL_DOCUMENTATION.md](FULL_DOCUMENTATION.md)** - Complete AWS/GCP deployment guide
- 🐳 **[DOCKER_SETUP.md](DOCKER_SETUP.md)** - Docker and Docker Compose configuration
- 🔧 **[JENKINS_SETUP.md](JENKINS_SETUP.md)** - Jenkins credentials and CI/CD setup
- ✅ **[DEPLOYMENT_READINESS.md](DEPLOYMENT_READINESS.md)** - Pre-deployment checklist

---

## 📂 Project Structure

```
multi-ai-agent-gcp/
├── app/
│   ├── backend/           # FastAPI server
│   │   ├── api.py
│   │   └── __init__.py
│   ├── frontend/          # Streamlit UI
│   │   ├── ui.py
│   │   └── __init__.py
│   ├── common/            # Utilities
│   │   ├── logger.py
│   │   ├── custom_exception.py
│   │   └── __init__.py
│   ├── config/            # Configuration
│   │   ├── settings.py
│   │   └── __init__.py
│   ├── core/              # AI agent logic
│   │   ├── ai_agent.py
│   │   └── __init__.py
│   ├── main.py
│   └── __init__.py
├── custom_jenkins/        # Jenkins Docker image
│   └── Dockerfile
├── logs/                  # Application logs
├── Dockerfile             # Multi-stage production build
├── docker-compose.yml     # Local development
├── Jenkinsfile            # CI/CD pipeline
├── pyproject.toml         # Dependencies
├── uv.lock                # Locked dependencies
├── main.py                # Entry point
├── .env.example           # Environment template
├── .dockerignore
├── .gitignore
└── README.md              # This file
```

---

## 🔐 Security Best Practices

✅ **Never commit `.env`** - Use `.env.example` as template
✅ **Use environment variables** - For all sensitive configuration
✅ **Rotate API keys regularly** - Groq and Tavily tokens
✅ **Use VPC/Security Groups** - When deploying to cloud
✅ **Enable HTTPS** - For production deployments
✅ **Monitor logs** - For suspicious activity

---

## 🧪 Testing

### Local Testing

```bash
# Test with uv
uv run python main.py

# Test with Docker
docker run -e GROQ_API_KEY=xxx -e TAVILY_API_KEY=xxx multi-ai-agent:latest

# Test with Docker Compose
docker-compose up -d
curl http://localhost:9999/docs
```

### Code Quality

SonarQube analysis is automatically run in Jenkins pipeline. View results at:
```
http://localhost:9000/projects
```

---

## 🐛 Troubleshooting

### API Keys Not Found

**Error:** `ValueError: GROQ_API_KEY not set in environment variables`

**Solution:**
```bash
# Ensure .env file exists and has API keys
cat .env

# Or set as shell environment variable
export GROQ_API_KEY=your_key_here
export TAVILY_API_KEY=your_key_here
```

### Port Already in Use

**Error:** `Address already in use: ('0.0.0.0', 8501)`

**Solution:**
```bash
# Find process using port
lsof -i :8501

# Kill process
kill -9 <PID>

# Or use different port
streamlit run app/frontend/ui.py --server.port 8502
```

### Docker Build Fails

**Error:** `ERROR: cannot find module`

**Solution:**
```bash
# Rebuild without cache
docker build --no-cache -t multi-ai-agent:latest .

# Check dependencies
uv sync
```

### Connection Refused

**Error:** `Connection refused: http://localhost:9999`

**Solution:**
```bash
# Ensure backend is running
# Check if service is on correct host/port
# In Docker: use service name instead of localhost
API_URL = "http://app:9999/chat"  # Instead of http://localhost:9999
```

---

## 📊 Performance Optimization

- **Multi-stage Docker build** - Reduced image size by ~70%
- **uv package manager** - 45x faster dependency resolution
- **Connection pooling** - Reuse database/API connections
- **Async operations** - FastAPI asynchronous request handling
- **Caching** - Frontend state management in Streamlit

---

## 🔄 Development Workflow

1. **Development**: `python main.py` (local development)
2. **Testing**: `docker-compose up` (test with Docker)
3. **Build**: `docker build -t multi-ai-agent:latest .` (create image)
4. **Push**: `docker push <registry>/multi-ai-agent:latest` (to registry)
5. **Deploy**: Jenkins pipeline automatically handles deployment

---

## 📝 Contributing

Contributions are welcome! Please:

1. Fork the repository
2. Create feature branch: `git checkout -b feature/AmazingFeature`
3. Commit changes: `git commit -m 'Add AmazingFeature'`
4. Push to branch: `git push origin feature/AmazingFeature`
5. Open Pull Request

---

## 📄 License

This project is open source and available under the MIT License.

---

## 📞 Support & Contact

For questions or issues:

1. Check [DEPLOYMENT_READINESS.md](DEPLOYMENT_READINESS.md) for common issues
2. Review logs: `docker-compose logs -f app`
3. Check SonarQube for code quality: http://localhost:9000
4. Reference [FULL_DOCUMENTATION.md](FULL_DOCUMENTATION.md) for detailed setup

---

## 🎯 Roadmap

- [ ] Add WebSocket support for real-time streaming
- [ ] Implement multi-turn conversations storage
- [ ] Add Redis caching layer
- [ ] Kubernetes manifests for advanced deployments
- [ ] Add authentication/authorization
- [ ] Performance monitoring dashboard
- [ ] Custom agent creation interface

---

**Built with ❤️ using Groq, Tavily, LangGraph, FastAPI, and Streamlit**

**Repository**: [github.com/farhanrhine/multi-ai-agent-gcp](https://github.com/farhanrhine/multi-ai-agent-gcp)
