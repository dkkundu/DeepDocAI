# Local Ollama Document Summarizer

A FastAPI application that uses local Ollama to summarize documents (PDF, DOCX, DOC).

## Features

- 📄 Support for PDF, DOCX, and DOC files
- 🤖 Integration with local Ollama API
- 🚀 Fast and async document processing
- 📊 Health check and model listing endpoints
- 🔧 Configurable via environment variables

## Prerequisites

### Option 1: Docker (Recommended)
- **Docker** and **Docker Compose** installed
- No need to install Ollama or Python separately

### Option 2: Local Installation
1. **Ollama installed and running locally**
   - Download from: https://ollama.ai
   - Install and start the Ollama service
   - Pull a model (e.g., `ollama pull llama2`)

2. **Python 3.8+**

## Installation

### Docker Compose (Recommended)

1. Navigate to the project directory:
```bash
cd /mnt/backup/Local_LM
```

2. Start the services:
```bash
docker-compose up -d
```

3. Pull an Ollama model (first time only):
```bash
docker exec -it ollama ollama pull llama2
```

The API will be available at `http://localhost:8000`

**Useful commands:**
- View logs: `docker-compose logs -f`
- Stop services: `docker-compose down`
- Rebuild: `docker-compose up -d --build`
- Access Ollama shell: `docker exec -it ollama ollama list`

### Local Installation

1. Clone or navigate to this directory:
```bash
cd /mnt/backup/Local_LM
```

2. Create a virtual environment (recommended):
```bash
python3 -m venv venv
source venv/bin/activate  # On Linux/Mac
# or
venv\Scripts\activate  # On Windows
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

## Configuration

Set environment variables (optional):

```bash
export OLLAMA_BASE_URL="http://localhost:11434"  # Default
export OLLAMA_MODEL="llama2"  # Default model name
```

## Running the Application

### Docker Compose
If using Docker Compose, the application is already running after `docker-compose up -d`.

### Local Installation
Start the FastAPI server:

```bash
python main.py
```

Or using uvicorn directly:

```bash
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

The API will be available at `http://localhost:8000`

## API Endpoints

### GET `/`
Root endpoint with API information

### GET `/health`
Check API and Ollama connection status

### GET `/models`
List available Ollama models

### POST `/summarize`
Upload and summarize a document

**Parameters:**
- `file`: Document file (PDF, DOCX, or DOC)
- `model` (optional): Ollama model name (defaults to configured model)
- `max_length` (optional): Maximum summary length in words

**Quick Example (curl):**
```bash
curl -X POST "http://localhost:8000/summarize" \
  -F "file=@document.pdf" \
  -F "model=llama2" \
  -F "max_length=200"
```

**Quick Example (Python):**
```python
import requests

url = "http://localhost:8000/summarize"
files = {"file": open("document.pdf", "rb")}
data = {"model": "llama2", "max_length": 200}

response = requests.post(url, files=files, data=data)
print(response.json())
```

📖 **For more detailed examples** (cURL, Python, JavaScript, Node.js, Postman, etc.), see [API_EXAMPLES.md](API_EXAMPLES.md)

## API Documentation

Once the server is running, visit:
- Swagger UI: `http://localhost:8000/docs`
- ReDoc: `http://localhost:8000/redoc`

## Project Structure

```
Local_LM/
├── main.py              # FastAPI application
├── document_parser.py   # Document parsing logic
├── requirements.txt     # Python dependencies
├── Dockerfile          # Docker image definition
├── docker-compose.yml  # Docker Compose configuration
├── .dockerignore       # Docker ignore file
├── example_client.py   # Example Python client script
├── API_EXAMPLES.md     # Detailed API usage examples
├── README.md           # This file
└── uploads/            # Temporary upload directory (created automatically)
```

## Quick Test

Use the example client script to test the API:

```bash
python example_client.py document.pdf --model llama2 --max-length 200
```

## Troubleshooting

1. **Ollama connection errors:**
   - Ensure Ollama is running: `ollama list`
   - Check if Ollama is accessible at the configured URL
   - Verify the model exists: `ollama list`

2. **Document parsing errors:**
   - Ensure all dependencies are installed
   - Check that the file is not corrupted
   - Verify the file format is supported

3. **Import errors:**
   - Make sure virtual environment is activated
   - Reinstall dependencies: `pip install -r requirements.txt`

## Notes

- Uploaded files are automatically deleted after processing
- Large documents may be truncated to fit Ollama's context window
- Processing time depends on document size and Ollama model performance

