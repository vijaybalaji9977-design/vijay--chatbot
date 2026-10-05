const APP_MODES = {
    general: {
        id: "general",
        name: "General Assistant",
        icon: "fa-sparkles",
        color: "from-indigo-500 to-purple-600",
        badge: "bg-indigo-100 text-indigo-800 dark:bg-indigo-900/40 dark:text-indigo-300 border-indigo-200 dark:border-indigo-800",
        description: "General conversational AI for broad Q&A, reasoning, and everyday assistance.",
        prompts: [
            "Explain the theory of relativity in simple terms",
            "What are 5 creative morning habits for high productivity?",
            "How do solar panels convert sunlight into electricity?",
            "Give me a 3-day travel itinerary for Kyoto, Japan"
        ]
    },
    study: {
        id: "study",
        name: "Study Assistance",
        icon: "fa-graduation-cap",
        color: "from-blue-500 to-cyan-600",
        badge: "bg-blue-100 text-blue-800 dark:bg-blue-900/40 dark:text-blue-300 border-blue-200 dark:border-blue-800",
        description: "Academic tutor for concept breakdowns, flashcards, active recall schedules, and review quizzes.",
        prompts: [
            "Explain the difference between mitosis and meiosis",
            "Create a 5-question multiple choice quiz on World War II with answers",
            "Give me an active recall study schedule for final exams",
            "Break down the concept of supply and demand with real-world analogies"
        ]
    },
    coding: {
        id: "coding",
        name: "Coding Assistance",
        icon: "fa-code",
        color: "from-emerald-500 to-teal-600",
        badge: "bg-emerald-100 text-emerald-800 dark:bg-emerald-900/40 dark:text-emerald-300 border-emerald-200 dark:border-emerald-800",
        description: "Write, debug, explain, and optimize code in Python, JavaScript, C++, Java, SQL, and more.",
        prompts: [
            "Write a Python script for binary search with explanatory comments",
            "How do I create a modern REST API endpoint in FastAPI?",
            "Explain how async/await works under the hood in JavaScript",
            "Write an optimized SQL query to find top 5 earning employees per department"
        ]
    },
    math: {
        id: "math",
        name: "Basic Problem Solving",
        icon: "fa-calculator",
        color: "from-amber-500 to-orange-600",
        badge: "bg-amber-100 text-amber-800 dark:bg-amber-900/40 dark:text-amber-300 border-amber-200 dark:border-amber-800",
        description: "Step-by-step solutions for algebra, calculus, arithmetic, and logic puzzles with LaTeX formulas.",
        prompts: [
            "Solve the quadratic equation x^2 - 5x + 6 = 0 step-by-step",
            "Calculate the derivative of x^3 + 4*x^2 - 7*x + 12",
            "Integrate 3*x^2 + 2*x + 5 with respect to x",
            "Evaluate sqrt(144) * 15 / 3"
        ]
    },
    summary: {
        id: "summary",
        name: "Text Summarization",
        icon: "fa-align-left",
        color: "from-cyan-500 to-blue-600",
        badge: "bg-cyan-100 text-cyan-800 dark:bg-cyan-900/40 dark:text-cyan-300 border-cyan-200 dark:border-cyan-800",
        description: "Condense long articles, reports, or text into executive bullet points and key takeaways.",
        prompts: [
            "Summarize the key advantages and ethical challenges of Artificial Intelligence",
            "Provide a 3-bullet executive summary of the attached document",
            "Condense this text into a concise 2-sentence TL;DR",
            "Extract the main action items from these meeting notes"
        ]
    },
    translate: {
        id: "translate",
        name: "Translation & Multilingual",
        icon: "fa-language",
        color: "from-purple-500 to-pink-600",
        badge: "bg-purple-100 text-purple-800 dark:bg-purple-900/40 dark:text-purple-300 border-purple-200 dark:border-purple-800",
        description: "Accurate translation across 30+ languages with pronunciation guides and grammar notes.",
        prompts: [
            "Translate 'Good morning, how can I help you today?' to Spanish and French",
            "Translate 'Welcome to our intelligent multi-functional chatbot platform' to Japanese",
            "Translate 'Thank you for your assistance' to Hindi, German, and Italian",
            "How do you say 'Where is the train station?' in German with pronunciation?"
        ]
    },
    content: {
        id: "content",
        name: "Content Creation & Generation",
        icon: "fa-feather-pointed",
        color: "from-pink-500 to-rose-600",
        badge: "bg-pink-100 text-pink-800 dark:bg-pink-900/40 dark:text-pink-300 border-pink-200 dark:border-pink-800",
        description: "Draft professional emails, essays, cover letters, social media posts, and creative stories.",
        prompts: [
            "Write a polite email asking a manager for quarterly project feedback",
            "Draft a compelling cover letter for a Senior Software Engineer position",
            "Create an engaging LinkedIn post announcing a new AI chatbot project",
            "Write a short creative sci-fi story about an autonomous Mars outpost"
        ]
    },
    vision: {
        id: "vision",
        name: "Image Understanding",
        icon: "fa-image",
        color: "from-teal-500 to-emerald-600",
        badge: "bg-teal-100 text-teal-800 dark:bg-teal-900/40 dark:text-teal-300 border-teal-200 dark:border-teal-800",
        description: "Multimodal visual reasoning, image description, OCR text extraction, and chart analysis.",
        prompts: [
            "Analyze and describe what is shown in this attached image",
            "Extract all text, numbers, and labels from this image",
            "Explain the architecture or chart illustrated in this diagram",
            "Solve the math equation or scientific diagram shown in the photo"
        ]
    },
    document: {
        id: "document",
        name: "Document Interaction",
        icon: "fa-file-lines",
        color: "from-orange-500 to-red-600",
        badge: "bg-orange-100 text-orange-800 dark:bg-orange-900/40 dark:text-orange-300 border-orange-200 dark:border-orange-800",
        description: "Analyze, search, and answer questions directly from attached PDFs, Word DOCX, and text files.",
        prompts: [
            "What are the main findings and conclusions in this document?",
            "List all key dates, names, and statistics mentioned in the file",
            "Explain section 2 of the attached report in simple terms",
            "Is there any mention of security protocols in this document?"
        ]
    },
    recommendation: {
        id: "recommendation",
        name: "Smart Recommendations",
        icon: "fa-compass",
        color: "from-rose-500 to-red-500",
        badge: "bg-rose-100 text-rose-800 dark:bg-rose-900/40 dark:text-rose-300 border-rose-200 dark:border-rose-800",
        description: "Personalized suggestions for books, courses, career roadmaps, software tools, and productivity workflows.",
        prompts: [
            "Recommend the best books for learning System Design & Architecture",
            "What are the top 5 productivity tools for developers in 2026?",
            "Suggest a beginner-to-advanced learning roadmap for Artificial Intelligence",
            "Recommend top sci-fi books exploring artificial general intelligence"
        ]
    }
};

const LANGUAGES_LIST = [
    "Spanish", "French", "German", "Hindi", "Japanese", "Chinese (Mandarin)", 
    "Italian", "Russian", "Arabic", "Portuguese", "Korean", "Tamil", "Telugu", 
    "Bengali", "Marathi", "Dutch", "Swedish", "Greek", "Turkish", "Polish"
];
