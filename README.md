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
├── .env                   # Environment variables (create this file)
├── docker-compose.yml     # Docker Compose configuration
├── n8n/
│   └── backup/
│       ├── credentials/   # Place n8n credential backups here
│       └── workflows/     # Place n8n workflow backups here
└── shared/                # Shared files accessible to services
```

If the directories don't exist, create them with:

```bash
# On Linux/macOS/Git Bash
mkdir -p ./n8n/backup/credentials ./n8n/backup/workflows ./shared

# On Windows CMD/PowerShell
mkdir n8n\backup\credentials
mkdir n8n\backup\workflows
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
       - Base URL: `http://ollama:11434`
     - **Embeddings Credential**:
       - Name: `Local Ollama Embeddings`
       - Base URL: `http://ollama:11434`
       - Model: `mxbai-embed-large` (or your configured embedding model)

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
   - Select from available models (default: `qwen3:30b-a3b-q4_K_M`, `gemma3:12b-it-qat`)

Open WebUI provides a ChatGPT-like interface for interacting with your local LLMs.

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
- `qwen3:30b-a3b-q4_K_M` (chat model)
- `gemma3:12b-it-qat` (chat model)
- `mxbai-embed-large` (embedding model)
- `qwen2.5:14b-instruct-q4_K_M` (chat model)

Additional models available (commented out by default):
- `qwen2.5-coder:14b` (code-specialized model)
- `deepseek-coder-v2:16b` (code-specialized model)
- `starcoder2:7b` (code-specialized model)

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
