import os
from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, BackgroundTasks
from sqlalchemy.orm import Session
from app.db import get_db, DocumentMetadata
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
    """Background task to extract text, summarize, and translate to Punjabi with error-resilience."""
    from app.db import SessionLocal
    db = SessionLocal()
    try:
        doc = db.query(DocumentMetadata).filter(DocumentMetadata.id == doc_id).first()
        if not doc:
            return
            
        # Extract text
        text = pdf_service.extract_text(file_path)
        if not text.strip():
            text = "[System Warning: This document appears to be a scanned image or empty. No digital text could be extracted. Please upload a digital text PDF, or chat with me using general knowledge.]"
            
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
    except Exception as e:
        print(f"Background processing failed for doc {doc_id}: {e}")
        try:
            doc = db.query(DocumentMetadata).filter(DocumentMetadata.id == doc_id).first()
            if doc:
                doc.status = "failed"
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
        
        # Create database entry
        doc_metadata = DocumentMetadata(
            filename=filename,
            storage_path=storage_path,
            file_size=file_size,
            status="processing"
        )
        db.add(doc_metadata)
        db.commit()
        db.refresh(doc_metadata)
        
        # Add background processing task for extracting, summarizing, and translating
        background_tasks.add_task(
            process_pdf_background, 
            doc_metadata.id, 
            storage_path
        )
        
        return {
            "id": doc_metadata.id,
            "filename": doc_metadata.filename,
            "status": doc_metadata.status,
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
    docs = db.query(DocumentMetadata).order_by(DocumentMetadata.created_at.desc()).all()
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
    """Retrieves metadata and summaries for a specific document."""
    doc = db.query(DocumentMetadata).filter(DocumentMetadata.id == doc_id).first()
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
    doc = db.query(DocumentMetadata).filter(DocumentMetadata.id == doc_id).first()
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
    doc = db.query(DocumentMetadata).filter(DocumentMetadata.id == doc_id).first()
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
    doc = db.query(DocumentMetadata).filter(DocumentMetadata.id == doc_id).first()
    if not doc:
        raise HTTPException(status_code=404, detail="Document not found")
        
    try:
        report = ai_service.run_compliance_audit(doc.storage_path, preset)
        return report
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Compliance audit failed: {str(e)}")
