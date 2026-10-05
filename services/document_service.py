import io
import uuid
from typing import Dict, Any, Optional
from pypdf import PdfReader
from core.database import save_document, get_document, get_all_documents, delete_document

class DocumentService:
    """
    Parses, stores, and performs context extraction for uploaded documents 
    (PDF, DOCX, TXT, CSV, JSON, Markdown, Code files, etc.)
    """

    async def process_file(self, filename: str, content_bytes: bytes) -> Dict[str, Any]:
        doc_id = str(uuid.uuid4())
        ext = filename.split(".")[-1].lower() if "." in filename else "txt"
        
        extracted_text = ""
        
        if ext == "pdf":
            try:
                reader = PdfReader(io.BytesIO(content_bytes))
                pages_text = []
                for i, page in enumerate(reader.pages):
                    t = page.extract_text() or ""
                    pages_text.append(f"--- Page {i+1} ---\n{t}")
                extracted_text = "\n\n".join(pages_text)
            except Exception as e:
                extracted_text = f"[PDF Extraction Error: {str(e)}]"
        elif ext in ["docx", "doc"]:
            try:
                import docx
                doc = docx.Document(io.BytesIO(content_bytes))
                extracted_text = "\n\n".join([p.text for p in doc.paragraphs if p.text.strip()])
            except Exception as e:
                extracted_text = f"[DOCX Extraction Error: {str(e)}]"
        elif ext in ["txt", "md", "csv", "json", "py", "js", "html", "css", "cpp", "c", "java", "sql", "xml", "yaml", "yml", "log"]:
            try:
                extracted_text = content_bytes.decode("utf-8", errors="replace")
            except Exception as e:
                extracted_text = f"[Text Decoding Error: {str(e)}]"
        else:
            try:
                extracted_text = content_bytes.decode("utf-8", errors="replace")
            except Exception:
                extracted_text = f"[Unsupported binary format: {filename}]"

        extracted_text = extracted_text.strip()
        preview = extracted_text[:300] + "..." if len(extracted_text) > 300 else extracted_text
        
        doc_data = save_document(
            doc_id=doc_id,
            filename=filename,
            file_type=ext,
            size=len(content_bytes),
            content=extracted_text,
            preview=preview
        )
        return doc_data

    def get_document_context(self, doc_id: str) -> Optional[str]:
        doc = get_document(doc_id)
        return doc["content"] if doc else None

    def list_documents(self):
        return get_all_documents()

    def remove_document(self, doc_id: str) -> bool:
        return delete_document(doc_id)

document_service = DocumentService()
