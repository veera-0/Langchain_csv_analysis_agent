## AI-CSV-Agent

A small MCP-based example that exposes CSV analysis tools via a simple MCP server and a LangChain-based client agent that can call those tools over stdio.

This repository demonstrates a minimal workflow where:
- `mcp_server/csv_server.py` exposes data-analysis tools (Pandas operations) through an MCP server.
- `mcp_client/agent.py` runs a LangChain agent that connects to the MCP server over stdio, loads the tools, and uses an Azure-backed chat model to answer questions about the CSV dataset.

## Repository layout

- `mcp_server/`
  - `csv_server.py` — MCP server exposing tools for the CSV (uses `pandas`).
  - `titanic.csv` — example dataset used by the server.
- `mcp_client/`
  - `agent.py` — LangChain-based client that starts or connects to the MCP stdio server and runs queries.

## Prerequisites

- Python 3.10 or newer (3.11 recommended).
- Basic familiarity with virtual environments and PowerShell on Windows.
- An Azure OpenAI deployment (if you intend to use `AzureChatOpenAI`) or configure whichever LLM backend you prefer.

## Recommended Python packages

The code imports a set of libraries that should be available in your environment. Create a `requirements.txt` with the pinned versions you prefer, or install these packages manually:

```
pandas
python-dotenv
langchain
langchain-core
langchain-openai
langchain-mcp-adapters
mcp
# plus any Azure/OpenAI runtime packages you need (example: azure-ai-openai or openai)
```

Note: Some packages (for example `langchain-mcp-adapters` and `mcp`) may be internal or custom; install them from your package source or replace with the appropriate package names you use.

## Create and activate a virtual environment (PowerShell)

Open PowerShell in the project root `E:\git\AI-CSV-Agent` and run:

```powershell
# create venv
python -m venv .venv

# On first use you may need to relax execution policy for the current user (only if activation fails):
# Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser

# activate
.\.venv\Scripts\Activate.ps1

# upgrade pip
python -m pip install --upgrade pip
```

## Install dependencies

After activating the venv, either install from an existing `requirements.txt` or install packages manually:

```powershell
# if you have requirements.txt
pip install -r requirements.txt

# or install manually
pip install pandas python-dotenv langchain langchain-core
# then install your LLM adapter packages and MCP packages as needed
```

## Environment variables

Create a `.env` file in the project root (the client loads environment variables via `python-dotenv`). Example `.env`:

```
API_BASE=https://your-azure-endpoint
API_KEY=your_azure_openai_key
API_VERSION=2023-03-15-preview
DEPLOYMENT_NAME=gpt-4o
```

Adjust names and values to the provider you're using. `agent.py` reads the variables:
- `API_BASE`
- `API_KEY`
- `API_VERSION` (optional, defaults to `2023-03-15-preview`)
- `DEPLOYMENT_NAME` (optional)

## Run the MCP server (CSV tools)

Start the server in one terminal. From the repository root run:

```powershell
# run the MCP stdio server (server prints nothing to stdout/stderr for stdio transport)
python .\mcp_server\csv_server.py
```

The server exposes a set of tools for CSV inspection such as `tool_schema`, `tool_nulls`, `tool_describe`, `tool_head`, `tool_value_counts`.

## Run the LangChain client agent

In another terminal (with the venv activated), start the client which connects to the MCP server and queries the dataset:

```powershell
python .\mcp_client\agent.py
```

By default, `agent.py` runs an example query in `main()` — you can modify the `question` variable or adapt the client to accept CLI args.

## Known issue & recommended small fix

While analyzing the project, the client currently references the server script as `..\mcp_server\csv.server.py` and invokes the `python` command string. The actual server file in this repo is `csv_server.py` (underscore). On Windows this mismatch will cause the client to fail to spawn the server.

Recommended change in `mcp_client/agent.py` (small, safe):

```python
server_script_path = r"..\mcp_server\csv.server.py"
command="python"
```

If you prefer to start the server manually (recommended while developing), run `python mcp_server/csv_server.py` in its own terminal and the client will connect to a started server (depending on how stdio_client is used).

