from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy.orm import Session
from app.db import get_db, ChatMessage, DocumentMetadata, Conversation
from app.services.auth_service import auth_service
from app.services.ai_service import ai_service
from app.services.ai_router import ai_router
from app.services.search_service import search_service
from app.services.pdf_service import pdf_service
from datetime import datetime

router = APIRouter(prefix="", tags=["Chat & Conversations"])

class ChatMessagePayload(BaseModel):
    role: str
    content: str

class ChatRequest(BaseModel):
    message: str
    conversation_id: int
    enable_search: bool = False
    history: list[ChatMessagePayload] = []
    language: str | None = "English"
    personality: str | None = "friendly"

class ChatResponse(BaseModel):
    message_id: int
    response: str
    search_results: list[dict] | None = None
    has_search: bool

class ConversationCreate(BaseModel):
    document_id: int | None = None

class ConversationUpdate(BaseModel):
    title: str | None = None
    document_id: int | None = None

# -------------------- CONVERSATION ENDPOINTS --------------------

@router.get("/conversations")
def list_conversations(
    user_id: int = Depends(auth_service.get_current_user_id), 
    db: Session = Depends(get_db)
):
    """Lists all past chat conversations belonging to the current user."""
    conversations = db.query(Conversation).filter(Conversation.user_id == user_id).order_by(Conversation.created_at.desc()).all()
    return [
        {
            "id": c.id,
            "title": c.title,
            "created_at": c.created_at,
            "document_id": c.document_id,
            "document_name": c.document.filename if c.document else None
        } for c in conversations
    ]

@router.post("/conversations")
def create_conversation(
    payload: ConversationCreate, 
    user_id: int = Depends(auth_service.get_current_user_id),
    db: Session = Depends(get_db)
):
    """Creates a new conversation session, optionally attaching a PDF, for the current user."""
    new_conv = Conversation(
        title="New Conversation",
        document_id=payload.document_id,
        user_id=user_id
    )
    db.add(new_conv)
    db.commit()
    db.refresh(new_conv)
    return {
        "id": new_conv.id,
        "title": new_conv.title,
        "created_at": new_conv.created_at,
        "document_id": new_conv.document_id
    }

@router.put("/conversations/{conversation_id}")
def update_conversation(
    conversation_id: int, 
    payload: ConversationUpdate, 
    user_id: int = Depends(auth_service.get_current_user_id),
    db: Session = Depends(get_db)
):
    """Updates conversation properties belonging to the current user."""
    conv = db.query(Conversation).filter(Conversation.id == conversation_id, Conversation.user_id == user_id).first()
    if not conv:
        raise HTTPException(status_code=404, detail="Conversation not found")
        
    if payload.title is not None:
        conv.title = payload.title
    if payload.document_id is not None:
        # If document_id is -1, it means detach the document
        if payload.document_id == -1:
            conv.document_id = None
        else:
            conv.document_id = payload.document_id
            
    db.commit()
    return {"status": "success", "message": "Conversation updated"}

@router.delete("/conversations/{conversation_id}")
def delete_conversation(
    conversation_id: int, 
    user_id: int = Depends(auth_service.get_current_user_id),
    db: Session = Depends(get_db)
):
    """Deletes a conversation session and all its messages belonging to the current user."""
    conv = db.query(Conversation).filter(Conversation.id == conversation_id, Conversation.user_id == user_id).first()
    if not conv:
        raise HTTPException(status_code=404, detail="Conversation not found")
        
    db.delete(conv)
    db.commit()
    return {"status": "success", "message": "Conversation deleted"}

@router.delete("/conversations/{conversation_id}/messages")
def clear_conversation_messages(
    conversation_id: int, 
    user_id: int = Depends(auth_service.get_current_user_id),
    db: Session = Depends(get_db)
):
    """Clears all messages in a specific conversation session belonging to the current user."""
    conv = db.query(Conversation).filter(Conversation.id == conversation_id, Conversation.user_id == user_id).first()
    if not conv:
        raise HTTPException(status_code=404, detail="Conversation not found")
    db.query(ChatMessage).filter(ChatMessage.conversation_id == conversation_id).delete()
    db.commit()
    return {"status": "success", "message": "History cleared"}

@router.delete("/conversations/{conversation_id}/messages/last")
def delete_last_message(
    conversation_id: int, 
    user_id: int = Depends(auth_service.get_current_user_id),
    db: Session = Depends(get_db)
):
    """Deletes the last user message and any subsequent assistant response."""
    conv = db.query(Conversation).filter(Conversation.id == conversation_id, Conversation.user_id == user_id).first()
    if not conv:
        raise HTTPException(status_code=404, detail="Conversation not found")
        
    last_user_msg = (
        db.query(ChatMessage)
        .filter(ChatMessage.conversation_id == conversation_id, ChatMessage.role == "user")
        .order_by(ChatMessage.id.desc())
        .first()
    )
    if not last_user_msg:
        raise HTTPException(status_code=404, detail="No user messages found")

    # Delete all messages after or equal to the last user message's ID
    db.query(ChatMessage).filter(
        ChatMessage.conversation_id == conversation_id,
        ChatMessage.id >= last_user_msg.id
    ).delete()
    db.commit()
    return {"status": "success", "message": "Last message deleted"}

@router.get("/conversations/{conversation_id}/messages")
def get_conversation_messages(
    conversation_id: int, 
    user_id: int = Depends(auth_service.get_current_user_id),
    db: Session = Depends(get_db)
):
    """Fetches all messages in a specific conversation belonging to current user."""
    conv = db.query(Conversation).filter(Conversation.id == conversation_id, Conversation.user_id == user_id).first()
    if not conv:
        raise HTTPException(status_code=404, detail="Conversation not found")
        
    messages = (
        db.query(ChatMessage)
        .filter(ChatMessage.conversation_id == conversation_id)
        .order_by(ChatMessage.timestamp.asc())
        .all()
    )
    return [
        {
            "id": m.id,
            "role": m.role,
            "content": m.content,
            "timestamp": m.timestamp,
            "has_search": m.has_search,
            "document_id": m.document_id,
            "rating": m.rating,
            "feedback_notes": m.feedback_notes
        } for m in messages
    ]

class FeedbackPayload(BaseModel):
    rating: int  # 1 for positive, -1 for negative
    feedback_notes: str | None = None

@router.post("/conversations/{conversation_id}/messages/{message_id}/feedback")
def submit_message_feedback(
    conversation_id: int,
    message_id: int,
    payload: FeedbackPayload,
    user_id: int = Depends(auth_service.get_current_user_id),
    db: Session = Depends(get_db)
):
    """Submits user evaluation feedback on model response quality (Thumbs Up/Down). Used to gather alignment dataset logs."""
    conv = db.query(Conversation).filter(Conversation.id == conversation_id, Conversation.user_id == user_id).first()
    if not conv:
        raise HTTPException(status_code=404, detail="Conversation session not found")
        
    msg = db.query(ChatMessage).filter(ChatMessage.id == message_id, ChatMessage.conversation_id == conversation_id).first()
    if not msg:
        raise HTTPException(status_code=404, detail="Message not found")
        
    msg.rating = payload.rating
    if payload.feedback_notes is not None:
        msg.feedback_notes = payload.feedback_notes
        
    db.commit()
    return {"status": "success", "message": "Feedback submitted successfully"}

# -------------------- CHAT ENDPOINTS --------------------

@router.post("/chat", response_model=ChatResponse)
def chat_endpoint(
    request: ChatRequest, 
    user_id: int = Depends(auth_service.get_current_user_id),
    db: Session = Depends(get_db)
):
    user_message = request.message
    conv_id = request.conversation_id
    enable_search = request.enable_search
    
    # 1. Retrieve Conversation belonging to current user
    conv = db.query(Conversation).filter(Conversation.id == conv_id, Conversation.user_id == user_id).first()
    if not conv:
        raise HTTPException(status_code=404, detail="Conversation session not found")

    # 2. Auto-rename conversation if it is named "New Conversation"
    if conv.title == "New Conversation":
        # Rename to first 35 characters of user query
        conv.title = user_message[:35] + ("..." if len(user_message) > 35 else "")
        db.commit()

    # 3. Save User Message
    db_user_msg = ChatMessage(
        role="user",
        content=user_message,
        conversation_id=conv_id,
        document_id=conv.document_id,
        has_search=enable_search
    )
    db.add(db_user_msg)
    db.commit()

    # 4. Build Context History
    history_list = []
    for msg in request.history:
        history_list.append({"role": msg.role, "content": msg.content})
    history_list.append({"role": "user", "content": user_message})

    # 5. Build AI Prompts
    search_results = None
    lang = request.language or "English"
    vibe = request.personality or "friendly"
    
    system_instruction = (
        f"You are YAAR, an intelligent digital companion for everyday life in India. "
        f"You are speaking to your user in {lang}. "
        f"Your personality vibe mode is '{vibe}'. "
    )
    if vibe == "friendly":
        system_instruction += (
            "Be extremely friendly, casual, and warm. Talk like a close friend (a true 'Yaar'). "
            "Use warm, positive expressions. Avoid dry, formal assistant templates."
        )
    elif vibe == "regional":
        system_instruction += (
            "Inject local cultural phrases, idioms, and regional greetings naturally. "
            "Make the user feel deeply understood and connected to their local culture."
        )
    else: # formal
        system_instruction += (
            "Be highly respectful, polite, and formal. Use structured answers and respectful pronouns."
        )

    # Inject PDF Context if attached to conversation
    if conv.document_id:
        doc = db.query(DocumentMetadata).filter(DocumentMetadata.id == conv.document_id).first()
        if doc and doc.status == "completed":
            try:
                full_text = pdf_service.extract_text(doc.storage_path)
                context_text = full_text[:25000] # Safe limit
                
                system_instruction += (
                    f"\n\nYou are answering questions about the attached document: '{doc.filename}'. "
                    f"Use the following document text as your primary source of information. "
                    f"If the answer cannot be found in the text, mention that but use your general knowledge to help as well.\n\n"
                    f"--- DOCUMENT TEXT START ---\n{context_text}\n--- DOCUMENT TEXT END ---"
                )
            except Exception as e:
                system_instruction += f"\n\nNote: An error occurred reading the document context: {str(e)}"

    # Inject Search Context
    if enable_search:
        search_results = search_service.search(user_message)
        search_context = search_service.format_search_results(search_results)
        
        system_instruction += (
            f"\n\nYou have access to real-time search engine results for the user's query. "
            f"Use the following search results to provide a current and factual answer. "
            f"Synthesize the search results and cite them if appropriate.\n\n"
            f"--- SEARCH RESULTS START ---\n{search_context}\n--- SEARCH RESULTS END ---"
        )

    # 6. Generate Response with AIRouter multi-model routing & offline local fallback
    router_response = ai_router.generate_chat_response(
        messages=history_list, 
        system_instruction=system_instruction
    )
    
    ai_response = router_response["text"]
    
    # If we fell back to offline engine and there is an attached document, attempt local keyword extraction
    if router_response["status"] == "local_fallback" and conv.document_id:
        doc = db.query(DocumentMetadata).filter(DocumentMetadata.id == conv.document_id).first()
        if doc:
            try:
                # Find matching passages from the document text
                from app.services.pdf_service import pdf_service
                full_text = pdf_service.extract_text(doc.storage_path)
                
                # Tokenize user query to find keywords
                keywords = [w.lower() for w in user_message.split() if len(w) > 3]
                
                # Split full text into paragraphs
                paragraphs = [p.strip() for p in full_text.split("\n") if p.strip()]
                matching_passages = []
                
                for p in paragraphs:
                    p_lower = p.lower()
                    score = sum(1 for kw in keywords if kw in p_lower)
                    if score > 0:
                        matching_passages.append((score, p))
                        
                # Sort matching passages by score (descending)
                matching_passages.sort(key=lambda x: x[0], reverse=True)
                
                # Take top 4 passages
                excerpts = [p for score, p in matching_passages[:4]]
                
                if excerpts:
                    excerpt_text = "\n\n• ".join(excerpts)
                    ai_response = (
                        "⚠️ **[Local Offline Search Mode: Live AI endpoints busy/offline]**\n\n"
                        f"I've searched the document **'{doc.filename}'** locally for your query. "
                        "Here are the most relevant matching excerpts:\n\n"
                        f"• {excerpt_text}\n\n"
                        "*(Standard AI answers will resume once connectivity resets)*"
                    )
                else:
                    # Fallback to pre-computed summary
                    ai_response = (
                        "⚠️ **[Local Offline Mode: Live AI endpoints busy/offline]**\n\n"
                        f"Here is the pre-computed summary of **'{doc.filename}'**:\n\n"
                        f"{doc.summary}\n\n"
                        "*(Standard AI answers will resume once connectivity resets)*"
                    )
            except Exception as parse_err:
                print(f"Fallback text extraction failed: {parse_err}")
                ai_response = (
                    "⚠️ **[Local Offline Mode: Live AI endpoints busy/offline]**\n\n"
                    f"Here is the pre-computed summary of **'{doc.filename}'**:\n\n"
                    f"{doc.summary}\n\n"
                    "*(Standard AI answers will resume once connectivity resets)*"
                )

    # 7. Save Assistant Message
    db_assistant_msg = ChatMessage(
        role="assistant",
        content=ai_response,
        conversation_id=conv_id,
        document_id=conv.document_id,
        has_search=enable_search
    )
    db.add(db_assistant_msg)
    db.commit()

    return ChatResponse(
        message_id=db_assistant_msg.id,
        response=ai_response,
        search_results=search_results,
        has_search=enable_search
    )
