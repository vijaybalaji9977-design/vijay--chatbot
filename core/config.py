import os
from pathlib import Path
from dotenv import load_dotenv

# Load environment variables from .env if present
load_dotenv()

BASE_DIR = Path(__file__).resolve().parent.parent
DATA_DIR = BASE_DIR / "data"
UPLOADS_DIR = DATA_DIR / "uploads"
IMAGES_DIR = DATA_DIR / "images"
DB_PATH = DATA_DIR / "chatbot.db"

# Ensure required directories exist
DATA_DIR.mkdir(parents=True, exist_ok=True)
UPLOADS_DIR.mkdir(parents=True, exist_ok=True)
IMAGES_DIR.mkdir(parents=True, exist_ok=True)

# Default LLM configurations
DEFAULT_PROVIDER = os.getenv("DEFAULT_PROVIDER", "gemini")
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY", "")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", "")
GROQ_API_KEY = os.getenv("GROQ_API_KEY", "")

# Default Models
DEFAULT_GEMINI_MODEL = os.getenv("DEFAULT_GEMINI_MODEL", "gemini-1.5-flash")
DEFAULT_OPENAI_MODEL = os.getenv("DEFAULT_OPENAI_MODEL", "gpt-4o-mini")
DEFAULT_GROQ_MODEL = os.getenv("DEFAULT_GROQ_MODEL", "llama-3.1-70b-versatile")

# Application Settings
APP_TITLE = "Intelligent Multi-Functional AI Chatbot"
APP_VERSION = "2.0.0"
APP_DESCRIPTION = (
    "An advanced multi-functional conversational AI platform for Q&A, study, coding, math, "
    "translation, summarization, content, documents, image understanding, and recommendations."
)

ALLOWED_IMAGE_EXTENSIONS = {".png", ".jpg", ".jpeg", ".webp", ".gif", ".bmp"}
ALLOWED_DOC_EXTENSIONS = {
    ".pdf", ".docx", ".txt", ".md", ".csv", ".json", ".py", ".js", 
    ".html", ".css", ".cpp", ".c", ".java", ".sql", ".xml", ".yaml", ".yml", ".log"
}
