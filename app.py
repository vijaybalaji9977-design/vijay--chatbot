import json
import time
import uuid
from typing import Optional, List
from fastapi import FastAPI, UploadFile, File, Form, HTTPException, Request
from fastapi.responses import HTMLResponse, StreamingResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
from pathlib import Path

from core.config import APP_TITLE, APP_VERSION, APP_DESCRIPTION, BASE_DIR, ALLOWED_IMAGE_EXTENSIONS
from core.database import (
    init_db,
    create_conversation,
    get_conversations,
    get_conversation,
    update_conversation_title,
    update_conversation_mode,
    delete_conversation,
    clear_all_conversations,
    add_message,
    get_messages,
    save_feedback,
    get_feedback_stats
)
from core.models import (
    ChatRequest,
    FeedbackRequest,
    ConversationCreate,
    ConversationUpdate,
    SettingsTestRequest
)
from core.intent import MODES, detect_intent, resolve_mode, get_system_prompt_for_mode
from services.llm_service import llm_service
from services.document_service import document_service
from services.image_service import image_service

# Initialize database schema
init_db()

# Create FastAPI app
app = FastAPI(
    title=APP_TITLE,
    version=APP_VERSION,
    description=APP_DESCRIPTION
)

# Enable CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

STATIC_DIR = BASE_DIR / "static"
STATIC_DIR.mkdir(parents=True, exist_ok=True)
(STATIC_DIR / "css").mkdir(parents=True, exist_ok=True)
(STATIC_DIR / "js").mkdir(parents=True, exist_ok=True)

# Mount static files
app.mount("/static", StaticFiles(directory=str(STATIC_DIR)), name="static")

@app.get("/", response_class=HTMLResponse)
async def read_index():
    index_file = STATIC_DIR / "index.html"
    if index_file.exists():
        return HTMLResponse(content=index_file.read_text(encoding="utf-8"))
    return HTMLResponse("<h1>AI-Powered Multi-Functional Chatbot is loading...</h1>")

@app.get("/api/health")
async def health_check():
    return {
        "status": "healthy",
        "app": APP_TITLE,
        "version": APP_VERSION,
        "database": "sqlite_ready",
        "features": [
            "general_qa", "text_generation", "text_summarization",
            "translation", "coding_assistance", "study_assistance",
            "problem_solving", "image_understanding", "document_interaction"
        ]
    }

@app.get("/api/modes")
async def get_modes():
    """Returns all supported AI functional modes and metadata."""
    return {"modes": list(MODES.values())}

# CONVERSATION ENDPOINTS
@app.get("/api/conversations")
async def list_conversations():
    return {"conversations": get_conversations()}

@app.post("/api/conversations")
async def new_conversation(req: ConversationCreate):
    conv = create_conversation(title=req.title or "New Conversation", mode=resolve_mode(req.mode or "general"))
    return conv

@app.get("/api/conversations/{conv_id}")
async def get_conv(conv_id: str):
    conv = get_conversation(conv_id)
    if not conv:
        raise HTTPException(status_code=404, detail="Conversation not found")
    messages = get_messages(conv_id)
    return {"conversation": conv, "messages": messages}

@app.put("/api/conversations/{conv_id}")
async def update_conv(conv_id: str, req: ConversationUpdate):
    success = update_conversation_title(conv_id, req.title)
    if not success:
        raise HTTPException(status_code=404, detail="Conversation not found")
    return {"status": "updated", "id": conv_id, "title": req.title}

@app.delete("/api/conversations/{conv_id}")
async def delete_conv(conv_id: str):
    success = delete_conversation(conv_id)
    if not success:
        raise HTTPException(status_code=404, detail="Conversation not found")
    return {"status": "deleted", "id": conv_id}

@app.delete("/api/conversations")
async def delete_all_convs():
    clear_all_conversations()
    return {"status": "cleared"}

# CHAT ENDPOINTS
@app.post("/api/chat")
async def chat(req: ChatRequest):
    """
    Main Chat Endpoint:
    - Intent auto-detection
    - Multimodal image processing & inspection
    - Document context injection
    - Multi-turn conversation persistence
    """
    conv_id = req.conversation_id or str(uuid.uuid4())
    has_image = bool(req.image_data)
    has_doc = bool(req.document_id)
    
    # 1. Determine active mode & intent
    resolved_mode = resolve_mode(req.mode)
    detected_intent_info = None
    if not req.mode or req.mode == "auto":
        detected_mode, confidence = detect_intent(req.message, has_image=has_image, has_document=has_doc)
        resolved_mode = detected_mode
        detected_intent_info = {"detected_mode": detected_mode, "confidence": confidence}

    # 2. Extract Document Context if document attached
    doc_context = ""
    if req.document_id:
        doc_context = document_service.get_document_context(req.document_id) or ""
        if resolved_mode != "vision":
            resolved_mode = "document"

    # 3. Process Image if attached
    img_metadata = None
    if req.image_data:
        processed_img = image_service.process_base64_image(req.image_data, req.image_filename or "upload.png")
        img_metadata = {
            "image_id": processed_img["id"],
            "image_data_url": processed_img["data_url"],
            "image_base64": processed_img["base64_data"],
            "image_mime": processed_img["mime_type"],
            "image_analysis": processed_img["offline_analysis"],
            "image_filename": req.image_filename or "image.png"
        }
        resolved_mode = "vision"

    # 4. Store User Message
    user_msg_meta = {}
    if req.document_id:
        user_msg_meta["document_id"] = req.document_id
    if img_metadata:
        user_msg_meta["image_data_url"] = img_metadata["image_data_url"]
        user_msg_meta["image_filename"] = img_metadata["image_filename"]

    user_msg = add_message(
        conversation_id=conv_id,
        role="user",
        content=req.message,
        mode=resolved_mode,
        metadata=user_msg_meta if user_msg_meta else None
    )

    # 5. Assemble Multi-Turn History
    past_messages = get_messages(conv_id, limit=10)
    history = [{"role": m["role"], "content": m["content"]} for m in past_messages]

    # 6. Build System Prompt & Extra Context
    extra_instructions = ""
    if req.document_id and doc_context:
        extra_instructions += f"\n--- Attached Document Context ---\n{doc_context[:4000]}\n--- End of Document Context ---"
    if req.target_language and resolved_mode == "translate":
        extra_instructions += f"\nTarget Translation Language: {req.target_language}"
    if req.summary_length and resolved_mode == "summary":
        extra_instructions += f"\nDesired Summary Length: {req.summary_length}"
    if img_metadata:
        extra_instructions += f"\n--- Attached Image Inspection ---\n{img_metadata['image_analysis']}\n--- End of Image Inspection ---"

    system_prompt = get_system_prompt_for_mode(resolved_mode, extra_instructions)

    # 7. Generate Assistant Response
    metadata = {
        "target_language": req.target_language,
        "summary_length": req.summary_length,
        "document_context": doc_context
    }
    if img_metadata:
        metadata.update(img_metadata)
    
    llm_res = await llm_service.generate_response(
        messages=history,
        system_prompt=system_prompt,
        mode=resolved_mode,
        provider=req.provider,
        api_key=req.api_key,
        model=req.model,
        temperature=req.temperature or 0.7,
        metadata=metadata
    )

    # 8. Store Assistant Message
    assistant_msg = add_message(
        conversation_id=conv_id,
        role="assistant",
        content=llm_res["text"],
        mode=resolved_mode,
        model=llm_res["model"],
        latency_ms=llm_res["latency_ms"],
        metadata={"provider": llm_res.get("provider"), "intent": detected_intent_info}
    )

    return {
        "conversation_id": conv_id,
        "user_message": user_msg,
        "assistant_message": assistant_msg,
        "mode": resolved_mode,
        "detected_intent": detected_intent_info,
        "latency_ms": llm_res["latency_ms"],
        "model": llm_res["model"]
    }

@app.post("/api/chat/stream")
async def chat_stream(req: ChatRequest):
    """
    Streaming Chat Endpoint using Server-Sent Events (SSE).
    """
    conv_id = req.conversation_id or str(uuid.uuid4())
    has_image = bool(req.image_data)
    has_doc = bool(req.document_id)
    
    resolved_mode = resolve_mode(req.mode)
    if not req.mode or req.mode == "auto":
        detected_mode, _ = detect_intent(req.message, has_image=has_image, has_document=has_doc)
        resolved_mode = detected_mode

    # Document Context
    doc_context = ""
    if req.document_id:
        doc_context = document_service.get_document_context(req.document_id) or ""
        if resolved_mode != "vision":
            resolved_mode = "document"

    # Image Context
    img_metadata = None
    if req.image_data:
        processed_img = image_service.process_base64_image(req.image_data, req.image_filename or "upload.png")
        img_metadata = {
            "image_id": processed_img["id"],
            "image_data_url": processed_img["data_url"],
            "image_base64": processed_img["base64_data"],
            "image_mime": processed_img["mime_type"],
            "image_analysis": processed_img["offline_analysis"],
            "image_filename": req.image_filename or "image.png"
        }
        resolved_mode = "vision"

    # Store User Message
    user_msg_meta = {}
    if req.document_id:
        user_msg_meta["document_id"] = req.document_id
    if img_metadata:
        user_msg_meta["image_data_url"] = img_metadata["image_data_url"]
        user_msg_meta["image_filename"] = img_metadata["image_filename"]

    add_message(
        conversation_id=conv_id,
        role="user",
        content=req.message,
        mode=resolved_mode,
        metadata=user_msg_meta if user_msg_meta else None
    )

    # History
    past_messages = get_messages(conv_id, limit=10)
    history = [{"role": m["role"], "content": m["content"]} for m in past_messages]

    # System Prompt
    extra_instructions = ""
    if req.document_id and doc_context:
        extra_instructions += f"\n--- Attached Document Context ---\n{doc_context[:4000]}\n--- End of Document Context ---"
    if req.target_language and resolved_mode == "translate":
        extra_instructions += f"\nTarget Translation Language: {req.target_language}"
    if img_metadata:
        extra_instructions += f"\n--- Attached Image Inspection ---\n{img_metadata['image_analysis']}\n--- End of Image Inspection ---"

    system_prompt = get_system_prompt_for_mode(resolved_mode, extra_instructions)

    metadata = {
        "target_language": req.target_language,
        "summary_length": req.summary_length,
        "document_context": doc_context
    }
    if img_metadata:
        metadata.update(img_metadata)

    async def event_generator():
        yield f"data: {json.dumps({'conversation_id': conv_id, 'mode': resolved_mode, 'start': True})}\n\n"
        
        full_content = []
        async for sse_event in llm_service.stream_response(
            messages=history,
            system_prompt=system_prompt,
            mode=resolved_mode,
            provider=req.provider,
            api_key=req.api_key,
            model=req.model,
            temperature=req.temperature or 0.7,
            metadata=metadata
        ):
            if sse_event.startswith("data: "):
                try:
                    payload = json.loads(sse_event[6:].strip())
                    if payload.get("chunk"):
                        full_content.append(payload["chunk"])
                except Exception:
                    pass
            yield sse_event

        final_text = "".join(full_content)
        if final_text:
            add_message(
                conversation_id=conv_id,
                role="assistant",
                content=final_text,
                mode=resolved_mode,
                model=req.model or "default"
            )

    return StreamingResponse(event_generator(), media_type="text/event-stream")

# FEEDBACK ENDPOINTS
@app.post("/api/feedback")
async def post_feedback(req: FeedbackRequest):
    saved = save_feedback(
        conversation_id=req.conversation_id,
        message_id=req.message_id,
        rating=req.rating,
        comment=req.comment,
        mode=req.mode
    )
    return {"status": "saved", "feedback": saved}

@app.get("/api/feedback/stats")
async def feedback_stats():
    return get_feedback_stats()

# FILE & IMAGE UPLOAD ENDPOINTS
@app.post("/api/upload")
async def upload_file(file: UploadFile = File(...)):
    content_bytes = await file.read()
    filename = file.filename or "upload.dat"
    ext = Path(filename).suffix.lower()

    # If it is an image file
    if ext in ALLOWED_IMAGE_EXTENSIONS:
        img_info = image_service.process_image_bytes(filename, content_bytes)
        return {
            "status": "uploaded",
            "type": "image",
            "image": {
                "id": img_info["id"],
                "filename": img_info["filename"],
                "data_url": img_info["data_url"],
                "width": img_info["width"],
                "height": img_info["height"],
                "size": img_info["size"],
                "analysis": img_info["offline_analysis"]
            }
        }
    else:
        # Document file (PDF, DOCX, TXT, CSV, etc.)
        doc_info = await document_service.process_file(filename, content_bytes)
        return {
            "status": "uploaded",
            "type": "document",
            "document": doc_info
        }

@app.post("/api/upload/image")
async def upload_image(file: UploadFile = File(...)):
    content_bytes = await file.read()
    filename = file.filename or "image.png"
    img_info = image_service.process_image_bytes(filename, content_bytes)
    return {
        "status": "uploaded",
        "image": {
            "id": img_info["id"],
            "filename": img_info["filename"],
            "data_url": img_info["data_url"],
            "width": img_info["width"],
            "height": img_info["height"],
            "size": img_info["size"],
            "analysis": img_info["offline_analysis"]
        }
    }

@app.get("/api/documents")
async def list_docs():
    return {"documents": document_service.list_documents()}

@app.delete("/api/documents/{doc_id}")
async def delete_doc(doc_id: str):
    success = document_service.remove_document(doc_id)
    if not success:
        raise HTTPException(status_code=404, detail="Document not found")
    return {"status": "deleted", "id": doc_id}

# SETTINGS TEST ENDPOINT
@app.post("/api/settings/test")
async def test_settings(req: SettingsTestRequest):
    test_msg = [{"role": "user", "content": "Respond with 'API Connection Successful!'"}]
    res = await llm_service.generate_response(
        messages=test_msg,
        system_prompt="You are a test validator.",
        provider=req.provider,
        api_key=req.api_key,
        model=req.model,
        mode="general"
    )
    return {"status": "success", "response": res}
