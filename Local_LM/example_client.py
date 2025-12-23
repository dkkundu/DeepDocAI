#!/usr/bin/env python3
"""
Simple example client for the document summarizer API
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
        max_length: Optional maximum summary length in words
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

