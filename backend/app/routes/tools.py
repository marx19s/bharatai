from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel
from app.services.ai_service import ai_service
from app.services.auth_service import auth_service

router = APIRouter(prefix="/tools", tags=["Tools"])

class TranslateRequest(BaseModel):
    text: str
    target_language: str = "Punjabi"

class TranslateResponse(BaseModel):
    translated_text: str
    target_language: str

class GrammarRequest(BaseModel):
    text: str

class GrammarResponse(BaseModel):
    corrected_text: str

@router.post("/translate", response_model=TranslateResponse)
def translate_endpoint(
    request: TranslateRequest,
    user_id: int = Depends(auth_service.get_current_user_id)
):
    """Direct text translation endpoint."""
    if not request.text.strip():
        raise HTTPException(status_code=400, detail="Text cannot be empty")
        
    try:
        translated = ai_service.translate_text(request.text, request.target_language)
        return TranslateResponse(
            translated_text=translated,
            target_language=request.target_language
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/grammar-fix", response_model=GrammarResponse)
def grammar_fix_endpoint(
    request: GrammarRequest,
    user_id: int = Depends(auth_service.get_current_user_id)
):
    """Direct grammar correction endpoint."""
    if not request.text.strip():
        raise HTTPException(status_code=400, detail="Text cannot be empty")
        
    try:
        corrected = ai_service.fix_grammar(request.text)
        return GrammarResponse(corrected_text=corrected)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
