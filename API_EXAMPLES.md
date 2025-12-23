# Summarize API Examples

This document provides examples of how to use the `/summarize` endpoint in various formats.

## Endpoint

```
POST http://localhost:8000/summarize
```

## Parameters

- `file` (required): Document file (PDF, DOCX, or DOC)
- `model` (optional): Ollama model name (defaults to configured model)
- `max_length` (optional): Maximum summary length in words

## Examples

### 1. cURL

#### Basic request (PDF)
```bash
curl -X POST "http://localhost:8000/summarize" \
  -F "file=@document.pdf"
```

#### With model and max length
```bash
curl -X POST "http://localhost:8000/summarize" \
  -F "file=@document.pdf" \
  -F "model=llama2" \
  -F "max_length=200"
```

#### DOCX file
```bash
curl -X POST "http://localhost:8000/summarize" \
  -F "file=@report.docx" \
  -F "model=mistral" \
  -F "max_length=150"
```

#### DOC file
```bash
curl -X POST "http://localhost:8000/summarize" \
  -F "file=@old_document.doc"
```

### 2. Python (requests library)

#### Basic example
```python
import requests

url = "http://localhost:8000/summarize"

# Open file and send request
with open("document.pdf", "rb") as f:
    files = {"file": f}
    response = requests.post(url, files=files)

print(response.json())
```

#### With all parameters
```python
import requests

url = "http://localhost:8000/summarize"

files = {"file": open("document.pdf", "rb")}
data = {
    "model": "llama2",
    "max_length": 200
}

response = requests.post(url, files=files, data=data)
result = response.json()

print(f"Summary: {result['summary']}")
print(f"Model used: {result['model']}")
print(f"Summary length: {result['summary_length']} characters")
```

#### Error handling
```python
import requests

url = "http://localhost:8000/summarize"

try:
    with open("document.pdf", "rb") as f:
        files = {"file": f}
        data = {"model": "llama2", "max_length": 200}
        response = requests.post(url, files=files, data=data)
        response.raise_for_status()
        
        result = response.json()
        print(result["summary"])
        
except requests.exceptions.HTTPError as e:
    print(f"HTTP Error: {e}")
    print(f"Response: {e.response.json()}")
except FileNotFoundError:
    print("File not found")
except Exception as e:
    print(f"Error: {e}")
```

### 3. Python (httpx - async)

```python
import httpx
import asyncio

async def summarize_document(file_path: str, model: str = "llama2", max_length: int = None):
    url = "http://localhost:8000/summarize"
    
    async with httpx.AsyncClient(timeout=300.0) as client:
        with open(file_path, "rb") as f:
            files = {"file": f}
            data = {"model": model}
            if max_length:
                data["max_length"] = max_length
            
            response = await client.post(url, files=files, data=data)
            response.raise_for_status()
            return response.json()

# Usage
result = asyncio.run(summarize_document("document.pdf", max_length=200))
print(result["summary"])
```

### 4. JavaScript (fetch API)

#### Basic example
```javascript
const formData = new FormData();
const fileInput = document.querySelector('input[type="file"]');
formData.append('file', fileInput.files[0]);
formData.append('model', 'llama2');
formData.append('max_length', '200');

fetch('http://localhost:8000/summarize', {
    method: 'POST',
    body: formData
})
.then(response => response.json())
.then(data => {
    console.log('Summary:', data.summary);
    console.log('Model:', data.model);
})
.catch(error => console.error('Error:', error));
```

#### Async/await version
```javascript
async function summarizeDocument(file, model = 'llama2', maxLength = null) {
    const formData = new FormData();
    formData.append('file', file);
    formData.append('model', model);
    if (maxLength) {
        formData.append('max_length', maxLength.toString());
    }
    
    try {
        const response = await fetch('http://localhost:8000/summarize', {
            method: 'POST',
            body: formData
        });
        
        if (!response.ok) {
            const error = await response.json();
            throw new Error(error.detail || 'Request failed');
        }
        
        const result = await response.json();
        return result;
    } catch (error) {
        console.error('Error:', error);
        throw error;
    }
}

// Usage
const fileInput = document.querySelector('input[type="file"]');
const result = await summarizeDocument(fileInput.files[0], 'llama2', 200);
console.log(result.summary);
```

### 5. Node.js (form-data)

```javascript
const FormData = require('form-data');
const fs = require('fs');
const axios = require('axios');

async function summarizeDocument(filePath, model = 'llama2', maxLength = null) {
    const form = new FormData();
    form.append('file', fs.createReadStream(filePath));
    form.append('model', model);
    if (maxLength) {
        form.append('max_length', maxLength.toString());
    }
    
    try {
        const response = await axios.post(
            'http://localhost:8000/summarize',
            form,
            {
                headers: form.getHeaders(),
                timeout: 300000 // 5 minutes
            }
        );
        
        return response.data;
    } catch (error) {
        console.error('Error:', error.response?.data || error.message);
        throw error;
    }
}

// Usage
summarizeDocument('./document.pdf', 'llama2', 200)
    .then(result => console.log(result.summary))
    .catch(error => console.error('Failed:', error));
```

### 6. Postman

1. **Method**: POST
2. **URL**: `http://localhost:8000/summarize`
3. **Body**: Select `form-data`
4. **Add fields**:
   - `file`: (Type: File) - Select your document
   - `model`: (Type: Text) - e.g., `llama2`
   - `max_length`: (Type: Text) - e.g., `200`

### 7. HTTPie

```bash
# Install httpie if needed: pip install httpie

http --form POST http://localhost:8000/summarize \
  file@document.pdf \
  model=llama2 \
  max_length=200
```

## Response Format

### Success Response (200 OK)

```json
{
    "filename": "document.pdf",
    "file_type": ".pdf",
    "model": "llama2",
    "original_length": 15234,
    "summary": "This document discusses...",
    "summary_length": 456
}
```

### Error Response (400 Bad Request)

```json
{
    "detail": "Unsupported file type: .txt. Supported types: .pdf, .docx, .doc"
}
```

### Error Response (500 Internal Server Error)

```json
{
    "detail": "Failed to generate summary: Ollama API returned status 404: model not found"
}
```

## Testing with Different Models

```bash
# Using llama2
curl -X POST "http://localhost:8000/summarize" \
  -F "file=@document.pdf" \
  -F "model=llama2"

# Using mistral
curl -X POST "http://localhost:8000/summarize" \
  -F "file=@document.pdf" \
  -F "model=mistral"

# Using llama3
curl -X POST "http://localhost:8000/summarize" \
  -F "file=@document.pdf" \
  -F "model=llama3"
```

## Complete Python Script Example

```python
#!/usr/bin/env python3
"""
Example script to summarize a document using the API
"""

import requests
import sys
import argparse

def summarize_document(file_path, api_url="http://localhost:8000", model=None, max_length=None):
    """
    Summarize a document using the API
    
    Args:
        file_path: Path to the document file
        api_url: Base URL of the API
        model: Optional model name
        max_length: Optional maximum summary length
    """
    url = f"{api_url}/summarize"
    
    try:
        with open(file_path, "rb") as f:
            files = {"file": f}
            data = {}
            if model:
                data["model"] = model
            if max_length:
                data["max_length"] = max_length
            
            print(f"Uploading {file_path}...")
            response = requests.post(url, files=files, data=data, timeout=300)
            response.raise_for_status()
            
            result = response.json()
            
            print("\n" + "="*60)
            print("SUMMARY")
            print("="*60)
            print(f"File: {result['filename']}")
            print(f"Type: {result['file_type']}")
            print(f"Model: {result['model']}")
            print(f"Original length: {result['original_length']} characters")
            print(f"Summary length: {result['summary_length']} characters")
            print("\n" + "-"*60)
            print(result['summary'])
            print("-"*60)
            
            return result
            
    except FileNotFoundError:
        print(f"Error: File '{file_path}' not found")
        sys.exit(1)
    except requests.exceptions.HTTPError as e:
        print(f"HTTP Error: {e}")
        if e.response:
            try:
                error_detail = e.response.json()
                print(f"Details: {error_detail.get('detail', 'Unknown error')}")
            except:
                print(f"Response: {e.response.text}")
        sys.exit(1)
    except Exception as e:
        print(f"Error: {e}")
        sys.exit(1)

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Summarize a document using the API")
    parser.add_argument("file", help="Path to the document file")
    parser.add_argument("--url", default="http://localhost:8000", help="API base URL")
    parser.add_argument("--model", help="Ollama model name")
    parser.add_argument("--max-length", type=int, help="Maximum summary length in words")
    
    args = parser.parse_args()
    summarize_document(args.file, args.url, args.model, args.max_length)
```

**Usage:**
```bash
python summarize_example.py document.pdf --model llama2 --max-length 200
```

