class VoiceManager {
    constructor() {
        this.recognition = null;
        this.isListening = false;
        this.synth = window.speechSynthesis;
        this.currentUtterance = null;
        this.autoReadEnabled = false;
        this.selectedVoice = null;
        this.voices = [];

        this.initSpeechRecognition();
        this.initSpeechSynthesis();
    }

    initSpeechRecognition() {
        const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition;
        if (!SpeechRecognition) {
            console.warn("Speech Recognition not supported in this browser.");
            return;
        }

        this.recognition = new SpeechRecognition();
        this.recognition.continuous = false;
        this.recognition.interimResults = true;
        this.recognition.lang = "en-US";

        this.recognition.onstart = () => {
            this.isListening = true;
            this.updateMicUI(true);
        };

        this.recognition.onresult = (event) => {
            let interimTranscript = '';
            let finalTranscript = '';

            for (let i = event.resultIndex; i < event.results.length; ++i) {
                if (event.results[i].isFinal) {
                    finalTranscript += event.results[i][0].transcript;
                } else {
                    interimTranscript += event.results[i][0].transcript;
                }
            }

            const inputEl = document.getElementById("messageInput");
            if (inputEl) {
                if (finalTranscript) {
                    inputEl.value = (inputEl.value + " " + finalTranscript).trim();
                } else if (interimTranscript) {
                    // Show live interim in placeholder or input temporarily
                    inputEl.setAttribute("placeholder", "🎙️ Listening: " + interimTranscript);
                }
            }
        };

        this.recognition.onerror = (event) => {
            console.error("Speech Recognition Error:", event.error);
            this.stopListening();
        };

        this.recognition.onend = () => {
            this.stopListening();
        };
    }

    initSpeechSynthesis() {
        if (!this.synth) return;

        const populateVoices = () => {
            this.voices = this.synth.getVoices();
            const voiceSelect = document.getElementById("voiceSelect");
            if (voiceSelect && this.voices.length > 0) {
                voiceSelect.innerHTML = "";
                this.voices.forEach((v, i) => {
                    const opt = document.createElement("option");
                    opt.value = i;
                    opt.textContent = `${v.name} (${v.lang})`;
                    if (v.default || v.lang.includes("en-US") || v.name.includes("Google") || v.name.includes("Natural")) {
                        opt.selected = true;
                        this.selectedVoice = v;
                    }
                    voiceSelect.appendChild(opt);
                });
            }
        };

        populateVoices();
        if (speechSynthesis.onvoiceschanged !== undefined) {
            speechSynthesis.onvoiceschanged = populateVoices;
        }
    }

    toggleListening() {
        if (!this.recognition) {
            alert("Speech recognition is not supported in this browser. Please use Chrome, Edge, or Safari.");
            return;
        }

        if (this.isListening) {
            this.stopListening();
        } else {
            try {
                this.recognition.start();
            } catch (e) {
                console.error("Start speech error:", e);
                this.stopListening();
            }
        }
    }

    stopListening() {
        this.isListening = false;
        this.updateMicUI(false);
        const inputEl = document.getElementById("messageInput");
        if (inputEl) {
            inputEl.setAttribute("placeholder", "Ask anything, enter code, math equation, or attach a document...");
        }
        if (this.recognition) {
            try { this.recognition.stop(); } catch (e) {}
        }
    }

    updateMicUI(listening) {
        const micBtn = document.getElementById("voiceInputBtn");
        const micIcon = document.getElementById("micIcon");
        const liveIndicator = document.getElementById("voiceLiveIndicator");

        if (listening) {
            if (micBtn) {
                micBtn.classList.add("bg-red-500", "text-white", "animate-pulse");
                micBtn.classList.remove("text-gray-500", "dark:text-gray-400", "hover:bg-gray-100", "dark:hover:bg-gray-700");
            }
            if (liveIndicator) liveIndicator.classList.remove("hidden");
        } else {
            if (micBtn) {
                micBtn.classList.remove("bg-red-500", "text-white", "animate-pulse");
                micBtn.classList.add("text-gray-500", "dark:text-gray-400", "hover:bg-gray-100", "dark:hover:bg-gray-700");
            }
            if (liveIndicator) liveIndicator.classList.add("hidden");
        }
    }

    speak(text, btnElement = null) {
        if (!this.synth) return;

        // Clean markdown and LaTeX tags for natural speech
        const cleanText = text
            .replace(/```[\s\S]*?```/g, "Code block omitted.")
            .replace(/\$\$[\s\S]*?\$\$/g, "Mathematical equation.")
            .replace(/\$([^\$]+)\$/g, "$1")
            .replace(/[#*`_~\[\]\(\)>]/g, "")
            .trim();

        if (this.synth.speaking) {
            this.synth.cancel();
            if (btnElement) {
                btnElement.innerHTML = '<i class="fa-solid fa-volume-high"></i>';
            }
            return;
        }

        const utterance = new SpeechSynthesisUtterance(cleanText);
        
        // Resolve voice
        const voiceSelect = document.getElementById("voiceSelect");
        if (voiceSelect && this.voices[voiceSelect.value]) {
            utterance.voice = this.voices[voiceSelect.value];
        } else if (this.selectedVoice) {
            utterance.voice = this.selectedVoice;
        }

        const rateInput = document.getElementById("voiceRate");
        if (rateInput) utterance.rate = parseFloat(rateInput.value) || 1.0;

        if (btnElement) {
            btnElement.innerHTML = '<i class="fa-solid fa-stop text-red-500 animate-pulse"></i>';
        }

        utterance.onend = () => {
            if (btnElement) {
                btnElement.innerHTML = '<i class="fa-solid fa-volume-high"></i>';
            }
        };

        utterance.onerror = () => {
            if (btnElement) {
                btnElement.innerHTML = '<i class="fa-solid fa-volume-high"></i>';
            }
        };

        this.synth.speak(utterance);
    }
}

const voiceManager = new VoiceManager();
