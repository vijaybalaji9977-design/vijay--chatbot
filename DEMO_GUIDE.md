# 🎯 Live Presentation & Demonstration Guide

This guide provides a step-by-step walkthrough for demonstrating all features of the **AI-Powered Multi-Functional Chatbot** during an evaluation, presentation, or portfolio demo.

---

## 🛠️ Step 0: Pre-Demo Preparation

1. **Launch the Server:**
   - Double-click `run.bat` in `C:\vijay chatbotnew\`, **OR**
   - In PowerShell:
     ```powershell
     python -m uvicorn app:app --host 127.0.0.1 --port 8000 --reload
     ```
2. **Open the Web Browser:**
   - Navigate to: **`http://localhost:8000`**
3. **Toggle Theme:**
   - Click the Sun/Moon icon in the top header to show Dark and Light mode transitions.

---

## 📌 Demonstration Steps

### Demo 1: Auto-Intent Detection & General Q&A
- **Action:** Leave the mode on **General** or click a suggestion chip on the welcome screen.
- **Sample Query:** `Explain how solar panels work in simple terms`
- **What to Highlight:**
  - Notice the instant response and clean formatting with bullet points.
  - The mode automatically displays in the header and message header.

---

### Demo 2: Basic Problem Solving & Mathematics (SymPy + KaTeX)
- **Action:** Switch to the **Problem Solving** pill, or simply type a math problem in the input box.
- **Sample Query 1:** `solve x^2 - 5x + 6 = 0`
- **Sample Query 2:** `differentiate x^3 + 4*x^2 - 7*x + 12 with respect to x`
- **What to Highlight:**
  - The computational engine is powered by **SymPy**.
  - All formulas render mathematically using **KaTeX** LaTeX formatting ($$x = 2, x = 3$$ and $$f'(x) = 3x^2 + 8x - 7$$).
  - Shows each intermediate mathematical step.

---

### Demo 3: Coding Assistance (Syntax Highlighting & One-Click Copy)
- **Action:** Click the **Coding** mode pill.
- **Sample Query:** `Write a python binary search algorithm with comments`
- **What to Highlight:**
  - Syntax highlighting powered by **Highlight.js** with language tags (`python`).
  - Click the **Copy** button in the code header; notice the button changes to a green checkmark saying *"Copied!"*.
  - Time and space complexity analysis ($\mathcal{O}(\log n)$) included.

---

### Demo 4: Study Assistance (Academic Tutor & Quizzes)
- **Action:** Click the **Study** mode pill.
- **Sample Query:** `Create a 5-question multiple choice quiz on World War II with answers`
- **What to Highlight:**
  - Structured academic concept breakdowns.
  - Interactive quiz formatting designed for active recall.

---

### Demo 5: Multimodal Image Understanding (Vision)
- **Action:** 
  1. Click the **Image icon (🖼️)** next to the input box, or drag-and-drop an image, or paste an image from your clipboard using `Ctrl+V`.
  2. Notice the thumbnail preview appears above the input box showing dimensions and file size.
  3. Click the thumbnail to open the full-screen image expansion modal.
- **Sample Query:** `Analyze this image and explain what is shown`
- **What to Highlight:**
  - Image thumbnail persists directly inside the user chat bubble.
  - Structured visual analysis detailing resolution, aspect ratio, orientation, and color tone.
  - Multimodal vision reasoning ready for online models (Gemini / GPT-4o).

---

### Demo 6: Document Interaction & Grounded Q&A (PDF & DOCX)
- **Action:**
  1. Click the **Paperclip icon (📎)**.
  2. Select any `.pdf`, `.docx`, or `.txt` file (e.g. from your notes or project files).
  3. Notice the active document badge showing filename, size, and character count.
  4. Click **Preview** to inspect the extracted text.
- **Sample Query:** `Summarize the main points discussed in this document`
- **What to Highlight:**
  - Native document parsing via `pypdf` and `python-docx`.
  - Context grounding ensures the chatbot answers directly from the attached document.

---

### Demo 7: Translation & Multilingual Support
- **Action:** Click the **Translate** mode pill.
- **Sample Query:** `Translate 'Welcome to our intelligent multi-functional chatbot' into Spanish, French, and Japanese`
- **What to Highlight:**
  - Polyglot translation across 30+ languages.
  - Pronunciation guidance and cultural context notes.

---

### Demo 8: Text Summarization
- **Action:** Click the **Summary** mode pill.
- **Sample Query:** `Summarize the advantages and ethical challenges of artificial intelligence into 3 executive bullet points`
- **What to Highlight:**
  - 1-sentence TL;DR followed by concise executive takeaways.

---

### Demo 9: Content Creation & Text Generation
- **Action:** Click the **Content** mode pill.
- **Sample Query:** `Draft a professional cover letter for a Senior Software Engineer position at a tech startup`
- **What to Highlight:**
  - Tone modulation, compelling structure, and call-to-action closing.

---

### Demo 10: Voice Input & Output (STT & TTS)
- **Action 1 (Voice Dictation):** Click the **Microphone 🎙️** button in the input bar. Speak a question aloud. Watch the pulsing red animation and live speech transcription into the text area.
- **Action 2 (Voice Reader):** Click the **Speaker 🔊** icon on any bot response. The browser speaks the response aloud using Web Speech Synthesis.
- **What to Highlight:**
  - Voice settings can be customized in the **Settings ⚙️** modal (voice selection, speech rate, auto-read toggle).

---

### Demo 11: Response Actions & Feedback
- **Action 1 (Copy Response):** Click the **Copy icon** at the bottom of any assistant message to copy the full markdown text.
- **Action 2 (Regenerate Response):** Click the **Regenerate icon (`↻`)** to re-run the previous query.
- **Action 3 (Feedback):** Click the **Thumbs Up 👍** or **Thumbs Down 👎** button. Open `http://localhost:8000/api/feedback/stats` to show the real-time feedback recorded in the SQLite database.

---

### Demo 12: Session Management & Export
- **Action 1 (New Chat):** Click the **+ New Chat** button in the sidebar to reset the view.
- **Action 2 (Search Chats):** Type in the sidebar search box to instantly filter conversation titles.
- **Action 3 (Rename & Delete):** Hover over a conversation to rename its title or delete it.
- **Action 4 (Export):** Click the **Download icon** in the top navigation bar to export the conversation as **Markdown (`.md`)** or **JSON (`.json`)**.

---

### Demo 13: Settings & Dual Engine Verification
- **Action:** Click the **Settings ⚙️** icon in the top right.
- **What to Highlight:**
  - Show the **AI Provider selector**: Built-in Offline Engine, Google Gemini, OpenAI, Groq, OpenRouter.
  - Click **Test Connection** to validate API keys in real time.
  - Explain how the built-in offline engine guarantees the application functions with 100% uptime even without an internet connection or API keys.
