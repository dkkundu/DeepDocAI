from fastapi import FastAPI, File, UploadFile, HTTPException
from fastapi.responses import JSONResponse
import aiofiles
import os
from pathlib import Path
from typing import Optional
import httpx
import logging

from document_parser import DocumentParser

# Load environment variables from .env file if it exists
try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass  # python-dotenv is optional

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(title="Local Ollama Document Summarizer", version="1.0.0")

# Configuration
OLLAMA_BASE_URL = os.getenv("OLLAMA_BASE_URL", "http://localhost:11434")
OLLAMA_MODEL = os.getenv("OLLAMA_MODEL", "deepseek-r1")
UPLOAD_DIR = Path("uploads")
UPLOAD_DIR.mkdir(exist_ok=True)

# Initialize document parser
parser = DocumentParser()


@app.get("/")
async def root():
    return {
        "message": "Local Ollama Document Summarizer API",
        "endpoints": {
            "health": "/health",
            "summarize": "/summarize",
            "models": "/models"
        }
    }


@app.get("/health")
async def health():
    """Check API and Ollama connection health"""
    try:
        async with httpx.AsyncClient(timeout=5.0) as client:
            response = await client.get(f"{OLLAMA_BASE_URL}/api/tags")
            ollama_status = response.status_code == 200
    except Exception as e:
        logger.error(f"Ollama connection error: {e}")
        ollama_status = False
    
    return {
        "status": "healthy" if ollama_status else "degraded",
        "ollama_connected": ollama_status,
        "ollama_url": OLLAMA_BASE_URL
    }


@app.get("/models")
async def list_models():
    """List available Ollama models"""
    try:
        async with httpx.AsyncClient(timeout=10.0) as client:
            response = await client.get(f"{OLLAMA_BASE_URL}/api/tags")
            if response.status_code == 200:
                models = response.json().get("models", [])
                return {
                    "models": [model.get("name", "") for model in models],
                    "current_model": OLLAMA_MODEL
                }
            else:
                raise HTTPException(status_code=500, detail="Failed to fetch models")
    except httpx.RequestError as e:
        raise HTTPException(status_code=503, detail=f"Cannot connect to Ollama: {str(e)}")


@app.post("/summarize")
async def summarize_document(
    file: UploadFile = File(...),
    model: Optional[str] = None,
    max_length: Optional[int] = None
):
    """
    Upload a document and get its summary using Ollama.
    
    Supported formats: PDF, DOCX, DOC
    
    Parameters:
    - file: The document file to summarize
    - model: Optional Ollama model name (defaults to OLLAMA_MODEL env var or 'llama2')
    - max_length: Optional maximum summary length in words (use -1, 0, or omit for unlimited)
    """
    # Validate file type
    file_ext = Path(file.filename).suffix.lower()
    if file_ext not in ['.pdf', '.docx', '.doc']:
        raise HTTPException(
            status_code=400,
            detail=f"Unsupported file type: {file_ext}. Supported types: .pdf, .docx, .doc"
        )
    
    # Use provided model or default
    model_name = model or OLLAMA_MODEL
    
    # Save uploaded file temporarily
    file_path = UPLOAD_DIR / file.filename
    try:
        async with aiofiles.open(file_path, 'wb') as f:
            content = await file.read()
            await f.write(content)
        
        logger.info(f"Processing file: {file.filename}")
        
        # Parse document
        try:
            text_content = await parser.parse_document(file_path, file_ext)
            if not text_content or not text_content.strip():
                raise HTTPException(
                    status_code=400,
                    detail="Could not extract text from document. The file might be empty or corrupted."
                )
        except Exception as e:
            logger.error(f"Document parsing error: {e}")
            raise HTTPException(
                status_code=500,
                detail=f"Failed to parse document: {str(e)}"
            )
        
        # Normalize max_length: treat -1, 0, and None as unlimited
        normalized_max_length = None if (max_length is None or max_length <= 0) else max_length
        
        # Generate summary using Ollama
        try:
            summary = await generate_summary(text_content, model_name, normalized_max_length)
        except Exception as e:
            logger.error(f"Summary generation error: {e}")
            raise HTTPException(
                status_code=500,
                detail=f"Failed to generate summary: {str(e)}"
            )
        
        return JSONResponse(content={
            "filename": file.filename,
            "file_type": file_ext,
            "model": model_name,
            "original_length": len(text_content),
            "summary": summary,
            "summary_length": len(summary)
        })
    
    finally:
        # Clean up uploaded file
        if file_path.exists():
            file_path.unlink()
            logger.info(f"Cleaned up file: {file_path}")


async def generate_summary(text: str, model: str, max_length: Optional[int] = None) -> str:
    """Generate summary using Ollama API"""
    
    # Truncate text if too long (Ollama has context limits)
    max_chars = 8000  # Conservative limit
    if len(text) > max_chars:
        text = text[:max_chars] + "... [truncated]"
        logger.warning(f"Text truncated to {max_chars} characters")
    
    # Create prompt
    length_instruction = f" Keep the summary under {max_length} words." if max_length else ""
    prompt = f"""Please provide a concise summary of the following document.{length_instruction}

Document:
{text}

Summary:"""
    
    # Call Ollama API
    async with httpx.AsyncClient(timeout=120.0) as client:
        response = await client.post(
            f"{OLLAMA_BASE_URL}/api/generate",
            json={
                "model": model,
                "prompt": prompt,
                "stream": False
            }
        )
        
        if response.status_code != 200:
            error_msg = response.text
            logger.error(f"Ollama API error: {error_msg}")
            raise Exception(f"Ollama API returned status {response.status_code}: {error_msg}")
        
        result = response.json()
        summary = result.get("response", "").strip()
        
        if not summary:
            raise Exception("Empty response from Ollama")
        
        return summary


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)

