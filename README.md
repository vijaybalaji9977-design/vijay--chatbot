# 🤖 AI-Powered Multi-Functional Chatbot

An intelligent conversational system designed to interact with users in a simple, natural, and user-friendly manner. The platform unifies multiple modern AI capabilities into a single, cohesive, responsive web application.

---

## 📄 Abstract

> The **AI-Powered Multi-Functional Chatbot** is an intelligent conversational system designed to interact with users in a simple, natural, and user-friendly manner. The main objective of this project is to develop a chatbot with multiple features similar to modern AI assistants, allowing users to perform different tasks through a single platform.
>
> The proposed chatbot can understand user queries and generate relevant responses using Artificial Intelligence and Natural Language Processing (NLP). It provides multiple options such as **general question answering, text generation, text summarization, translation, coding assistance, study assistance, content creation, and basic problem solving**. The system can also maintain the context of a conversation to provide more meaningful responses.
>
> The chatbot is designed with an easy-to-use interface where users can enter their questions and receive responses instantly. Additional features such as **chat history, new chat, copy response, regenerate response, clear conversation, and different task modes** can be included to improve the user experience.
>
> The system can be developed using technologies such as **Python, NLP, Machine Learning, APIs, HTML, CSS, and JavaScript**. The chatbot can be further enhanced with features such as **voice input and output, document/file interaction, image understanding, personalized responses, and multilingual support**.
>
> Overall, this project aims to create a **single intelligent platform for communication, learning, coding, content creation, and everyday assistance**, providing users with a flexible chatbot experience similar to modern AI conversational systems.

---

## 📌 Core Functional Modes

| Mode | Icon | Category | Core Capabilities |
| :--- | :---: | :--- | :--- |
| **General Assistant** | 🧠 | General Q&A | Everyday knowledge Q&A, reasoning, logic, planning, and multi-turn conversations. |
| **Study Assistance** | 📚 | Academic Tutor | Complex concept explanations, flashcards, active recall schedules, and custom quizzes. |
| **Coding Assistance** | 💻 | Software Engineering | Code generation, syntax explanations, bug fixing, time/space complexity, syntax highlighting & one-click copy. |
| **Problem Solving** | 📐 | Math & Computational Solver | Step-by-step calculus (derivatives, integrals), algebraic equations ($ax^2 + bx + c = 0$), arithmetic, and KaTeX LaTeX rendering powered by SymPy. |
| **Image Understanding** | 🖼️ | Multimodal Vision | Upload or paste (Ctrl+V) images (.png, .jpg, .webp); scene inspection, text/OCR extraction, and chart reasoning via Gemini / GPT-4o Vision and offline image inspector. |
| **Text Summarization** | 📝 | Information Synthesizer | Executive summaries, bullet points, TL;DRs, and adjustable summary lengths. |
| **Translation** | 🌐 | Multilingual Engine | Polyglot translations across 30+ languages with pronunciation guidance and grammar notes. |
| **Content Creation** | ✍️ | Creative & Professional Writing | Professional emails, cover letters, essays, LinkedIn posts, blog drafts, and storytelling. |
| **Document Interaction** | 📄 | Document Ingestion & Q&A | Upload PDF, DOCX, TXT, CSV, JSON, or code files; text extraction, document search, and grounded Q&A. |
| **Smart Recommendations**| 💡 | Personalized Recommender | Curated suggestions for books, tech stacks, career roadmaps, tools, and productivity workflows. |

---

## 🚀 Key Interactive Innovations

1. **Auto-Intent Detection**: Intelligently analyzes natural language queries, uploaded attachments, and equations to automatically activate the optimal mode.
2. **🖼️ Multimodal Image Understanding**:
   - Drag & drop, file picker, or direct clipboard paste (`Ctrl+V`).
   - Image thumbnail preview with expand modal.
   - Dual multimodal vision: Cloud models (Gemini / GPT-4o) + built-in offline image property inspector.
3. **🎙️ Voice Input and Output**:
   - **Speech-to-Text (STT)**: Real-time microphone dictation with visual sound wave feedback.
   - **Text-to-Speech (TTS)**: Natural voice reader with voice selector, rate control, and auto-speak toggle.
4. **📄 Document & File Ingestion**:
   - Direct parsing for `.pdf` (PyPDF), `.docx` (python-docx), `.txt`, `.csv`, `.json`, `.py`, `.js`, `.html`, `.cpp`, `.sql`, etc.
   - Grounded context injection and document preview modal.
5. **💬 Session & History Management**:
   - Persistent SQLite conversation database.
   - Real-time conversation search, renaming, deletion, and one-click export to Markdown (`.md`) or JSON (`.json`).
   - **New Chat** button and **Clear History** wiping.
6. **🔄 Response Actions**:
   - **Copy Response**: Instant clipboard copying with feedback.
   - **Regenerate Response**: Re-run the last prompt seamlessly.
   - **Feedback Collection**: Response rating (thumbs up / thumbs down) stored in database analytics.
7. **⚡ Dual AI Engine**:
   - **Cloud Models**: Google Gemini (Flash, Pro, 2.0), OpenAI (GPT-4o), Groq (Llama 3.3/3.1), OpenRouter configured via Settings modal.
   - **Built-in Offline Intelligent Engine**: Zero-API-key fallback powered by SymPy, NLP heuristics, and rule-based generators.
8. **🎨 Modern Glassmorphic UI**:
   - Dark and Light mode themes with instant persistence.
   - KaTeX LaTeX math rendering ($$...$$ and $...$).
   - Highlight.js syntax highlighting with copyable code headers.

---

## 🛠️ Quick Start

### 1. Requirements
- Python 3.10+ (tested on Python 3.12)
- Modern web browser (Chrome, Edge, Firefox, Safari)

### 2. Launch
Double-click `run.bat` or run in terminal:
```bash
# 1. Install dependencies
pip install -r requirements.txt

# 2. Start server
python -m uvicorn app:app --host 127.0.0.1 --port 8000 --reload
```

### 3. Access Web UI
Open your browser and navigate to:
```
http://127.0.0.1:8000
```

---

## 🧪 Automated Testing

Run the automated verification suite:
```bash
python test_chatbot.py
# or with pytest:
pytest test_chatbot.py
```

All 7 test suites verify:
- Health check & mode registry
- Intent classification across all categories
- SymPy symbolic math solver
- Document upload and extraction
- Image processing and multimodal vision
- Chat, multi-turn history & feedback
- Frontend static delivery

---

## ⚙️ Configuration & API Keys

- Click the **Settings ⚙️** icon in the top right to configure:
  - **AI Provider**: Offline Engine, Google Gemini, OpenAI, Groq, OpenRouter
  - **API Key**: Saved securely in browser `localStorage`
  - **Model Name**: e.g., `gemini-1.5-flash`, `gpt-4o-mini`, `llama-3.1-70b-versatile`
  - **Creativity Temperature**: (0.0 to 1.0)
  - **TTS Voice & Speech Rate**: Customize speech output
- You can also set `GEMINI_API_KEY`, `OPENAI_API_KEY`, or `GROQ_API_KEY` in a `.env` file (see `.env.example`).

---

## 📂 Project Architecture

```
c:\vijay chatbotnew\
├── app.py                 # FastAPI server & REST API endpoints
├── requirements.txt       # Dependencies (FastAPI, Uvicorn, Pillow, SymPy, PyPDF, python-docx, etc.)
├── .env.example           # Environment template
├── run.bat                # Windows quick launcher
├── README.md              # Project documentation
├── ABSTRACT.md            # Project abstract
├── test_chatbot.py        # Automated test suite
├── core/
│   ├── config.py          # App configurations, directories, & paths
│   ├── database.py        # SQLite schema & CRUD operations
│   ├── models.py          # Pydantic data schemas
│   └── intent.py          # Intent classification & system prompts
├── services/
│   ├── llm_service.py     # Gemini / OpenAI / Groq multi-provider service (Multimodal)
│   ├── offline_engine.py  # SymPy math solver & offline NLP fallback
│   ├── document_service.py# PDF & DOCX text file parsing / extraction
│   └── image_service.py   # Pillow image validation, base64 encoding & vision inspection
└── static/
    ├── index.html         # Responsive SPA layout
    ├── css/
    │   └── styles.css     # Glassmorphism, KaTeX & animations
    └── js/
        ├── app.js         # State controller, KaTeX, Marked.js, feedback, regenerate
        ├── presets.js     # Mode definitions & prompt chips
        ├── voice.js       # Speech-to-Text & Text-to-Speech manager
        ├── document.js    # File drag-and-drop & attachment manager
        └── image.js       # Image upload, drag-and-drop, clipboard paste, & thumbnail manager
```
[Open Chatbot](https://accessories-skilled-pray-season.trycloudflare.com)


