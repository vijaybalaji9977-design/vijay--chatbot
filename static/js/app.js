class ChatApp {
    constructor() {
        this.currentConversationId = null;
        this.currentMode = "general";
        this.isGenerating = false;
        this.conversations = [];
        this.messages = [];
        this.settings = {
            provider: localStorage.getItem("chatbot_provider") || "offline",
            apiKey: localStorage.getItem("chatbot_api_key") || "",
            model: localStorage.getItem("chatbot_model") || "gemini-1.5-flash",
            temperature: parseFloat(localStorage.getItem("chatbot_temperature")) || 0.7,
            autoRead: localStorage.getItem("chatbot_auto_read") === "true",
            theme: localStorage.getItem("chatbot_theme") || "dark"
        };

        this.initMarkdownAndMath();
        this.initTheme();
        this.initEventListeners();
        this.loadSettingsToUI();
        this.loadConversations();
        this.renderPromptChips();
    }

    initMarkdownAndMath() {
        // Configure Marked.js with custom code renderer
        if (window.marked) {
            const renderer = new marked.Renderer();
            
            renderer.code = function(code, language) {
                const lang = language || 'plaintext';
                let highlighted = code;
                if (window.hljs && hljs.getLanguage(lang)) {
                    try {
                        highlighted = hljs.highlight(code, { language: lang }).value;
                    } catch (e) {
                        highlighted = hljs.highlightAuto(code).value;
                    }
                } else if (window.hljs) {
                    highlighted = hljs.highlightAuto(code).value;
                }

                const encodedCode = encodeURIComponent(code);
                return `
                <div class="code-block-wrapper my-4 rounded-xl overflow-hidden border border-gray-700/60 bg-gray-950/80 shadow-md">
                    <div class="code-header flex items-center justify-between px-4 py-2 bg-gray-900 border-b border-gray-800 text-xs text-gray-400 font-mono">
                        <span class="font-semibold text-indigo-400 uppercase tracking-wider">${lang}</span>
                        <button onclick="window.chatApp.copyCode(this, '${encodedCode}')" class="copy-btn flex items-center gap-1.5 px-2.5 py-1 rounded bg-gray-800 hover:bg-gray-700 text-gray-300 hover:text-white transition">
                            <i class="fa-regular fa-copy"></i>
                            <span>Copy</span>
                        </button>
                    </div>
                    <pre class="p-4 overflow-x-auto text-sm text-gray-200 font-mono leading-relaxed"><code class="hljs language-${lang}">${highlighted}</code></pre>
                </div>`;
            };

            marked.setOptions({
                renderer: renderer,
                breaks: true,
                gfm: true
            });
        }
    }

    renderMath(element) {
        if (window.renderMathInElement) {
            try {
                renderMathInElement(element, {
                    delimiters: [
                        { left: "$$", right: "$$", display: true },
                        { left: "$", right: "$", display: false },
                        { left: "\\[", right: "\\]", display: true },
                        { left: "\\(", right: "\\)", display: false }
                    ],
                    throwOnError: false
                });
            } catch (e) {
                console.warn("KaTeX render error:", e);
            }
        }
    }

    initTheme() {
        const root = document.documentElement;
        if (this.settings.theme === "dark") {
            root.classList.add("dark");
        } else {
            root.classList.remove("dark");
        }
        this.updateThemeIcon();
    }

    toggleTheme() {
        const root = document.documentElement;
        if (root.classList.contains("dark")) {
            root.classList.remove("dark");
            this.settings.theme = "light";
        } else {
            root.classList.add("dark");
            this.settings.theme = "dark";
        }
        localStorage.setItem("chatbot_theme", this.settings.theme);
        this.updateThemeIcon();
    }

    updateThemeIcon() {
        const btn = document.getElementById("themeToggleBtn");
        if (btn) {
            btn.innerHTML = this.settings.theme === "dark" 
                ? '<i class="fa-solid fa-sun text-amber-400"></i>' 
                : '<i class="fa-solid fa-moon text-indigo-600"></i>';
        }
    }

    initEventListeners() {
        // Send button and input keypress
        const sendBtn = document.getElementById("sendBtn");
        const msgInput = document.getElementById("messageInput");

        if (sendBtn) {
            sendBtn.addEventListener("click", () => this.sendMessage());
        }

        if (msgInput) {
            msgInput.addEventListener("keydown", (e) => {
                if (e.key === "Enter" && !e.shiftKey) {
                    e.preventDefault();
                    this.sendMessage();
                }
            });
            // Auto resize textarea
            msgInput.addEventListener("input", () => {
                msgInput.style.height = "auto";
                msgInput.style.height = Math.min(msgInput.scrollHeight, 180) + "px";
            });
        }

        // New Chat button
        const newChatBtn = document.getElementById("newChatBtn");
        if (newChatBtn) {
            newChatBtn.addEventListener("click", () => this.createNewConversation());
        }

        // Clear all chats button
        const clearAllBtn = document.getElementById("clearAllBtn");
        if (clearAllBtn) {
            clearAllBtn.addEventListener("click", () => this.clearAllConversations());
        }

        // Theme toggle
        const themeBtn = document.getElementById("themeToggleBtn");
        if (themeBtn) {
            themeBtn.addEventListener("click", () => this.toggleTheme());
        }

        // Voice input mic
        const micBtn = document.getElementById("voiceInputBtn");
        if (micBtn) {
            micBtn.addEventListener("click", () => voiceManager.toggleListening());
        }

        // Mode tabs / pills
        document.querySelectorAll(".mode-pill").forEach(pill => {
            pill.addEventListener("click", (e) => {
                const mode = pill.getAttribute("data-mode");
                this.setMode(mode);
            });
        });

        // Search conversations input
        const searchInput = document.getElementById("searchConvInput");
        if (searchInput) {
            searchInput.addEventListener("input", (e) => this.filterConversations(e.target.value));
        }

        // Settings save button
        const saveSettingsBtn = document.getElementById("saveSettingsBtn");
        if (saveSettingsBtn) {
            saveSettingsBtn.addEventListener("click", () => this.saveSettings());
        }

        // Test API button
        const testApiBtn = document.getElementById("testApiBtn");
        if (testApiBtn) {
            testApiBtn.addEventListener("click", () => this.testApiConnection());
        }

        // Mobile sidebar toggles
        const sidebarToggle = document.getElementById("sidebarToggleBtn");
        const sidebarClose = document.getElementById("sidebarCloseBtn");
        const sidebar = document.getElementById("sidebar");

        if (sidebarToggle && sidebar) {
            sidebarToggle.addEventListener("click", () => {
                sidebar.classList.toggle("-translate-x-full");
            });
        }
        if (sidebarClose && sidebar) {
            sidebarClose.addEventListener("click", () => {
                sidebar.classList.add("-translate-x-full");
            });
        }
    }

    setMode(mode) {
        if (!APP_MODES[mode]) mode = "general";
        this.currentMode = mode;

        // Update UI pill active states
        document.querySelectorAll(".mode-pill").forEach(pill => {
            const m = pill.getAttribute("data-mode");
            if (m === mode) {
                pill.classList.add("bg-indigo-600", "text-white", "shadow-sm");
                pill.classList.remove("text-gray-600", "dark:text-gray-300", "hover:bg-gray-200", "dark:hover:bg-gray-800");
            } else {
                pill.classList.remove("bg-indigo-600", "text-white", "shadow-sm");
                pill.classList.add("text-gray-600", "dark:text-gray-300", "hover:bg-gray-200", "dark:hover:bg-gray-800");
            }
        });

        // Update Header Badge
        const activeBadge = document.getElementById("activeModeBadge");
        const modeInfo = APP_MODES[mode];
        if (activeBadge && modeInfo) {
            activeBadge.innerHTML = `<i class="fa-solid ${modeInfo.icon} mr-1.5"></i> ${modeInfo.name}`;
            activeBadge.className = `inline-flex items-center px-3 py-1 rounded-full text-xs font-semibold border ${modeInfo.badge} transition-all duration-300`;
        }

        // Update Mode Description in welcome screen
        const descEl = document.getElementById("welcomeModeDesc");
        if (descEl && modeInfo) {
            descEl.textContent = modeInfo.description;
        }

        this.renderPromptChips();
    }

    renderPromptChips() {
        const container = document.getElementById("promptChipsContainer");
        if (!container) return;

        const modeInfo = APP_MODES[this.currentMode] || APP_MODES["general"];
        container.innerHTML = "";

        modeInfo.prompts.forEach(prompt => {
            const chip = document.createElement("button");
            chip.className = "text-left p-3.5 rounded-xl border border-gray-200/80 dark:border-gray-800 bg-white/70 dark:bg-gray-800/60 hover:border-indigo-500 dark:hover:border-indigo-500 hover:shadow-md transition-all group backdrop-blur-sm";
            chip.innerHTML = `
                <div class="flex items-start gap-2.5">
                    <span class="p-1.5 rounded-lg bg-indigo-50 dark:bg-indigo-950/50 text-indigo-600 dark:text-indigo-400 group-hover:scale-110 transition-transform">
                        <i class="fa-solid ${modeInfo.icon} text-xs"></i>
                    </span>
                    <span class="text-xs font-medium text-gray-700 dark:text-gray-300 group-hover:text-indigo-600 dark:group-hover:text-indigo-400 leading-snug">${prompt}</span>
                </div>
            `;
            chip.addEventListener("click", () => {
                const input = document.getElementById("messageInput");
                if (input) {
                    input.value = prompt;
                    this.sendMessage();
                }
            });
            container.appendChild(chip);
        });
    }

    async loadConversations() {
        try {
            const res = await fetch("/api/conversations");
            const data = await res.json();
            this.conversations = data.conversations || [];
            this.renderConversationsList();
        } catch (e) {
            console.error("Load conversations error:", e);
        }
    }

    renderConversationsList(filter = "") {
        const list = document.getElementById("conversationsList");
        if (!list) return;
        list.innerHTML = "";

        const filtered = this.conversations.filter(c => 
            c.title.toLowerCase().includes(filter.toLowerCase())
        );

        if (filtered.length === 0) {
            list.innerHTML = `<div class="text-center py-6 text-xs text-gray-400">No conversations found</div>`;
            return;
        }

        filtered.forEach(c => {
            const item = document.createElement("div");
            const isActive = c.id === this.currentConversationId;
            item.className = `group flex items-center justify-between p-2.5 rounded-xl text-xs font-medium cursor-pointer transition ${
                isActive 
                    ? "bg-indigo-50 dark:bg-indigo-900/30 text-indigo-700 dark:text-indigo-300 border border-indigo-200/60 dark:border-indigo-800/60" 
                    : "text-gray-700 dark:text-gray-300 hover:bg-gray-100 dark:hover:bg-gray-800/70"
            }`;

            item.innerHTML = `
                <div class="flex items-center gap-2.5 overflow-hidden flex-1" onclick="window.chatApp.selectConversation('${c.id}')">
                    <i class="fa-regular fa-message text-gray-400 group-hover:text-indigo-500"></i>
                    <span class="truncate title-text">${c.title}</span>
                </div>
                <div class="flex items-center gap-1 opacity-0 group-hover:opacity-100 transition-opacity">
                    <button onclick="event.stopPropagation(); window.chatApp.renameConversation('${c.id}')" title="Rename" class="p-1 hover:text-indigo-600 rounded">
                        <i class="fa-regular fa-pen-to-square"></i>
                    </button>
                    <button onclick="event.stopPropagation(); window.chatApp.deleteConversation('${c.id}')" title="Delete" class="p-1 hover:text-red-500 rounded">
                        <i class="fa-regular fa-trash-can"></i>
                    </button>
                </div>
            `;
            list.appendChild(item);
        });
    }

    filterConversations(query) {
        this.renderConversationsList(query);
    }

    async selectConversation(convId) {
        this.currentConversationId = convId;
        this.renderConversationsList();

        try {
            const res = await fetch(`/api/conversations/${convId}`);
            if (!res.ok) throw new Error("Conversation not found");
            const data = await res.json();
            
            this.messages = data.messages || [];
            this.renderMessages();

            if (data.conversation && data.conversation.mode) {
                this.setMode(data.conversation.mode);
            }
        } catch (e) {
            console.error("Select conversation error:", e);
        }
    }

    createNewConversation() {
        this.currentConversationId = null;
        this.messages = [];
        documentManager.clearActiveDocument();
        this.renderMessages();
        this.renderConversationsList();
        
        const input = document.getElementById("messageInput");
        if (input) {
            input.value = "";
            input.focus();
        }
    }

    async renameConversation(convId) {
        const conv = this.conversations.find(c => c.id === convId);
        const currentTitle = conv ? conv.title : "";
        const newTitle = prompt("Enter new title for this conversation:", currentTitle);
        if (newTitle && newTitle.trim() && newTitle !== currentTitle) {
            try {
                await fetch(`/api/conversations/${convId}`, {
                    method: "PUT",
                    headers: { "Content-Type": "application/json" },
                    body: JSON.stringify({ title: newTitle.trim() })
                });
                this.loadConversations();
            } catch (e) {
                console.error("Rename conversation error:", e);
            }
        }
    }

    async deleteConversation(convId) {
        if (!confirm("Are you sure you want to delete this conversation?")) return;
        try {
            await fetch(`/api/conversations/${convId}`, { method: "DELETE" });
            if (this.currentConversationId === convId) {
                this.createNewConversation();
            }
            this.loadConversations();
        } catch (e) {
            console.error("Delete conversation error:", e);
        }
    }

    async clearAllConversations() {
        if (!confirm("Are you sure you want to delete ALL conversations? This cannot be undone.")) return;
        try {
            await fetch("/api/conversations", { method: "DELETE" });
            this.createNewConversation();
            this.loadConversations();
        } catch (e) {
            console.error("Clear all error:", e);
        }
    }

    renderMessages() {
        const welcomeScreen = document.getElementById("welcomeScreen");
        const messagesList = document.getElementById("messagesList");
        if (!messagesList) return;

        if (this.messages.length === 0) {
            if (welcomeScreen) welcomeScreen.classList.remove("hidden");
            messagesList.classList.add("hidden");
            messagesList.innerHTML = "";
            return;
        }

        if (welcomeScreen) welcomeScreen.classList.add("hidden");
        messagesList.classList.remove("hidden");
        messagesList.innerHTML = "";

        this.messages.forEach(msg => {
            this.appendMessageToUI(msg);
        });

        this.scrollToBottom();
    }

    appendMessageToUI(msg) {
        const messagesList = document.getElementById("messagesList");
        if (!messagesList) return;

        const isUser = msg.role === "user";
        const msgDiv = document.createElement("div");
        msgDiv.id = `msg-${msg.id || Date.now()}`;
        msgDiv.className = `flex gap-4 p-4 rounded-2xl transition-all ${
            isUser 
                ? "bg-gray-100/80 dark:bg-gray-800/50 border border-gray-200/50 dark:border-gray-700/40 ml-12" 
                : "bg-white dark:bg-gray-900 border border-gray-200/80 dark:border-gray-800 shadow-sm mr-12"
        }`;

        const avatar = isUser
            ? `<div class="w-8 h-8 rounded-full bg-gradient-to-tr from-indigo-500 to-purple-600 text-white flex items-center justify-center font-bold text-xs shadow-sm flex-shrink-0">U</div>`
            : `<div class="w-8 h-8 rounded-full bg-gradient-to-tr from-indigo-600 to-pink-500 text-white flex items-center justify-center text-xs shadow-sm flex-shrink-0"><i class="fa-solid fa-sparkles"></i></div>`;

        // Render Markdown content
        const rawContent = msg.content || "";
        const formattedHtml = isUser ? this.escapeHtml(rawContent) : (window.marked ? marked.parse(rawContent) : rawContent);

        // Check for attached image
        let imageHtml = "";
        const imgUrl = (msg.metadata && msg.metadata.image_data_url) || msg.image_data_url;
        if (imgUrl) {
            imageHtml = `
                <div class="mb-3">
                    <img src="${imgUrl}" alt="Attached Image" class="max-w-xs max-h-56 rounded-xl object-contain border border-gray-200 dark:border-gray-700 shadow-sm cursor-pointer hover:opacity-95 transition" onclick="imageManager.showImageModal(this.src, 'Attached Image')">
                </div>
            `;
        }

        // Assistant action toolbar (Copy, Regenerate, Voice TTS, Thumbs Up/Down)
        let actionsHtml = "";
        if (!isUser) {
            const encodedForSpeech = encodeURIComponent(rawContent);
            actionsHtml = `
                <div class="flex items-center gap-3 mt-3 pt-2.5 border-t border-gray-100 dark:border-gray-800/80 text-xs text-gray-400">
                    <button onclick="window.chatApp.copyText(this, '${encodedForSpeech}')" title="Copy response" class="hover:text-indigo-600 dark:hover:text-indigo-400 transition flex items-center gap-1">
                        <i class="fa-regular fa-copy"></i>
                    </button>
                    <button onclick="window.chatApp.regenerateLastResponse()" title="Regenerate response" class="hover:text-indigo-600 dark:hover:text-indigo-400 transition flex items-center gap-1">
                        <i class="fa-solid fa-rotate-right"></i>
                    </button>
                    <button onclick="voiceManager.speak(decodeURIComponent('${encodedForSpeech}'), this)" title="Read aloud" class="hover:text-indigo-600 dark:hover:text-indigo-400 transition flex items-center gap-1">
                        <i class="fa-solid fa-volume-high"></i>
                    </button>
                    <button onclick="window.chatApp.sendFeedback('${msg.id}', 1, this)" title="Thumbs up" class="feedback-up hover:text-emerald-500 transition">
                        <i class="fa-regular fa-thumbs-up"></i>
                    </button>
                    <button onclick="window.chatApp.sendFeedback('${msg.id}', -1, this)" title="Thumbs down" class="feedback-down hover:text-red-500 transition">
                        <i class="fa-regular fa-thumbs-down"></i>
                    </button>
                    ${msg.model ? `<span class="ml-auto text-[10px] font-mono text-gray-400 bg-gray-100 dark:bg-gray-800 px-2 py-0.5 rounded-full">${msg.model}</span>` : ""}
                </div>
            `;
        }

        msgDiv.innerHTML = `
            ${avatar}
            <div class="flex-1 overflow-hidden min-w-0">
                <div class="flex items-center justify-between mb-1.5">
                    <span class="text-xs font-semibold text-gray-800 dark:text-gray-200">${isUser ? "You" : "AI Assistant"}</span>
                    ${msg.mode ? `<span class="text-[10px] font-medium text-gray-400 uppercase tracking-wider">${msg.mode}</span>` : ""}
                </div>
                ${imageHtml}
                <div class="prose prose-sm dark:prose-invert max-w-none text-gray-800 dark:text-gray-200 leading-relaxed message-body">${formattedHtml}</div>
                ${actionsHtml}
            </div>
        `;

        messagesList.appendChild(msgDiv);
        this.renderMath(msgDiv);
    }

    async sendMessage() {
        if (this.isGenerating) return;

        const inputEl = document.getElementById("messageInput");
        const messageText = inputEl ? inputEl.value.trim() : "";
        
        const activeImage = imageManager.getActiveImage();
        const activeDoc = documentManager.activeDocument;

        if (!messageText && !activeImage && !activeDoc) return;

        // Reset input box
        if (inputEl) {
            inputEl.value = "";
            inputEl.style.height = "auto";
        }

        const docId = activeDoc ? activeDoc.id : null;
        const imageDataUrl = activeImage ? activeImage.data_url : null;
        const imageFilename = activeImage ? activeImage.filename : null;

        if (activeImage) {
            imageManager.clearActiveImage();
        }

        // Hide welcome screen
        const welcomeScreen = document.getElementById("welcomeScreen");
        const messagesList = document.getElementById("messagesList");
        if (welcomeScreen) welcomeScreen.classList.add("hidden");
        if (messagesList) messagesList.classList.remove("hidden");

        // Append user message locally
        const userMsg = {
            id: "user-" + Date.now(),
            role: "user",
            content: messageText || (imageDataUrl ? "Analyze this uploaded image." : "Inspect document."),
            mode: this.currentMode,
            metadata: imageDataUrl ? { image_data_url: imageDataUrl, image_filename: imageFilename } : {}
        };
        this.messages.push(userMsg);
        this.appendMessageToUI(userMsg);
        this.scrollToBottom();

        // Create temporary bot placeholder with typing indicator
        const tempBotId = "temp-" + Date.now();
        const placeholderMsg = {
            id: tempBotId,
            role: "assistant",
            content: '<div class="flex items-center gap-1.5 py-1 text-gray-400"><div class="w-2 h-2 rounded-full bg-indigo-500 animate-bounce"></div><div class="w-2 h-2 rounded-full bg-indigo-500 animate-bounce [animation-delay:0.2s]"></div><div class="w-2 h-2 rounded-full bg-indigo-500 animate-bounce [animation-delay:0.4s]"></div><span class="text-xs ml-2">Thinking...</span></div>',
            mode: this.currentMode
        };
        this.appendMessageToUI(placeholderMsg);
        this.scrollToBottom();

        this.isGenerating = true;
        this.setSendButtonState(true);

        const payload = {
            conversation_id: this.currentConversationId,
            message: userMsg.content,
            mode: this.currentMode,
            document_id: docId,
            image_data: imageDataUrl,
            image_filename: imageFilename,
            provider: this.settings.provider,
            api_key: this.settings.apiKey,
            model: this.settings.model,
            temperature: this.settings.temperature
        };

        try {
            const res = await fetch("/api/chat", {
                method: "POST",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify(payload)
            });

            if (!res.ok) throw new Error(`Server returned ${res.status}`);
            const data = await res.json();

            this.currentConversationId = data.conversation_id;

            // Remove placeholder and append real assistant message
            const tempDiv = document.getElementById(`msg-${tempBotId}`);
            if (tempDiv) tempDiv.remove();

            const botMsg = data.assistant_message;
            this.messages.push(botMsg);
            this.appendMessageToUI(botMsg);
            this.scrollToBottom();

            // Auto voice read if enabled
            if (this.settings.autoRead) {
                voiceManager.speak(botMsg.content);
            }

            this.loadConversations();
        } catch (err) {
            console.error("Chat error:", err);
            const tempDiv = document.getElementById(`msg-${tempBotId}`);
            if (tempDiv) {
                tempDiv.querySelector(".message-body").innerHTML = `<span class="text-red-500">Error generating response: ${err.message}</span>`;
            }
        } finally {
            this.isGenerating = false;
            this.setSendButtonState(false);
        }
    }

    async regenerateLastResponse() {
        if (this.isGenerating || this.messages.length === 0) return;
        
        let lastUserIndex = -1;
        for (let i = this.messages.length - 1; i >= 0; i--) {
            if (this.messages[i].role === "user") {
                lastUserIndex = i;
                break;
            }
        }
        if (lastUserIndex === -1) return;

        const lastUserMsg = this.messages[lastUserIndex];
        
        // Remove trailing assistant message
        if (this.messages.length > lastUserIndex + 1) {
            const removed = this.messages.pop();
            const el = document.getElementById(`msg-${removed.id}`);
            if (el) el.remove();
        }

        const inputEl = document.getElementById("messageInput");
        if (inputEl) inputEl.value = lastUserMsg.content;

        if (lastUserMsg.metadata && lastUserMsg.metadata.image_data_url) {
            imageManager.setActiveImage({
                data_url: lastUserMsg.metadata.image_data_url,
                filename: lastUserMsg.metadata.image_filename || "image.png",
                size: 0,
                width: 800,
                height: 600
            });
        }

        // Remove user message from list because sendMessage will re-add
        this.messages.splice(lastUserIndex, 1);
        const userEl = document.getElementById(`msg-${lastUserMsg.id}`);
        if (userEl) userEl.remove();

        await this.sendMessage();
    }

    setSendButtonState(generating) {
        const sendBtn = document.getElementById("sendBtn");
        if (!sendBtn) return;
        if (generating) {
            sendBtn.innerHTML = '<i class="fa-solid fa-spinner fa-spin"></i>';
            sendBtn.disabled = true;
        } else {
            sendBtn.innerHTML = '<i class="fa-solid fa-arrow-up"></i>';
            sendBtn.disabled = false;
        }
    }

    async sendFeedback(messageId, rating, btn) {
        if (!this.currentConversationId || !messageId) return;
        try {
            await fetch("/api/feedback", {
                method: "POST",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify({
                    conversation_id: this.currentConversationId,
                    message_id: messageId,
                    rating: rating,
                    mode: this.currentMode
                })
            });

            // Visual feedback
            if (btn) {
                const parent = btn.parentElement;
                parent.querySelectorAll(".feedback-up, .feedback-down").forEach(b => b.classList.remove("text-emerald-500", "text-red-500"));
                if (rating === 1) btn.classList.add("text-emerald-500");
                else if (rating === -1) btn.classList.add("text-red-500");
            }
        } catch (e) {
            console.error("Feedback error:", e);
        }
    }

    copyText(btn, encodedText) {
        const text = decodeURIComponent(encodedText);
        navigator.clipboard.writeText(text).then(() => {
            const icon = btn.querySelector("i");
            if (icon) {
                icon.className = "fa-solid fa-check text-emerald-500";
                setTimeout(() => { icon.className = "fa-regular fa-copy"; }, 2000);
            }
        });
    }

    copyCode(btn, encodedCode) {
        const code = decodeURIComponent(encodedCode);
        navigator.clipboard.writeText(code).then(() => {
            const span = btn.querySelector("span");
            const icon = btn.querySelector("i");
            if (span) span.textContent = "Copied!";
            if (icon) icon.className = "fa-solid fa-check text-emerald-400";
            setTimeout(() => {
                if (span) span.textContent = "Copy";
                if (icon) icon.className = "fa-regular fa-copy";
            }, 2000);
        });
    }

    exportChat(format = "markdown") {
        if (this.messages.length === 0) {
            alert("No messages to export.");
            return;
        }

        let content = "";
        let filename = `chat_export_${Date.now()}`;

        if (format === "markdown") {
            filename += ".md";
            content = `# Conversation Export\nMode: ${this.currentMode}\nDate: ${new Date().toLocaleString()}\n\n---\n\n`;
            this.messages.forEach(m => {
                content += `### ${m.role === "user" ? "User" : "AI Assistant"}\n\n${m.content}\n\n---\n\n`;
            });
        } else if (format === "json") {
            filename += ".json";
            content = JSON.stringify({ conversation_id: this.currentConversationId, mode: this.currentMode, messages: this.messages }, null, 2);
        }

        const blob = new Blob([content], { type: "text/plain;charset=utf-8" });
        const url = URL.createObjectURL(blob);
        const a = document.createElement("a");
        a.href = url;
        a.download = filename;
        a.click();
        URL.revokeObjectURL(url);
    }

    loadSettingsToUI() {
        const providerSelect = document.getElementById("settingsProvider");
        const apiKeyInput = document.getElementById("settingsApiKey");
        const modelSelect = document.getElementById("settingsModel");
        const tempSlider = document.getElementById("settingsTemp");
        const tempVal = document.getElementById("settingsTempVal");
        const autoReadCheck = document.getElementById("settingsAutoRead");

        if (providerSelect) providerSelect.value = this.settings.provider;
        if (apiKeyInput) apiKeyInput.value = this.settings.apiKey;
        if (modelSelect) modelSelect.value = this.settings.model;
        if (tempSlider) {
            tempSlider.value = this.settings.temperature;
            if (tempVal) tempVal.textContent = this.settings.temperature;
            tempSlider.oninput = (e) => { if (tempVal) tempVal.textContent = e.target.value; };
        }
        if (autoReadCheck) autoReadCheck.checked = this.settings.autoRead;
    }

    saveSettings() {
        const providerSelect = document.getElementById("settingsProvider");
        const apiKeyInput = document.getElementById("settingsApiKey");
        const modelSelect = document.getElementById("settingsModel");
        const tempSlider = document.getElementById("settingsTemp");
        const autoReadCheck = document.getElementById("settingsAutoRead");

        if (providerSelect) this.settings.provider = providerSelect.value;
        if (apiKeyInput) this.settings.apiKey = apiKeyInput.value.trim();
        if (modelSelect) this.settings.model = modelSelect.value;
        if (tempSlider) this.settings.temperature = parseFloat(tempSlider.value);
        if (autoReadCheck) this.settings.autoRead = autoReadCheck.checked;

        localStorage.setItem("chatbot_provider", this.settings.provider);
        localStorage.setItem("chatbot_api_key", this.settings.apiKey);
        localStorage.setItem("chatbot_model", this.settings.model);
        localStorage.setItem("chatbot_temperature", this.settings.temperature.toString());
        localStorage.setItem("chatbot_auto_read", this.settings.autoRead.toString());

        this.hideSettingsModal();
        alert("Settings saved successfully!");
    }

    async testApiConnection() {
        const statusEl = document.getElementById("testApiStatus");
        const apiKeyInput = document.getElementById("settingsApiKey");
        const providerSelect = document.getElementById("settingsProvider");
        const modelSelect = document.getElementById("settingsModel");

        if (!statusEl) return;
        statusEl.className = "text-xs font-mono text-indigo-500 animate-pulse";
        statusEl.textContent = "Testing connection...";

        try {
            const res = await fetch("/api/settings/test", {
                method: "POST",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify({
                    provider: providerSelect ? providerSelect.value : "gemini",
                    api_key: apiKeyInput ? apiKeyInput.value.trim() : "",
                    model: modelSelect ? modelSelect.value : "gemini-1.5-flash"
                })
            });

            const data = await res.json();
            if (res.ok && data.status === "success") {
                statusEl.className = "text-xs font-mono text-emerald-500 font-semibold";
                statusEl.textContent = "✓ Connected Successfully!";
            } else {
                statusEl.className = "text-xs font-mono text-red-500";
                statusEl.textContent = "✗ Connection Failed";
            }
        } catch (e) {
            statusEl.className = "text-xs font-mono text-red-500";
            statusEl.textContent = `✗ Error: ${e.message}`;
        }
    }

    showSettingsModal() {
        const modal = document.getElementById("settingsModal");
        if (modal) modal.classList.remove("hidden");
    }

    hideSettingsModal() {
        const modal = document.getElementById("settingsModal");
        if (modal) modal.classList.add("hidden");
    }

    scrollToBottom() {
        const chatContainer = document.getElementById("chatContainer");
        if (chatContainer) {
            setTimeout(() => {
                chatContainer.scrollTop = chatContainer.scrollHeight;
            }, 50);
        }
    }

    escapeHtml(text) {
        const map = { '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;', "'": '&#039;' };
        return text.replace(/[&<>"']/g, (m) => map[m]);
    }
}

// Global initialization
window.addEventListener("DOMContentLoaded", () => {
    window.chatApp = new ChatApp();
});
