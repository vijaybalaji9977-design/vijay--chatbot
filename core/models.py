from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any

class MessageModel(BaseModel):
    id: Optional[str] = None
    role: str  # 'user', 'assistant', 'system'
    content: str
    mode: Optional[str] = "general"
    timestamp: Optional[str] = None
    metadata: Optional[Dict[str, Any]] = None

class ChatRequest(BaseModel):
    conversation_id: Optional[str] = None
    message: str
    mode: Optional[str] = "auto"
    target_language: Optional[str] = "Spanish"
    summary_length: Optional[str] = "medium"
    stream: Optional[bool] = True
    document_id: Optional[str] = None
    image_data: Optional[str] = None      # Base64 string or data:image/...;base64,...
    image_filename: Optional[str] = None
    api_key: Optional[str] = None
    provider: Optional[str] = None        # 'gemini', 'openai', 'groq', 'openrouter', 'offline'
    model: Optional[str] = None
    temperature: Optional[float] = 0.7

class FeedbackRequest(BaseModel):
    conversation_id: str
    message_id: str
    rating: int  # 1 for thumbs up, -1 for thumbs down, 0 for neutral
    comment: Optional[str] = None
    mode: Optional[str] = None

class ConversationCreate(BaseModel):
    title: Optional[str] = "New Conversation"
    mode: Optional[str] = "general"

class ConversationUpdate(BaseModel):
    title: str

class SettingsTestRequest(BaseModel):
    provider: str
    api_key: str
    model: Optional[str] = None

class DocumentInfo(BaseModel):
    id: str
    filename: str
    file_type: str
    size: int
    char_count: int
    preview: str
    created_at: str

class ImageInfo(BaseModel):
    id: str
    filename: str
    file_type: str
    width: int
    height: int
    size: int
    data_url: str
    analysis: Optional[str] = None
    created_at: str
