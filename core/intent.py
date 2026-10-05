import re
from typing import Dict, Any, Tuple

MODES = {
    "general": {
        "id": "general",
        "name": "General Assistant",
        "icon": "sparkles",
        "color": "indigo",
        "description": "General conversational AI for broad Q&A, reasoning, and everyday assistance.",
        "system_prompt": (
            "You are an Intelligent Multi-Functional AI Chatbot, an advanced conversational assistant. "
            "Provide helpful, accurate, well-formatted, and concise answers. Use markdown formatting with bullet points, "
            "bold text, and structured sections where appropriate."
        )
    },
    "study": {
        "id": "study",
        "name": "Study Assistance",
        "icon": "book-open",
        "color": "blue",
        "description": "Academic tutor for explaining complex concepts, generating quizzes, study guides, and flashcards.",
        "system_prompt": (
            "You are an expert Academic Tutor and Study Assistant. Your goal is to help students learn effectively. "
            "Break down complex concepts into simple, intuitive explanations using analogies, bullet points, "
            "examples, and key takeaways. Offer quick review quizzes or flashcard-style summaries when helpful."
        )
    },
    "coding": {
        "id": "coding",
        "name": "Coding Assistance",
        "icon": "code",
        "color": "emerald",
        "description": "Programming assistant for writing, debugging, explaining, and optimizing code in any language.",
        "system_prompt": (
            "You are a Senior Software Engineer and Coding Assistant. "
            "Provide clean, efficient, well-commented code. Always wrap code blocks with their respective language tag (e.g. ```python, ```javascript, ```cpp, ```html). "
            "Explain how the code works step-by-step, discuss time/space complexity if relevant, and offer best practices or edge cases."
        )
    },
    "math": {
        "id": "math",
        "name": "Basic Problem Solving & Math",
        "icon": "calculator",
        "color": "amber",
        "description": "Step-by-step solver for arithmetic, algebra, calculus, logic problems, and word equations with LaTeX rendering.",
        "system_prompt": (
            "You are an expert Mathematician and Problem Solver. "
            "Provide step-by-step mathematical solutions and logical deduction. Format mathematical formulas clearly using LaTeX delimiters: "
            "use single dollar signs for inline math (e.g., $x^2 + y^2 = r^2$) and double dollar signs for block equations (e.g., $$\\int_{0}^{\\infty} e^{-x^2} dx = \\frac{\\sqrt{\\pi}}{2}$$). "
            "State the given problem, identify knowns/unknowns, show each intermediate step with rationale, and clearly highlight the final answer."
        )
    },
    "summary": {
        "id": "summary",
        "name": "Text Summarization",
        "icon": "file-text",
        "color": "cyan",
        "description": "Summarize long articles, research papers, reports, or text into concise key points or briefs.",
        "system_prompt": (
            "You are an expert Summarizer and Information Synthesizer. "
            "Extract the core message, key insights, and actionable takeaways from the provided text. "
            "Structure your output with: 1) One-sentence TL;DR, 2) Key Highlights (bullet points), 3) Detailed Takeaways."
        )
    },
    "translate": {
        "id": "translate",
        "name": "Translation & Multilingual",
        "icon": "languages",
        "color": "violet",
        "description": "Accurate multilingual translation across 30+ languages with pronunciation and context notes.",
        "system_prompt": (
            "You are a Professional Polyglot Translator and Linguist. "
            "Translate the text accurately preserving tone, idiom, and cultural nuances. "
            "Provide: 1) The exact translation, 2) Phonetic/Pronunciation guide (if helpful), 3) Key vocabulary or contextual notes."
        )
    },
    "content": {
        "id": "content",
        "name": "Content Creation & Text Generation",
        "icon": "pen-tool",
        "color": "pink",
        "description": "Creative & professional writer for essays, emails, cover letters, blog posts, and stories.",
        "system_prompt": (
            "You are a Professional Writer and Creative Copywriter. "
            "Craft engaging, well-structured, and persuasive content tailored to the user's requested tone (professional, casual, creative, academic). "
            "Include catchy headlines, clear structure, smooth transitions, and a compelling call-to-action when appropriate."
        )
    },
    "vision": {
        "id": "vision",
        "name": "Image Understanding & Vision",
        "icon": "image",
        "color": "teal",
        "description": "Visual analysis, OCR, chart interpretation, and question-answering for uploaded images.",
        "system_prompt": (
            "You are a Multimodal AI Vision Assistant. "
            "Analyze the attached image in detail. Describe visual elements, identify objects, extract any legible text, "
            "explain charts or diagrams, and answer any specific user questions regarding the image thoroughly."
        )
    },
    "document": {
        "id": "document",
        "name": "Document Interaction & Q&A",
        "icon": "file-search",
        "color": "orange",
        "description": "Document analysis, search, and Q&A over uploaded PDFs, Word documents, text files, and datasets.",
        "system_prompt": (
            "You are a Document Analysis Assistant. "
            "Answer questions strictly and accurately based on the provided document context. "
            "Cite relevant sections or quotes when answering, and state clearly if the document does not contain the requested information."
        )
    },
    "recommendation": {
        "id": "recommendation",
        "name": "Smart Recommendations",
        "icon": "compass",
        "color": "rose",
        "description": "Personalized suggestions for books, courses, career paths, software tools, and productivity hacks.",
        "system_prompt": (
            "You are an Intelligent Recommendation Advisor. "
            "Provide curated, personalized recommendations based on the user's preferences, goals, and experience level. "
            "For each recommendation, explain Why it's recommended, Key Benefits, and who it is best for."
        )
    }
}

# Mode aliases for flexibility
MODE_ALIASES = {
    "problem_solving": "math",
    "math_solver": "math",
    "image": "vision",
    "image_understanding": "vision",
    "text_generation": "content",
    "content_creation": "content",
    "text_summarization": "summary",
    "coding_assistance": "coding",
    "study_assistance": "study"
}

def resolve_mode(mode: str) -> str:
    """Resolves mode name or alias to canonical ID."""
    m = (mode or "general").lower().strip()
    return MODE_ALIASES.get(m, m if m in MODES else "general")

def detect_intent(query: str, has_image: bool = False, has_document: bool = False) -> Tuple[str, float]:
    """
    Intelligently analyzes the user's natural language query and context to identify the best mode.
    Returns (mode_id, confidence).
    """
    if has_image:
        return "vision", 0.99
    if has_document:
        return "document", 0.95

    q = query.lower().strip()
    
    # 1. Vision / Image queries
    vision_patterns = [
        r'\b(in this image|in the image|in this photo|in the picture|look at this image|analyze this picture|what is in this image|extract text from image)\b'
    ]
    for pat in vision_patterns:
        if re.search(pat, q, re.IGNORECASE):
            return "vision", 0.95

    # 2. Math & Problem solving patterns
    math_patterns = [
        r'\b(solve|calculate|evaluate|derivative|integral|integrate|differentiate|algebra|matrix|equation|quadratic|limit|polynomial|arithmetic)\b',
        r'[\d\w\s]+(\+|\-|\*|\/|\^|\=)[\d\w\s]+(\=|\?)?',
        r'\\(frac|sqrt|int|sum|prod|alpha|beta|theta|pi)',
        r'\bsin\(|\bcos\(|\btan\(|\blog\(|\bln\(',
        r'find the value of [a-z]',
        r'\b(word problem|math problem|problem solving|logic puzzle|step-by-step solution)\b'
    ]
    for pat in math_patterns:
        if re.search(pat, q, re.IGNORECASE):
            return "math", 0.9

    # 3. Coding patterns
    coding_patterns = [
        r'```',
        r'\b(code|function|debug|script|python|javascript|typescript|c\+\+|java|html|css|sql|rust|go|algorithm|syntax error|bug|exception|regex|api endpoint)\b',
        r'\bdef\s+\w+\(|\bclass\s+\w+|\bconst\s+\w+\s*=|import\s+\w+|#include\s+<',
        r'write a (program|script|function|class|method|component)',
        r'fix (this|the) (error|bug|issue|code)'
    ]
    for pat in coding_patterns:
        if re.search(pat, q, re.IGNORECASE):
            return "coding", 0.9

    # 4. Translation patterns
    translation_patterns = [
        r'\b(translate|translation|how do you say|how to say)\b',
        r'\binto\s+(spanish|french|german|hindi|italian|japanese|chinese|russian|arabic|portuguese|korean|tamil|telugu|bengali|marathi|dutch|swedish|latin)\b',
        r'\bin\s+(spanish|french|german|hindi|italian|japanese|chinese|russian|arabic|portuguese|korean|tamil|telugu|bengali|marathi|dutch|swedish|latin)\b'
    ]
    for pat in translation_patterns:
        if re.search(pat, q, re.IGNORECASE):
            return "translate", 0.95

    # 5. Summarization patterns
    summary_patterns = [
        r'\b(summarize|summary|tl;?dr|sum up|condense|bullet points of|brief overview|key takeaways of)\b',
        r'give me a summary'
    ]
    for pat in summary_patterns:
        if re.search(pat, q, re.IGNORECASE):
            return "summary", 0.9

    # 6. Study assistance patterns
    study_patterns = [
        r'\b(explain concept|quiz me|make a quiz|flashcards|study guide|exam prep|teach me|how does .* work|physics|chemistry|biology|history of|quantum computing|mitosis|meiosis)\b',
        r'help me study',
        r'explain .* (to|like|for)',
        r'\b(teach me|tutor me|study tips|how to learn)\b'
    ]
    for pat in study_patterns:
        if re.search(pat, q, re.IGNORECASE):
            return "study", 0.85

    # 7. Content generation patterns
    content_patterns = [
        r'\b(write|draft|compose|generate|create)\s+(?:an?|the)?\s*(?:professional|casual|creative)?\s*(?:a\s+)?(letter|email|cover letter|essay|story|poem|blog|post|article|speech|script|bio|linkedin|resume|proposal|announcement)\b',
        r'\b(cover letter|essay writing|blog outline|creative writing|write an essay|draft a|content creation|text generation)\b'
    ]
    for pat in content_patterns:
        if re.search(pat, q, re.IGNORECASE):
            return "content", 0.9

    # 8. Recommendations patterns
    rec_patterns = [
        r'\b(recommend|suggest|what are the best|top \d+|best books|best movies|best tools|what should i learn|which is better .* or .*)\b',
        r'give me suggestions'
    ]
    for pat in rec_patterns:
        if re.search(pat, q, re.IGNORECASE):
            return "recommendation", 0.85

    # Default to general assistant
    return "general", 0.5

def get_system_prompt_for_mode(mode: str, extra_context: str = "") -> str:
    """Gets the tuned system prompt for a mode."""
    mode_id = resolve_mode(mode)
    mode_info = MODES.get(mode_id, MODES["general"])
    prompt = mode_info["system_prompt"]
    if extra_context:
        prompt += f"\n\nAdditional Context / Instructions:\n{extra_context}"
    return prompt
