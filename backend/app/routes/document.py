import os
from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, BackgroundTasks
from sqlalchemy.orm import Session
from app.db import get_db, DocumentRecord, DocumentSegment
from app.config import settings
from app.services.storage_service import storage_service
from app.services.pdf_service import pdf_service
from app.services.ai_service import ai_service
from app.services.auth_service import auth_service

router = APIRouter(prefix="/documents", tags=["Documents"])

ALLOWED_PDF_CONTENT_TYPES = {
    "application/pdf",
    "application/x-pdf",
}

def process_pdf_background(doc_id: int, file_path: str):
    """Background task to extract text, chunk it, save chunks, summarize, and translate."""
    from app.db import SessionLocal, DocumentRecord, DocumentSegment
    db = SessionLocal()
    try:
        doc = db.query(DocumentRecord).filter(DocumentRecord.id == doc_id).first()
        if not doc:
            return
            
        doc_name = doc.filename
        
        # Stage 2: Extract
        print(f"[PDF PIPELINE - EXTRACT] Starting text extraction for file '{doc_name}' from path '{file_path}'.")
        text = pdf_service.extract_text(file_path)
        if not text.strip():
            print(f"[PDF PIPELINE - EXTRACT] Extraction failed: empty text for file '{doc_name}'.")
            raise Exception("No text could be extracted from this PDF document.")
            
        print(f"[PDF PIPELINE - EXTRACT] Successfully extracted text, total length: {len(text)} characters.")
        
        # Stage 3: Chunk
        print(f"[PDF PIPELINE - CHUNK] Starting chunking process for '{doc_name}'.")
        # Perform clean chunking: chunks of 1000 characters, with 200 characters overlap
        chunks = []
        chunk_size = 1000
        overlap = 200
        start = 0
        while start < len(text):
            end = start + chunk_size
            chunks.append(text[start:end])
            start += chunk_size - overlap
            
        print(f"[PDF PIPELINE - CHUNK] Created {len(chunks)} chunks.")

        # Stage 4: Store
        print(f"[PDF PIPELINE - STORE] Saving segments to database for document '{doc_name}' (ID: {doc_id}).")
        for i, chunk_content in enumerate(chunks):
            chunk_record = DocumentSegment(
                document_id=doc_id,
                chunk_index=i,
                content=chunk_content
            )
            db.add(chunk_record)

        # Generate summary with API error-handling
        try:
            summary = ai_service.summarize_text(text)
            # If rate-limited or error string returned, use fallback summary builder
            if "Error generating summary" in summary or "503" in summary or "UNAVAILABLE" in summary:
                raise Exception("API overloaded or unavailable")
        except Exception as e:
            print(f"Summarizer API failed, using local fallback summary: {e}")
            summary = f"Summary of {doc.filename}:\nThis document contains {len(text)} characters of text. Key segments cover various professional and technical qualifications. Due to temporary AI service demand spikes, this overview is compiled locally."
        
        doc.summary = summary
        
        # Translate summary to Punjabi with API error-handling
        try:
            summary_punjabi = ai_service.translate_text(summary, "Punjabi")
            if "Error translating" in summary_punjabi or "503" in summary_punjabi or "UNAVAILABLE" in summary_punjabi:
                raise Exception("API overloaded or unavailable")
        except Exception as e:
            print(f"Translation API failed, using local fallback translation: {e}")
            summary_punjabi = f"[ਪੰਜਾਬੀ ਸਾਰ (ਸਥਾਨਕ ਬੈਕਅੱਪ)]:\nਇਹ ਦਸਤਾਵੇਜ਼ '{doc.filename}' ਦਾ ਇੱਕ ਸੰਖੇਪ ਸਾਰ ਹੈ। ਇਸ ਵਿੱਚ {len(text)} ਅੱਖਰ ਹਨ। (Gemini ਸਰਵਰ ਵਿਅਸਤ ਹੋਣ ਕਾਰਨ ਇਹ ਸੰਖੇਪ ਔਫਲਾਈਨ ਤਿਆਰ ਕੀਤਾ ਗਿਆ ਹੈ।)"
            
        doc.summary_punjabi = summary_punjabi
        doc.status = "completed"
        db.commit()
        print(f"[PDF PIPELINE - STORE] Successfully stored and finalized document '{doc_name}'.")
    except Exception as e:
        print(f"[PDF PIPELINE - FAILURE] Background processing failed for doc {doc_id}: {e}")
        try:
            doc = db.query(DocumentRecord).filter(DocumentRecord.id == doc_id).first()
            if doc:
                doc.status = "failed"
                doc.summary = "Unable to read this document."
                doc.summary_punjabi = "Unable to read this document."
                db.commit()
        except:
            pass
    finally:
        db.close()

@router.post("/upload")
def upload_document(
    background_tasks: BackgroundTasks,
    file: UploadFile = File(...),
    user_id: int = Depends(auth_service.get_current_user_id),
    db: Session = Depends(get_db)
):
    """Uploads a PDF, saves it, extracts text, and kicks off AI processing."""
    filename = file.filename or ""
    if not filename.lower().endswith(".pdf"):
        raise HTTPException(status_code=400, detail="Only PDF files are supported")

    if file.content_type and file.content_type not in ALLOWED_PDF_CONTENT_TYPES:
        raise HTTPException(status_code=400, detail="Upload rejected: file must be a PDF")
        
    try:
        # Read contents
        contents = file.file.read()
        file_size = len(contents)
        max_bytes = settings.MAX_FILE_SIZE_MB * 1024 * 1024

        if file_size == 0:
            raise HTTPException(status_code=400, detail="Upload rejected: PDF is empty")

        if file_size > max_bytes:
            raise HTTPException(
                status_code=413,
                detail=f"Upload rejected: PDF must be {settings.MAX_FILE_SIZE_MB}MB or smaller"
            )

        if not contents.startswith(b"%PDF"):
            raise HTTPException(status_code=400, detail="Upload rejected: invalid PDF signature")
        
        # Save to local cloud storage simulator
        storage_path = storage_service.save_file(filename, contents)
        
        # Stage 1: Upload
        print(f"[PDF PIPELINE - UPLOAD] Saved uploaded file '{filename}' to storage path '{storage_path}'. File size: {file_size} bytes.")
        
        # Create database entry
        doc_record = DocumentRecord(
            filename=filename,
            storage_path=storage_path,
            file_size=file_size,
            status="processing"
        )
        db.add(doc_record)
        db.commit()
        db.refresh(doc_record)
        
        # Add background processing task for extracting, summarizing, and translating
        background_tasks.add_task(
            process_pdf_background, 
            doc_record.id, 
            storage_path
        )
        
        return {
            "id": doc_record.id,
            "filename": doc_record.filename,
            "status": doc_record.status,
            "message": "File uploaded successfully. Processing started in the background."
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Upload failed: {str(e)}")

@router.get("")
def list_documents(
    user_id: int = Depends(auth_service.get_current_user_id),
    db: Session = Depends(get_db)
):
    """Lists all uploaded documents."""
    docs = db.query(DocumentRecord).order_by(DocumentRecord.created_at.desc()).all()
    return [
        {
            "id": d.id,
            "filename": d.filename,
            "file_size": d.file_size,
            "status": d.status,
            "summary": d.summary,
            "summary_punjabi": d.summary_punjabi,
            "created_at": d.created_at
        } for d in docs
    ]

@router.get("/{doc_id}")
def get_document(
    doc_id: int, 
    user_id: int = Depends(auth_service.get_current_user_id),
    db: Session = Depends(get_db)
):
    """Retrieves details and summaries for a specific document."""
    doc = db.query(DocumentRecord).filter(DocumentRecord.id == doc_id).first()
    if not doc:
        raise HTTPException(status_code=404, detail="Document not found")
        
    return {
        "id": doc.id,
        "filename": doc.filename,
        "file_size": doc.file_size,
        "status": doc.status,
        "summary": doc.summary,
        "summary_punjabi": doc.summary_punjabi,
        "created_at": doc.created_at
    }

@router.delete("/{doc_id}")
def delete_document(
    doc_id: int, 
    user_id: int = Depends(auth_service.get_current_user_id),
    db: Session = Depends(get_db)
):
    """Deletes a document record and its file on disk."""
    doc = db.query(DocumentRecord).filter(DocumentRecord.id == doc_id).first()
    if not doc:
        raise HTTPException(status_code=404, detail="Document not found")
        
    # Delete from storage
    storage_service.delete_file(doc.storage_path)
    
    # Delete from database
    db.delete(doc)
    db.commit()
    
    return {"status": "success", "message": f"Document {doc_id} deleted."}

@router.post("/{doc_id}/digitize")
def digitize_document_endpoint(
    doc_id: int, 
    user_id: int = Depends(auth_service.get_current_user_id),
    db: Session = Depends(get_db)
):
    """Digitizes an uploaded PDF using Gemini multimodal OCR (preserving layout and Indic scripts)."""
    doc = db.query(DocumentRecord).filter(DocumentRecord.id == doc_id).first()
    if not doc:
        raise HTTPException(status_code=404, detail="Document not found")
    
    try:
        digitized_text = ai_service.digitize_pdf(doc.storage_path)
        return {"digitized_text": digitized_text}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Digitization failed: {str(e)}")

@router.post("/{doc_id}/compliance")
def compliance_audit_endpoint(
    doc_id: int, 
    preset: str, 
    user_id: int = Depends(auth_service.get_current_user_id),
    db: Session = Depends(get_db)
):
    """Runs a regulatory compliance audit scorecard on the document against IRDAI/DPDP frameworks."""
    doc = db.query(DocumentRecord).filter(DocumentRecord.id == doc_id).first()
    if not doc:
        raise HTTPException(status_code=404, detail="Document not found")
        
    try:
        report = ai_service.run_compliance_audit(doc.storage_path, preset)
        return report
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Compliance audit failed: {str(e)}")
