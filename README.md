# AI-PRESET: Local AI Stack Setup Guide

This repository contains a Docker Compose setup for running a complete local AI stack with n8n, Ollama (LLM), Qdrant (Vector DB), and user-friendly UI tools. This guide will help you get started with the setup, configuration, and usage of the various components.

## Table of Contents

- [Prerequisites](#prerequisites)
- [Getting Started](#getting-started)
  - [Environment Configuration](#environment-configuration)
  - [Directory Setup](#directory-setup)
  - [Starting the Stack](#starting-the-stack)
- [Accessing Services](#accessing-services)
- [Working with pgAdmin](#working-with-pgadmin)
- [Working with n8n](#working-with-n8n)
- [Using Open WebUI](#using-open-webui)
- [Working with Qdrant](#working-with-qdrant)
- [Customizing Ollama Models](#customizing-ollama-models)
- [Troubleshooting](#troubleshooting)
- [Security Considerations](#security-considerations)

## Prerequisites

Before you begin, ensure you have the following installed:

- **Docker and Docker Compose**:
  - **Windows/Mac**: Install [Docker Desktop](https://www.docker.com/products/docker-desktop/)
  - **Linux**: Install [Docker Engine](https://docs.docker.com/engine/install/) and [Docker Compose Plugin](https://docs.docker.com/compose/install/)

- **For GPU Usage**:
  - **Nvidia GPU**: Latest Nvidia drivers and [NVIDIA Container Toolkit](https://docs.nvidia.com/datacenter/cloud-native/container-toolkit/latest/install-guide.html)
  - **AMD GPU (Linux Only)**: AMD drivers with ROCm support

## Getting Started

### Environment Configuration

1. Create a `.env` file in the project root directory with the following content:

```
# PostgreSQL Credentials (used by n8n and postgres service)
POSTGRES_USER=n8n_user
POSTGRES_PASSWORD=your_strong_password_here
POSTGRES_DB=n8n_database

# pgAdmin Credentials
PGADMIN_DEFAULT_EMAIL=admin@example.com
PGADMIN_DEFAULT_PASSWORD=your_pgadmin_password_here

# n8n Security Keys (ensure these are very secure and random)
# Generate with e.g., openssl rand -hex 32
N8N_ENCRYPTION_KEY=your_secure_random_32_byte_hex_string
N8N_USER_MANAGEMENT_JWT_SECRET=another_secure_random_32_byte_hex_string
```

> **IMPORTANT**: Replace the placeholder values with strong, unique passwords and keys. You can generate secure random strings using `openssl rand -hex 32` or a password manager.

### Directory Setup

Ensure the following directory structure exists:

```
AI-PRESET/
├── .env                                     # Environment variables (create this file)
├── docker-compose.yml                       # Docker Compose configuration
├── n8n_pipe_function.py                    # Custom pipe function for Open WebUI integration
├── functions-export-1747750482065.json     # Function definition for Open WebUI
├── n8n/
│   └── backup/
│       └── AI_Agent_With_Knowledge_Base_Main.json  # RAG implementation workflow
└── shared/                                 # Shared files accessible to services
```

If the directories don't exist, create them with:

```bash
# On Linux/macOS/Git Bash
mkdir -p ./n8n/backup ./shared

# On Windows CMD/PowerShell
mkdir n8n\backup
mkdir shared
```

### Starting the Stack

Choose the appropriate command based on your hardware:

- **For CPU-only execution**:
  ```bash
  docker compose --profile cpu up -d
  ```

- **For Nvidia GPU execution**:
  ```bash
  docker compose --profile gpu-nvidia up -d
  ```

The first startup will:
1. Download all necessary container images
2. Pull the configured LLM and embedding models (this may take significant time)
3. Initialize the databases and services

To monitor the model download progress:
```bash
# For GPU profile
docker compose logs -f ollama-pull-llama-gpu

# For CPU profile
docker compose logs -f ollama-pull-llama-cpu
```

## Accessing Services

Once the stack is running, access the services at:

- **n8n**: [http://localhost:5678](http://localhost:5678)
  - Set up your owner account on first visit
  
- **Open WebUI**: [http://localhost:3000](http://localhost:3000)
  - Create a local account on first use
  - Configure to use Ollama models

- **Qdrant Dashboard**: [http://localhost:6333/dashboard](http://localhost:6333/dashboard)
  - Basic overview of vector collections

- **pgAdmin**: [http://localhost:5050](http://localhost:5050)
  - PostgreSQL database management interface
  - Login with credentials from your `.env` file

- **Ollama API**: http://localhost:11434
  - Used by n8n, Open WebUI, and other tools

## Working with pgAdmin

1. Navigate to [http://localhost:5050](http://localhost:5050)
2. Log in with the credentials set in your `.env` file:
   - Email: The value of `PGADMIN_DEFAULT_EMAIL`
   - Password: The value of `PGADMIN_DEFAULT_PASSWORD`
3. To connect to the PostgreSQL database:
   - Right-click on "Servers" in the left panel and select "Create" → "Server"
   - In the "General" tab, give it a name (e.g., "Local Postgres")
   - In the "Connection" tab, enter:
     - Host name/address: `postgres` (Docker service name)
     - Port: `5432`
     - Maintenance database: `postgres`
     - Username: The value of `POSTGRES_USER` from your `.env` file
     - Password: The value of `POSTGRES_PASSWORD` from your `.env` file
   - Click "Save"

pgAdmin provides a comprehensive interface for managing your PostgreSQL database, including:
- Viewing and editing database tables
- Running SQL queries
- Managing users and permissions
- Monitoring database performance

## Working with n8n

### First-time Setup

1. Navigate to [http://localhost:5678](http://localhost:5678)
2. Create your owner account
3. Set up Ollama credentials:
   - Go to "Credentials" → "Add Credential"
   - Search for "Ollama" and create:
     - **Chat Model Credential**:
       - Name: `Local Ollama Chat`
       - Base URL: `http://ollama:11434/v1`
     - **Embeddings Credential**:
       - Name: `Local Ollama Embeddings`
       - Base URL: `http://ollama:11434`
       - Model: `nomic-embed-text`

### Using Imported Workflows

If you've placed workflow files in `n8n/backup/workflows` before the first startup, they should be automatically imported. You can find them in the n8n workflows list.

### Creating RAG Applications

The stack includes all components needed for Retrieval-Augmented Generation (RAG):
1. Use n8n to process documents from the `shared` directory
2. Generate embeddings with Ollama's embedding model
3. Store vectors in Qdrant
4. Create workflows that retrieve relevant context and send to LLM

## Using Open WebUI

1. Navigate to [http://localhost:3000](http://localhost:3000)
2. Create a local account
3. Configure Ollama:
   - Go to Settings → Models
   - Add Ollama endpoint: `http://ollama:11434` (internal Docker network)
   - Select from available models (default: `llama3.1:8b`, `qwen3:30b-a3b-q4_K_M`, `gemma3:12b-it-qat`, `mistral-small3.1:24b`)

Open WebUI provides a ChatGPT-like interface for interacting with your local LLMs.

## Project Files

This repository includes several important files for setting up your AI environment:

- **docker-compose.yml**: Main configuration file for the Docker services
- **n8n_pipe_function.py**: Custom pipe function for Open WebUI and n8n integration
- **functions-export-1747750482065.json**: Exported function definition for Open WebUI
- **n8n/backup/AI_Agent_With_Knowledge_Base_Main.json**: n8n workflow for RAG implementation

## n8n Pipe Function for Open WebUI Integration

The `n8n_pipe_function.py` file implements a custom pipe function that enables bidirectional communication between Open WebUI and n8n workflows. This integration allows you to extend your AI chatbot capabilities with n8n's powerful workflow automation.

### Setting Up the Function in Open WebUI

1. Navigate to Open WebUI at [http://localhost:3000](http://localhost:3000)
2. Log in with your administrator account
3. Go to the Administrator section
4. Select the "Functions" tab
5. Click "Import Function"
6. Upload the `functions-export-1747750482065.json` file
7. After importing, edit the function to update the webhook URL
8. Change the URL to use `http://host.docker.internal:5678/webhook-test/[your webhook URL]` instead of the default localhost URL
   - Note: `host.docker.internal` is required for proper communication between Docker containers

### How the Integration Works

1. **Communication Flow**:
   - User sends a message in Open WebUI
   - The n8n pipe function intercepts the message
   - Function makes an HTTP request to the n8n webhook
   - n8n processes the message through its workflow
   - n8n returns a response to Open WebUI
   - Open WebUI displays the response to the user

### Key Configuration Settings

The pipe function uses a `Valves` class to manage configuration settings:

```python
class Valves(BaseModel):
    n8n_url: str = Field(
        default="https://n8n.[your domain].com/webhook/[your webhook URL]"
    )
    n8n_bearer_token: str = Field(default="...")
    input_field: str = Field(default="chatInput")
    response_field: str = Field(default="output")
    emit_interval: float = Field(
        default=2.0, description="Interval in seconds between status emissions"
    )
    enable_status_indicator: bool = Field(
        default=True, description="Enable or disable status indicator emissions"
    )
```

- **n8n_url**: The webhook URL of your n8n workflow
- **n8n_bearer_token**: Authentication token for the n8n API
- **input_field**: Field name used to pass user input to n8n
- **response_field**: Field name to extract the response from n8n
- **emit_interval**: How often to emit status updates during processing
- **enable_status_indicator**: Toggle status indicators in the UI

### Implementation Features

- **Asynchronous Communication**: Uses `aiohttp` for non-blocking API calls
- **Status Reporting**: Provides real-time feedback during processing
- **Error Handling**: Comprehensive error handling and reporting
- **Session Management**: Maintains chat context using session IDs

### Using the Pipe Function

1. Place the `n8n_pipe_function.py` file in your Open WebUI functions directory
2. Configure the n8n webhook URL and bearer token in the file
3. Create a corresponding webhook workflow in n8n that:
   - Accepts input from the `chatInput` field
   - Processes the request as needed
   - Returns a response in the `output` field

### Use Cases

- **Database-powered chatbots**: Connect to databases for dynamic data retrieval
- **Multi-API orchestration**: Integrate with multiple external services
- **Document processing**: Generate, analyze, or transform documents
- **Multi-model orchestration**: Use different AI models for specialized tasks

For more details, see the [original article](https://www.pondhouse-data.com/blog/integrating-n8n-with-open-webui).

## Working with Qdrant

Qdrant is a vector database for semantic similarity search, essential for RAG applications:

- **Dashboard**: [http://localhost:6333/dashboard](http://localhost:6333/dashboard)
- **API Endpoint**: http://localhost:6333

In n8n workflows, use the HTTP Request node to interact with Qdrant's REST API:
- Create collections
- Upload vectors
- Perform similarity searches

## Customizing Ollama Models

To change or add Ollama models:

1. Edit the `docker-compose.yml` file
2. Find the `x-init-ollama:` section with the `command:` that contains `ollama pull` commands
3. Modify the models listed after `ollama pull` (separated by semicolons)
4. Save and restart the stack:
   ```bash
   docker compose down
   docker compose --profile [cpu|gpu-nvidia] up -d
   ```
5. Update your n8n credentials and Open WebUI settings to use the new models

Default active models:
- `llama3.1:8b` (chat model)
- `qwen3:30b-a3b-q4_K_M` (chat model)
- `gemma3:12b-it-qat` (chat model)
- `mistral-small3.1:24b` (chat model)
- `nomic-embed-text` (embedding model)

Additional models available (commented out by default):
- `devstral:24b` (chat model)

## Troubleshooting

- **Port Conflicts**: If services fail to start due to port conflicts, edit the `ports:` section in `docker-compose.yml` to use different external ports
- **Service Failures**: Check logs with `docker compose logs [service-name]`
- **GPU Issues**: Verify drivers and toolkit setup, check Ollama logs
- **Model Download Errors**: Check internet connection and Ollama puller logs

## Security Considerations

- **Never commit** your `.env` file with real secrets to version control
- Use strong, unique passwords for all services
- The stack is designed for local use; implement proper security measures if exposing to a network
- Keep Docker and all components updated regularly

---

For more detailed information, refer to the `INFO.md` file in this repository.
