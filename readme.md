# 🤖 Multi-AI Agent using Groq & Tavily

A multi-AI agent application powered by a **custom LangGraph StateGraph** agent with **Groq LLM** and **Tavily Search**. Built with **FastAPI** backend and **Streamlit** frontend, deployable on **GCP Cloud Run** via **Jenkins CI/CD**.

---

## 🌟 Features

- ✨ **Multi-Model Support** — Switch between Groq models (Qwen, Llama)
- 🔍 **Web Search Integration** — Tavily Search for real-time information retrieval
- 🏗️ **Agent Architecture** — Custom LangGraph `StateGraph` with nodes, edges & conditional routing
- 🌊 **Real-time Streaming** — Token-by-token response display
- 📜 **Auto-scroll** — Smooth auto-scrolling during response generation
- ⚡ **FastAPI Backend** — REST API on port 9999
- 🎨 **Streamlit Frontend** — Interactive UI on port 8501
- 🐳 **Docker Ready** — Multi-stage optimized builds
- ☁️ **GCP Cloud Run** — Cloud deployment
- 🔌 **CI/CD** — Jenkins + SonarQube

---

## 🔄 Workflow

### Application Flow

```mermaid
flowchart TD
    A[👤 User] -->|Query + Model| B[🎨 Streamlit UI\nPort 8501]
    B -->|POST /chat| C[⚡ FastAPI\nPort 9999]
    C -->|Build & Compile| D[🔧 StateGraph]

    subgraph LangGraph Agent
        D --> E["🧠 llm_node\ninit_chat_model + bind_tools"]
        E --> F{should_continue?}
        F -->|tool_calls exist| G["🔍 tool_node\nTavily Search"]
        G -->|results| E
        F -->|no tool_calls| H[END]
    end

    H -->|AI Response| C
    C -->|JSON| B
    B -->|Display| A

    style A fill:#4CAF50,color:#fff
    style B fill:#FF9800,color:#fff
    style C fill:#2196F3,color:#fff
    style D fill:#9C27B0,color:#fff
    style E fill:#F44336,color:#fff
    style F fill:#FF5722,color:#fff
    style G fill:#00BCD4,color:#fff
    style H fill:#607D8B,color:#fff
```

### CI/CD Pipeline

```mermaid
flowchart LR
    A[📝 Git Push] -->|Webhook| B[🔧 Jenkins]
    B --> C[📊 SonarQube\nCode Analysis]
    C --> D[🐳 Docker Build\nMulti-stage]
    D --> E[📦 GCP Artifact\nRegistry]
    E --> F[☁️ Cloud Run\nDeploy]
    F --> G[🌐 Live App]

    style A fill:#333,color:#fff
    style B fill:#D24939,color:#fff
    style C fill:#4E9BCD,color:#fff
    style D fill:#2496ED,color:#fff
    style E fill:#4285F4,color:#fff
    style F fill:#34A853,color:#fff
    style G fill:#4CAF50,color:#fff
```

---

## 🚀 Quick Start

### Prerequisites

- Python 3.12+
- [Groq API Key](https://console.groq.com) & [Tavily API Key](https://tavily.com)

### Setup & Run

```bash
git clone https://github.com/farhanrhine/multi-ai-agent-gcp.git
cd multi-ai-agent-gcp

cp .env.example .env   # Add your API keys

uv sync                # Install dependencies
uv run main.py         # Start app
```

- 🎨 **UI**: <http://localhost:8501>
- ⚙️ **API Docs**: <http://localhost:9999/docs>

---

## 💡 Example Prompts

Here are some examples to get started. Set the **System Prompt** to define the agent's role, then ask your **Query**.

### 🔬 Research Assistant (with Web Search ✅)

> **System Prompt:** `You are a research assistant who provides well-sourced, factual answers.`
>
> **Query:** `What are the latest breakthroughs in quantum computing in 2025?`

### 💻 Code Helper

> **System Prompt:** `You are a senior Python developer. Explain concepts clearly with code examples.`
>
> **Query:** `How do I implement a retry mechanism with exponential backoff in Python?`

### 🩺 Medical Info (with Web Search ✅)

> **System Prompt:** `You are a medical information assistant. Always recommend consulting a doctor.`
>
> **Query:** `What are the early symptoms of Type 2 diabetes and how is it diagnosed?`

### 📊 Data Analyst

> **System Prompt:** `You are a data analyst. Explain things with examples and suggest tools.`
>
> **Query:** `How should I clean and preprocess a dataset with missing values and outliers?`

### ✍️ Content Writer

> **System Prompt:** `You are a professional content writer. Write in a clear, engaging tone.`
>
> **Query:** `Write a LinkedIn post about how AI agents are changing software development.`

### 🌍 Travel Planner (with Web Search ✅)

> **System Prompt:** `You are a travel planning expert. Give detailed itineraries with costs.`
>
> **Query:** `Plan a 5-day budget trip to Tokyo, Japan for a solo traveler.`

> **💡 Tip:** Enable **Web Search** when you need real-time or up-to-date information. Disable it for general knowledge questions to get faster responses.

---

## 🐳 Docker

```bash
# Build & run
docker build -t multi-ai-agent:latest .
docker run -it -p 8501:8501 -p 9999:9999 \
  -e GROQ_API_KEY=your_key -e TAVILY_API_KEY=your_key \
  multi-ai-agent:latest

# Or use Docker Compose (App + Jenkins + SonarQube)
docker-compose up -d
```

---

## 📚 API

### `GET /` — Health Check

```json
// Response
{ "status": "running", "service": "Multi AI Agent API" }
```

### `POST /chat` — Chat with Agent

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
  "response": "The weather today in..."
}
```

### `POST /chat/stream` — Streaming Chat

Same request body as `/chat`. Returns `text/plain` streamed response (token by token).

**Supported Models:** `qwen/qwen3-32b` · `llama-3.3-70b-versatile`

---

## ☁️ GCP Cloud Run Deployment

```bash
gcloud auth login
gcloud config set project YOUR_PROJECT_ID

# Create repo & configure Docker
gcloud artifacts repositories create multi-ai-agent --repository-format=docker --location=us-central1
gcloud auth configure-docker us-central1-docker.pkg.dev

# Build, push & deploy
docker build -t multi-ai-agent:latest .
docker tag multi-ai-agent:latest us-central1-docker.pkg.dev/YOUR_PROJECT_ID/multi-ai-agent/multi-ai-agent:latest
docker push us-central1-docker.pkg.dev/YOUR_PROJECT_ID/multi-ai-agent/multi-ai-agent:latest

gcloud run deploy multi-ai-agent-service \
  --image us-central1-docker.pkg.dev/YOUR_PROJECT_ID/multi-ai-agent/multi-ai-agent:latest \
  --region us-central1 --allow-unauthenticated --port 8501 \
  --memory 2Gi --cpu 2 \
  --set-env-vars GROQ_API_KEY=xxx,TAVILY_API_KEY=xxx
```

Or use the included `Jenkinsfile` for automated CI/CD deployment.

---

## 📂 Project Structure

```
multi-ai-agent-gcp/
├── app/
│   ├── backend/api.py          # FastAPI REST API
│   ├── frontend/ui.py          # Streamlit UI
│   ├── core/ai_agent.py        # Custom LangGraph StateGraph agent
│   ├── config/settings.py      # Environment & model config
│   └── common/                 # Logger & custom exceptions
├── custom_jenkins/Dockerfile   # Jenkins image with GCP SDK
├── Dockerfile                  # Multi-stage production build
├── docker-compose.yml          # Local dev stack
├── Jenkinsfile                 # CI/CD pipeline
├── main.py                     # Entry point
├── pyproject.toml              # Dependencies
└── .env.example                # Environment template
```

---

**Built by Farhan with ❤️ using Groq, Tavily, LangChain, LangGraph, FastAPI, and Streamlit**
