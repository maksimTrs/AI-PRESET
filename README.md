# AI-PRESET: Complete Local AI Stack

A Docker Compose setup for running a complete local AI stack with **n8n**, **Ollama (LLM)**, **PostgreSQL with pgvector**, and **Open WebUI**. Includes automatic function import for seamless n8n-Open WebUI integration.

## 🚀 Quick Start

### Prerequisites
- **Docker Desktop** (Windows/Mac) or **Docker Engine + Compose** (Linux)
- **For GPU**: NVIDIA drivers

### Setup

1. **Create environment file** (`.env`):
```bash
# PostgreSQL & pgAdmin
POSTGRES_USER=n8n_user
POSTGRES_PASSWORD=your_strong_password_here
POSTGRES_DB=n8n_database
PGADMIN_DEFAULT_EMAIL=admin@example.com
PGADMIN_DEFAULT_PASSWORD=your_pgadmin_password_here

# Open WebUI Admin (auto-created)
WEBUI_ADMIN_EMAIL=admin@example.com
WEBUI_ADMIN_USER=your_strong_password_here
WEBUI_ADMIN_PASS=your_strong_password_here

# n8n Security (generate with: openssl rand -hex 32)
N8N_ENCRYPTION_KEY=your_secure_random_32_byte_hex_string
N8N_USER_MANAGEMENT_JWT_SECRET=another_secure_random_32_byte_hex_string
```

2. **Create directories**:
```bash
mkdir -p ./n8n/backup ./shared
```

3. **Start the stack**:
```bash
# CPU only
docker compose --profile cpu up -d

# With NVIDIA GPU
docker compose --profile gpu-nvidia up -d
```

## 📋 Project Structure

```
AI-PRESET/
├── .env                                    # Environment variables
├── docker-compose.yml                     # Main configuration
├── open-webui-functions-for-import.json   # Auto-imported n8n function
├── n8n_pipe_function.py                   # Function source code
├── n8n/backup/                           # n8n workflows (auto-imported)
└── shared/                               # Shared files between services
```

## 🌐 Access Services

| Service | URL | Purpose |
|---------|-----|---------|
| **Open WebUI** | [localhost:3000](http://localhost:3000) | ChatGPT-like interface |
| **n8n** | [localhost:5678](http://localhost:5678) | Workflow automation |
| **pgAdmin** | [localhost:5050](http://localhost:5050) | Database management |
| **Ollama API** | localhost:11434 | LLM API endpoint |

## ⚙️ Configuration

### Open WebUI Setup
1. Login with admin credentials from `.env` file
2. **Configure Ollama**: Settings → Models → Add endpoint: `http://ollama:11434`
3. **Configure n8n Function**: Admin → Functions → Find imported function → Configure Valves:
   - **N8N Url**: `http://n8n:5678/webhook-test/[your-webhook-url]`
   - **N8N Bearer Token**: (if required)
   - **Input Field**: `chatInput`
   - **Response Field**: `output`

### n8n Setup
1. Create owner account
2. **Add Ollama credentials**:
   - **Chat Model**: Base URL `http://ollama:11434/v1`
   - **Embeddings**: Base URL `http://ollama:11434`, Model `nomic-embed-text`

### pgAdmin Setup
1. Login with credentials from `.env`
2. **Connect to PostgreSQL**:
   - Host: `postgres`, Port: `5432`
   - Username/Password: from `.env` file

## 🤖 Available Models

**Default Models** (automatically downloaded):
- `llama3.1:8b` - General chat
- `gemma3:12b-it-qat` - Instruction following
- `mistral-small3.1:24b` - Advanced reasoning
- `nomic-embed-text` - Text embeddings

**To customize models**: Edit `docker-compose.yml` → `x-init-ollama` section → `ollama pull` commands

## 🔗 n8n-Open WebUI Integration

### How It Works
1. User sends message in Open WebUI
2. n8n pipe function intercepts and forwards to n8n webhook
3. n8n processes via workflow and returns response
4. Response displayed in Open WebUI

### Function Features
- ✅ **Auto-imported** during startup
- ✅ **Real-time status** indicators
- ✅ **Session management** for chat context
- ✅ **Error handling** and reporting

### Use Cases
- **RAG Applications**: Document processing with vector search
- **Database Integration**: Dynamic data retrieval
- **Multi-API Orchestration**: Complex workflow automation
- **Custom AI Agents**: Specialized task automation

## 🛠️ Docker Compose Architecture

### Services
- **open-webui**: ChatGPT-like interface with auto-imported functions
- **n8n**: Workflow automation with auto-imported workflows
- **postgres**: PostgreSQL with pgvector extension
- **pgadmin**: Database management interface
- **ollama-cpu/gpu**: LLM inference engine
- **ollama-pull**: Automatic model downloader

### Key Features
- **Automatic Setup**: Functions and workflows imported on startup
- **Network Isolation**: Internal Docker networks for security
- **Volume Persistence**: Data survives container restarts
- **Profile Support**: CPU-only or GPU-accelerated execution

## 🔧 Troubleshooting

| Issue | Solution |
|-------|----------|
| **Port conflicts** | Edit `ports:` in `docker-compose.yml` |
| **Service failures** | Check logs: `docker compose logs [service-name]` |
| **GPU issues** | Verify NVIDIA drivers and container toolkit |
| **Model downloads** | Monitor: `docker compose logs -f ollama-pull-llama-[cpu/gpu]` |
| **Function not working** | Check n8n webhook URL in Open WebUI function settings |

## 🔒 Security Notes

- **Never commit** `.env` file with real credentials
- **Change default passwords** before production use
- **Local use only** - implement proper security for network exposure
- **Keep updated** - regularly update Docker images

---

**Need more details?** Check the original documentation or the [n8n integration article](https://www.pondhouse-data.com/blog/integrating-n8n-with-open-webui).
