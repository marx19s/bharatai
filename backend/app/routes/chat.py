from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy.orm import Session
from app.db import get_db, ChatMessage, DocumentRecord, DocumentSegment, Conversation
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
    source: str | None = "knowledge"

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
    import json
    return [
        {
            "id": m.id,
            "role": m.role,
            "content": m.content,
            "timestamp": m.timestamp,
            "has_search": m.has_search,
            "document_id": m.document_id,
            "rating": m.rating,
            "feedback_notes": m.feedback_notes,
            "source": m.source,
            "search_results": json.loads(m.search_results_raw) if m.search_results_raw else None
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
    # Automatic Knowledge Router: Detect if search is needed automatically
    def should_trigger_live_search(query: str) -> bool:
        q = query.lower()
        keywords = [
            "today", "current", "news", "price", "latest", "weather", "score", "live", "breaking",
            "gold", "silver", "nifty", "sensex", "stock", "shares", "minister", "president",
            "election", "gdp", "inflation", "ipl", "cricket", "match", "versus", " vs ",
            "temperature", "search online", "google", "search web", "lookup online", "online search"
        ]
        if any(kw in q for kw in keywords):
            return True
        if "who is" in q and not any(static in q for static in ["shakespeare", "einstein", "newton", "gandhi"]):
            return True
        return False

    enable_search = request.enable_search or should_trigger_live_search(user_message)
    
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
            "Make the user feel deeply understood and connected to their local culture. "
            "Speak like a close local friend: "
            "If speaking in Punjabi, speak naturally as a local friend would, using natural phrases like 'Main theek aa veere. Tu dass?' instead of textbook Punjabi translations. "
            "If speaking in Hindi, speak naturally like a friend, e.g. use 'Main theek hoon dost. Tum batao?'. "
            "If speaking in Gujarati, use friendly colloquialisms like 'Maja ma chu mitra. Tame kem cho?'. "
            "If speaking in Tamil, use natural friend speech like 'Naan nalla irukken nanba. Neenga eppadi irukeenga?'. "
            "Never use textbook translations; use natural conversational speech for all scheduled Indian languages."
        )
    else: # formal
        system_instruction += (
            "Be highly respectful, polite, and formal. Use structured answers and respectful pronouns."
        )

    # Constraint system instructions (NO AI-sounding responses)
    system_instruction += (
        "\n\nCRITICAL CONSTRAINTS:\n"
        "1. Answer first, explain second. Answer the query directly in the very first sentence.\n"
        "2. Do NOT use introductory filler (e.g., 'Sure', 'Certainly', 'Absolutely', 'Great question', 'You're asking about').\n"
        "3. You must NEVER use the following forbidden phrases: 'Sure', 'Certainly', 'Great question', 'Excellent question', "
        "'You're asking about', 'I'd be happy to help', 'Absolutely', 'Of course', "
        "'That's a fantastic question', 'Oh Yaar!'.\n"
        "4. Do NOT repeat the user's question.\n"
        "5. Keep responses natural and concise.\n"
    )

    # Inject PDF Context if attached to conversation
    is_doc_attached = False
    doc_context = ""
    doc_filenames_str = ""
    not_found_prefix = ""
    is_question_paper = False
    ai_response = ""
    source = "knowledge"
    
    if conv.document_id:
        doc = db.query(DocumentRecord).filter(DocumentRecord.id == conv.document_id).first()
        if doc:
            if doc.status == "failed":
                ai_response = "Unable to read this document."
                source = "document"
            elif doc.status == "completed":
                is_doc_attached = True
                doc_filenames_str = doc.filename
                try:
                    import re
                    # Stage 5: Retrieve
                    print(f"[PDF PIPELINE - RETRIEVE] Retrieving segments for document ID {conv.document_id}, filename '{doc_filenames_str}'. Query: '{user_message}'")
                    # Retrieve document segments from database
                    segments = db.query(DocumentSegment).filter(DocumentSegment.document_id == conv.document_id).all()
                    
                    # Simple keyword overlap search to find top 3 relevant chunks
                    words = re.findall(r'[a-zA-Z0-9]+', user_message.lower())
                    stopwords = {"the", "a", "an", "and", "or", "but", "is", "are", "was", "were", "of", "to", "for", "in", "on", "at", "with", "this", "that", "these", "those", "it", "its", "you", "your", "we", "our", "they", "them", "he", "she", "him", "her", "i", "me", "my", "how", "what", "why", "who", "where", "when", "which", "can", "could", "will", "would", "should"}
                    keywords = [w for w in words if (len(w) > 2 or w.isdigit() or (len(w) == 2 and w[0] == 'q' and w[1].isdigit())) and w not in stopwords]
                    
                    # Parse page numbers from query (e.g. "page 2" or "page two")
                    page_match = re.search(r'(?:page|p\.?)\s*(\d+)', user_message.lower())
                    target_page = int(page_match.group(1)) if page_match else None
                    if not target_page:
                        word_to_num = {
                            "one": 1, "first": 1, "two": 2, "second": 2, "three": 3, "third": 3,
                            "four": 4, "fourth": 4, "five": 5, "fifth": 5, "six": 6, "sixth": 6,
                            "seven": 7, "seventh": 7, "eight": 8, "eighth": 8, "nine": 9, "ninth": 9,
                            "ten": 10, "tenth": 10
                        }
                        for word, num in word_to_num.items():
                            if f"page {word}" in user_message.lower() or f"p. {word}" in user_message.lower():
                                target_page = num
                                break
    
                    # Parse target questions for question paper detection
                    target_questions = []
                    if any(p in user_message.lower() for p in ["first two", "first 2"]):
                        target_questions = [1, 2]
                    elif any(p in user_message.lower() for p in ["first question", "question 1", "q1", "q.1"]):
                        target_questions = [1]
                    elif any(p in user_message.lower() for p in ["second question", "question 2", "q2", "q.2"]):
                        target_questions = [2]
                    else:
                        # Map ordinal words like first, second, third, etc.
                        word_to_num_map = {
                            "first": 1, "second": 2, "third": 3, "fourth": 4, "fifth": 5,
                            "sixth": 6, "seventh": 7, "eighth": 8, "ninth": 9, "tenth": 10,
                            "one": 1, "two": 2, "three": 3, "four": 4, "five": 5, "six": 6,
                            "seven": 7, "eight": 8, "nine": 9, "ten": 10
                        }
                        for word, num in word_to_num_map.items():
                            if f"{word} question" in user_message.lower() or f"question {word}" in user_message.lower() or f"q {word}" in user_message.lower() or f"q.{word}" in user_message.lower():
                                if num not in target_questions:
                                    target_questions.append(num)
                        
                        if not target_questions:
                            q_nums = re.findall(r'(?:question|q\.?)\s*(\d+)', user_message.lower())
                            if q_nums:
                                target_questions = [int(n) for n in q_nums]
    
                    def segment_contains_question(content: str, q_num: int) -> bool:
                        content_lower = content.lower()
                        
                        # 1. Direct explicit question markers
                        patterns = [
                            rf"\bquestion\s*{q_num}\b",
                            rf"\bq\s*{q_num}\b",
                            rf"\bq\.\s*{q_num}\b",
                            rf"\bq{q_num}\b",
                            rf"\bq\.{q_num}\b",
                        ]
                        for p in patterns:
                            if re.search(p, content_lower):
                                return True
                                
                        # 2. Number list items like 1., 1), 1:
                        esc_q = str(q_num)
                        pattern_num = rf'(?:^|[\s\n\r\.\[\]\(\)])' + esc_q + rf'(?:[\.\)\:]|\b)'
                        if re.search(pattern_num, content_lower):
                            if re.search(rf'\b{esc_q}\b', content_lower) or re.search(rf'\b{esc_q}[\.\)\:]', content_lower):
                                return True
                                
                        return False
    
                    # Filter by target page if specified
                    if target_page:
                        page_segments = [s for s in segments if s.page_number == target_page]
                        if page_segments:
                            segments = page_segments
                    
                    scored_segments = []
                    for seg in segments:
                        seg_content_lower = seg.content.lower()
                        score = 0
                        for kw in keywords:
                            escaped_kw = re.escape(kw)
                            if kw.isdigit():
                                score += len(re.findall(rf'\b{escaped_kw}\b', seg_content_lower)) * 5
                            else:
                                score += len(re.findall(rf'\b{escaped_kw}\b', seg_content_lower))
                        
                        # Boost if target page matches
                        if target_page and seg.page_number == target_page:
                            score += 10000
                        
                        # Boost target questions
                        if target_questions:
                            for q_num in target_questions:
                                if segment_contains_question(seg.content, q_num):
                                    score += 5000
                        
                        # Boost first few chunks for "first two", "first 2"
                        is_first_few_query = any(phrase in user_message.lower() for phrase in ["first two", "first 2", "first questions", "start", "beginning", "first question"])
                        if is_first_few_query and seg.chunk_index is not None and seg.chunk_index < 4:
                            score += 100 - (seg.chunk_index * 20)
                        
                        scored_segments.append((score, seg))
                        
                    scored_segments.sort(key=lambda x: x[0], reverse=True)
                    
                    # 1. Early auto-detect if document is a question paper or test document
                    is_question_paper = False
                    if doc_filenames_str and any(term in doc_filenames_str.lower() for term in ["question", "paper", "exam", "test", "assignment"]):
                        is_question_paper = True
                    elif target_questions or any(term in user_message.lower() for term in ["question", "solve", "exam", "paper", "test", "assignment"]):
                        is_question_paper = True

                    # 2. Retrieve segments and expand context by pulling sequential neighbor segments
                    seg_by_index = {s.chunk_index: s for s in segments if s.chunk_index is not None}
                    retrieved_segments_objs = []
                    
                    if is_question_paper and len(segments) <= 30:
                        retrieved_segments_objs = sorted(segments, key=lambda x: x.chunk_index or 0)
                        print(f"[PDF PIPELINE - RETRIEVE] Question paper detected with {len(segments)} <= 30 chunks. Loading ENTIRE document as context.")
                    else:
                        top_segs = [s[1] for s in scored_segments[:3]]
                        retrieved_chunk_indices = set()
                        for seg in top_segs:
                            if seg.chunk_index not in retrieved_chunk_indices:
                                retrieved_chunk_indices.add(seg.chunk_index)
                                retrieved_segments_objs.append(seg)
                            
                            # Grab preceding and subsequent neighbor segments if it is a question paper to prevent missing parts
                            if is_question_paper:
                                for offset in [-2, -1, 1, 2, 3, 4]:
                                    neighbor_idx = seg.chunk_index + offset
                                    if neighbor_idx in seg_by_index and neighbor_idx not in retrieved_chunk_indices:
                                        retrieved_chunk_indices.add(neighbor_idx)
                                        retrieved_segments_objs.append(seg_by_index[neighbor_idx])
                        
                        retrieved_segments_objs.sort(key=lambda x: x.chunk_index or 0)
                    
                    retrieved_segments = [s.content for s in retrieved_segments_objs]
                    doc_context = "\n\n---\n\n".join(retrieved_segments)
                    print(f"[PDF PIPELINE - RETRIEVE] Retrieved {len(retrieved_segments)} segments (including neighbor expansion). Best segment score: {scored_segments[0][0] if scored_segments else 0}")
                    
                    # Secondary fallback verification check for question paper markers
                    if not is_question_paper and doc_context:
                        question_markers = len(re.findall(r'\b(?:question|q\b|q\.)\s*\d+\b', doc_context.lower()))
                        num_list_markers = len(re.findall(r'(?:^|[\n\r])\s*\d+[\.\)]\s+', doc_context))
                        if question_markers >= 2 or num_list_markers >= 3:
                            is_question_paper = True
                            if len(segments) <= 30:
                                retrieved_segments_objs = sorted(segments, key=lambda x: x.chunk_index or 0)
                            else:
                                retrieved_chunk_indices = set(s.chunk_index for s in retrieved_segments_objs)
                                for seg in top_segs:
                                    for offset in [-2, -1, 1, 2, 3, 4]:
                                        neighbor_idx = seg.chunk_index + offset
                                        if neighbor_idx in seg_by_index and neighbor_idx not in retrieved_chunk_indices:
                                            retrieved_chunk_indices.add(neighbor_idx)
                                            retrieved_segments_objs.append(seg_by_index[neighbor_idx])
                                retrieved_segments_objs.sort(key=lambda x: x.chunk_index or 0)
                            
                            retrieved_segments = [s.content for s in retrieved_segments_objs]
                            doc_context = "\n\n---\n\n".join(retrieved_segments)

                    # 3. Extract question text
                    combined_q_text = ""
                    if is_question_paper:
                        if target_questions:
                            extracted_questions = []
                            for q_num in target_questions:
                                lines = doc_context.split('\n')
                                q_text = ""
                                found = False
                                for idx, line in enumerate(lines):
                                    esc_q = str(q_num)
                                    pattern = rf'(?:^|[\s\n\r\.\[\]\(\)])(?:q|question)?\.?\s*{esc_q}(?:[\.\)\:]|\b)'
                                    if re.search(pattern, line.lower()):
                                        found = True
                                        q_text += line + "\n"
                                        for next_line in lines[idx+1:]:
                                            next_q_match = re.search(r'(?:^|[\s\n\r\.\[\]\(\)])(?:q|question)?\.?\s*(\d+)(?:[\.\)\:]|\b)', next_line.lower())
                                            if next_q_match:
                                                next_num = int(next_q_match.group(1))
                                                if next_num != q_num:
                                                    break
                                            q_text += next_line + "\n"
                                        break
                                if found and q_text.strip():
                                    extracted_questions.append(q_text.strip())
                            if extracted_questions:
                                combined_q_text = "\n\n".join(extracted_questions)
                        
                        # Fallback to the retrieved doc context if no specific questions were extracted
                        if not combined_q_text:
                            combined_q_text = doc_context
 
                except Exception as e:
                    print(f"Error reading doc context: {str(e)}")
                    is_question_paper = False
                    combined_q_text = ""
    
        # We will run strict PDF RAG first if document is attached
        ai_response = ""
        source = "knowledge"
        
        if is_doc_attached and doc_context:
            if is_question_paper and combined_q_text:
                # Question paper specific RAG flow (always answer the question using search + knowledge)
                q_paper_search_results = None
                q_paper_search_context = ""
                # Determine if search is needed for this question
                if enable_search or should_trigger_live_search(combined_q_text):
                    try:
                        search_query = combined_q_text
                        search_query_clean = re.sub(r'^\s*(?:q|question)?\.?\s*\d+\.?\s*', '', search_query, flags=re.IGNORECASE)
                        search_query_clean = search_query_clean[:100].strip()
                        print(f"[PDF PIPELINE - SEARCH] Question paper auto-triggered search. Query: '{search_query_clean}'")
                        q_paper_search_results = search_service.search(search_query_clean)
                        q_paper_search_context = search_service.format_search_results(q_paper_search_results)
                        enable_search = True
                        search_results = q_paper_search_results
                    except Exception as search_err:
                        print(f"Question paper search failed: {search_err}")

                doc_system_instruction = (
                    f"You are YAAR, an intelligent digital companion for everyday life in India.\n"
                    f"You are speaking to your user in {lang}.\n"
                    f"The user has uploaded a question paper: '{doc_filenames_str}'.\n"
                    f"They want you to answer the following question(s) from the paper:\n"
                    f"\"\"\"\n{combined_q_text}\n\"\"\"\n\n"
                    f"Here is the text context retrieved from the question paper:\n"
                    f"--- START RETRIEVED CHUNKS ---\n{doc_context}\n--- END RETRIEVED CHUNKS ---\n\n"
                )
                if q_paper_search_context:
                    doc_system_instruction += (
                        f"Here is the relevant live search context retrieved from the web:\n"
                        f"--- START SEARCH RESULTS ---\n{q_paper_search_context}\n--- END SEARCH RESULTS ---\n\n"
                        f"You MUST use inline citations (e.g. [1], [2]) to cite the search results wherever you state facts derived from them. Do not cite if not supported.\n\n"
                    )
                doc_system_instruction += (
                    f"CRITICAL INSTRUCTIONS:\n"
                    f"1. Clearly state in your very first sentence that you are answering the question from the uploaded document '{doc_filenames_str}' "
                    f"(e.g., 'Based on Question X from the uploaded document...').\n"
                    f"2. Solve/answer the question fully using the provided context, search results, and your general knowledge.\n"
                    f"3. Do NOT stop with 'answer not found' or say you cannot answer. Synthesize a complete answer.\n\n"
                    f"CRITICAL CONSTRAINTS:\n"
                    f"1. Answer first, explain second. Answer the query directly in the very first sentence.\n"
                    f"2. Do NOT use introductory filler (e.g., 'Sure', 'Certainly', 'Absolutely').\n"
                    f"3. Limit emojis to at most 1.\n"
                )
                
                print(f"[PDF PIPELINE - INJECT] Injecting question paper prompt for '{doc_filenames_str}'.")
                router_response = ai_router.generate_chat_response(
                    messages=history_list, 
                    system_instruction=doc_system_instruction
                )
                first_resp = router_response["text"].strip()
                is_not_found = (
                    "ANSWER_NOT_FOUND_IN_DOCUMENT" in first_resp or
                    "not found in the document" in first_resp.lower() or
                    "not mentioned in the provided" in first_resp.lower() or
                    "not mentioned in the document" in first_resp.lower() or
                    "does not contain information" in first_resp.lower() or
                    "is not contained in the retrieved" in first_resp.lower()
                )
                if not is_not_found:
                    ai_response = first_resp
                    source = "document"
                    print(f"[PDF PIPELINE - ANSWER] AI generated response for question paper. Source: {source}")
                else:
                    print(f"[PDF PIPELINE - FALLBACK] Question paper response not found. Falling back to general router.")
            else:
                # Regular document RAG flow
                doc_system_instruction = (
                    f"You are YAAR, an intelligent digital companion for everyday life in India.\n"
                    f"You are speaking to your user in {lang}.\n"
                    f"You are answering questions about the attached document: '{doc_filenames_str}'.\n\n"
                    f"Here are the top relevant retrieved chunks from the document:\n"
                    f"--- START RETRIEVED CHUNKS ---\n{doc_context}\n--- END RETRIEVED CHUNKS ---\n\n"
                    f"CRITICAL RAG INSTRUCTIONS:\n"
                    f"1. Check if the retrieved chunks contain the context or answer to the question being asked.\n"
                    f"2. If the user is asking to answer or solve questions (e.g. 'Answer Question 1', 'Answer first two questions') presented in the document, "
                    f"locate the question text inside the retrieved chunks, then answer/solve them using your general knowledge or search. Do NOT return 'ANSWER_NOT_FOUND_IN_DOCUMENT' if you find the question text. Answer it fully.\n"
                    f"3. Otherwise, if you are asked to summarize, explain, or retrieve details, answer strictly using the provided chunks. Do not make up facts.\n"
                    f"4. If the question/topic is entirely missing, not mentioned, or unrelated to the document, you MUST respond with exactly the text: 'ANSWER_NOT_FOUND_IN_DOCUMENT'.\n"
                    f"5. Clearly state in your response that the answer came from the uploaded document '{doc_filenames_str}' (e.g., 'According to the uploaded document...', 'Based on the provided document...').\n\n"
                    f"CRITICAL CONSTRAINTS:\n"
                    f"1. Answer first, explain second. Answer the query directly in the very first sentence.\n"
                    f"2. Do NOT use introductory filler (e.g., 'Sure', 'Certainly', 'Absolutely', 'Great question', 'You're asking about').\n"
                    f"3. Do NOT repeat the user's question.\n"
                    f"4. Limit emojis to at most 1.\n"
                )
                
                print(f"[PDF PIPELINE - INJECT] Injecting retrieved document context of '{doc_filenames_str}' into the system prompt.")
                router_response = ai_router.generate_chat_response(
                    messages=history_list, 
                    system_instruction=doc_system_instruction
                )
                
                first_resp = router_response["text"].strip()
                is_not_found = (
                    "ANSWER_NOT_FOUND_IN_DOCUMENT" in first_resp or
                    "not found in the document" in first_resp.lower() or
                    "not mentioned in the provided" in first_resp.lower() or
                    "not mentioned in the document" in first_resp.lower() or
                    "does not contain information" in first_resp.lower() or
                    "is not contained in the retrieved" in first_resp.lower()
                )
                if router_response["status"] != "local_fallback" and not is_not_found and first_resp:
                    ai_response = first_resp
                    source = "document"
                    print(f"[PDF PIPELINE - ANSWER] AI generated response based on document context. Source: {source}")
                else:
                    not_found_prefix = "I couldn't find the answer in the uploaded document. "
        elif is_doc_attached:
            not_found_prefix = "I couldn't find the answer in the uploaded document. "

    # If not answered from document, run fallback (web search or general knowledge)
    if not ai_response:
        # Re-initialize system instruction for fallback
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
                "Make the user feel deeply understood and connected to their local culture. "
                "Speak like a close local friend: "
                "If speaking in Punjabi, speak naturally as a local friend would, using natural phrases like 'Main theek aa veere. Tu dass?' instead of textbook Punjabi translations. "
                "If speaking in Hindi, speak naturally like a friend, e.g. use 'Main theek hoon dost. Tum batao?'. "
                "If speaking in Gujarati, use friendly colloquialisms like 'Maja ma chu mitra. Tame kem cho?'. "
                "If speaking in Tamil, use natural friend speech like 'Naan nalla irukken nanba. Neenga eppadi irukeenga?'. "
                "Never use textbook translations; use natural conversational speech for all scheduled Indian languages."
            )
        else: # formal
            system_instruction += (
                "Be highly respectful, polite, and formal. Use structured answers and respectful pronouns."
            )

        system_instruction += (
            "\n\nCRITICAL CONSTRAINTS:\n"
            "1. Answer first, explain second. Answer the query directly in the very first sentence.\n"
            "2. Do NOT use introductory filler (e.g., 'Sure', 'Certainly', 'Absolutely', 'Great question', 'You're asking about').\n"
            "3. You must NEVER use the following forbidden phrases: 'Sure', 'Certainly', 'Great question', 'Excellent question', "
            "'You're asking about', 'I'd be happy to help', 'Absolutely', 'Of course', "
            "'That's a fantastic question', 'Oh Yaar!'.\n"
            "4. Do NOT repeat the user's question.\n"
            "5. Keep responses natural and concise.\n"
            "6. Limit emojis to at most 1.\n"
        )

        if enable_search:
            try:
                search_results = search_service.search(user_message)
                search_context = search_service.format_search_results(search_results)
                
                system_instruction += (
                    f"\n\nYou have access to real-time search engine results for the user's query. "
                    f"You MUST use inline citations (e.g., [1], [2]) to cite the search results wherever you state facts derived from them. "
                    f"Never make up citations. Only cite the numbers of the search results provided.\n\n"
                    f"--- SEARCH RESULTS START ---\n{search_context}\n--- SEARCH RESULTS END ---"
                )
                source = "web"
            except Exception as search_err:
                print(f"Search service failed: {search_err}")
                ai_response = "Live search is temporarily unavailable."
                source = "web"
        else:
            source = "knowledge"

        if not ai_response:
            router_response = ai_router.generate_chat_response(
                messages=history_list, 
                system_instruction=system_instruction
            )
            
            # Local Offline Fallback
            if router_response["status"] == "local_fallback":
                if enable_search and 'search_results' in locals() and search_results:
                    excerpts = []
                    for r in search_results:
                        excerpts.append(f"**{r['title']}**\n{r['snippet']}\n*(Source: {r['link']})*")
                    excerpt_text = "\n\n• ".join(excerpts)
                    ai_response = (
                        "I am currently having some trouble connecting to the server, but I have searched the web locally for your query. "
                        "Here are the web search results:\n\n"
                        f"• {excerpt_text}"
                    )
                    source = "web"
                elif is_doc_attached:
                    try:
                        segments = db.query(DocumentSegment).filter(DocumentSegment.document_id == conv.document_id).all()
                        keywords = [w.lower().strip(".,?!;:()\"'") for w in user_message.split()]
                        keywords = [w for w in keywords if len(w) > 3]
                        
                        scored_segments = []
                        for seg in segments:
                            seg_content_lower = seg.content.lower()
                            score = sum(seg_content_lower.count(kw) for kw in keywords)
                            if score > 0:
                                scored_segments.append((score, seg.content))
                        
                        scored_segments.sort(key=lambda x: x[0], reverse=True)
                        excerpts = [content for score, content in scored_segments[:4]]
                        
                        if excerpts:
                            excerpt_text = "\n\n• ".join(excerpts)
                            ai_response = (
                                "I am currently having some trouble connecting to the server, but I have searched your document locally. "
                                f"Here is what I found in **'{doc_filenames_str}'**:\n\n"
                                f"• {excerpt_text}"
                            )
                            source = "document"
                        else:
                            ai_response = (
                                "I am having trouble connecting right now. "
                                f"Here is a summary of the document **'{doc_filenames_str}'**:\n\n"
                                f"{doc.summary}"
                            )
                            source = "knowledge"
                    except Exception as parse_err:
                        print(f"Fallback text extraction failed: {parse_err}")
                        ai_response = (
                            "I am having trouble connecting right now. "
                            f"Here is a summary of the document **'{doc_filenames_str}'**:\n\n"
                            f"{doc.summary}"
                        )
                        source = "knowledge"
                else:
                    ai_response = router_response["text"]
            else:
                ai_response = router_response["text"]
            
        if not_found_prefix:
            ai_response = not_found_prefix + ai_response

    # Enforce response sanitizer
    from app.services.ai_router import clean_ai_phrases
    ai_response = clean_ai_phrases(ai_response)

    # 7. Save Assistant Message (with search_results_raw)
    import json
    db_assistant_msg = ChatMessage(
        role="assistant",
        content=ai_response,
        conversation_id=conv_id,
        document_id=conv.document_id,
        has_search=enable_search,
        source=source,
        search_results_raw=json.dumps(search_results) if search_results is not None else None
    )
    db.add(db_assistant_msg)
    db.commit()

    return ChatResponse(
        message_id=db_assistant_msg.id,
        response=ai_response,
        search_results=search_results,
        has_search=enable_search,
        source=source
    )
