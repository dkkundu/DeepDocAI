import asyncio
from pathlib import Path
from typing import Optional
import logging

logger = logging.getLogger(__name__)


class DocumentParser:
    """Parser for various document formats"""
    
    async def parse_document(self, file_path: Path, file_ext: str) -> str:
        """
        Parse document and extract text content.
        
        Args:
            file_path: Path to the document file
            file_ext: File extension (e.g., '.pdf', '.docx', '.doc')
        
        Returns:
            Extracted text content
        """
        file_ext = file_ext.lower()
        
        if file_ext == '.pdf':
            return await self._parse_pdf(file_path)
        elif file_ext == '.docx':
            return await self._parse_docx(file_path)
        elif file_ext == '.doc':
            return await self._parse_doc(file_path)
        else:
            raise ValueError(f"Unsupported file type: {file_ext}")
    
    async def _parse_pdf(self, file_path: Path) -> str:
        """Parse PDF file"""
        try:
            import PyPDF2
            
            # Run in thread pool to avoid blocking
            loop = asyncio.get_event_loop()
            text = await loop.run_in_executor(
                None,
                self._extract_pdf_text,
                file_path
            )
            return text
        except ImportError:
            raise ImportError(
                "PyPDF2 is required for PDF parsing. Install it with: pip install PyPDF2"
            )
        except Exception as e:
            logger.error(f"PDF parsing error: {e}")
            raise Exception(f"Failed to parse PDF: {str(e)}")
    
    def _extract_pdf_text(self, file_path: Path) -> str:
        """Synchronous PDF text extraction"""
        import PyPDF2
        
        text_parts = []
        with open(file_path, 'rb') as file:
            pdf_reader = PyPDF2.PdfReader(file)
            for page_num, page in enumerate(pdf_reader.pages):
                try:
                    text = page.extract_text()
                    if text:
                        text_parts.append(text)
                except Exception as e:
                    logger.warning(f"Error extracting text from page {page_num + 1}: {e}")
        
        return "\n\n".join(text_parts)
    
    async def _parse_docx(self, file_path: Path) -> str:
        """Parse DOCX file"""
        try:
            from docx import Document
            
            loop = asyncio.get_event_loop()
            text = await loop.run_in_executor(
                None,
                self._extract_docx_text,
                file_path
            )
            return text
        except ImportError:
            raise ImportError(
                "python-docx is required for DOCX parsing. Install it with: pip install python-docx"
            )
        except Exception as e:
            logger.error(f"DOCX parsing error: {e}")
            raise Exception(f"Failed to parse DOCX: {str(e)}")
    
    def _extract_docx_text(self, file_path: Path) -> str:
        """Synchronous DOCX text extraction"""
        from docx import Document
        
        doc = Document(file_path)
        paragraphs = [para.text for para in doc.paragraphs if para.text.strip()]
        return "\n\n".join(paragraphs)
    
    async def _parse_doc(self, file_path: Path) -> str:
        """Parse DOC file (older Microsoft Word format)"""
        try:
            import textract
            
            loop = asyncio.get_event_loop()
            text = await loop.run_in_executor(
                None,
                textract.process,
                str(file_path)
            )
            # textract returns bytes, decode to string
            return text.decode('utf-8', errors='ignore')
        except ImportError:
            raise ImportError(
                "textract is required for DOC parsing. Install it with: pip install textract"
            )
        except Exception as e:
            logger.error(f"DOC parsing error: {e}")
            raise Exception(f"Failed to parse DOC: {str(e)}")

