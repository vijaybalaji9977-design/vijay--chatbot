class DocumentManager {
    constructor() {
        this.activeDocument = null;
        this.initEventListeners();
    }

    initEventListeners() {
        const fileInput = document.getElementById("fileInput");
        if (fileInput) {
            fileInput.addEventListener("change", (e) => this.handleFileSelect(e));
        }

        // Drag and drop on drop zone
        const dropZone = document.getElementById("chatContainer");
        if (dropZone) {
            dropZone.addEventListener("dragover", (e) => {
                e.preventDefault();
                dropZone.classList.add("border-2", "border-dashed", "border-indigo-500");
            });

            dropZone.addEventListener("dragleave", () => {
                dropZone.classList.remove("border-2", "border-dashed", "border-indigo-500");
            });

            dropZone.addEventListener("drop", (e) => {
                e.preventDefault();
                dropZone.classList.remove("border-2", "border-dashed", "border-indigo-500");
                if (e.dataTransfer.files && e.dataTransfer.files.length > 0) {
                    this.uploadFile(e.dataTransfer.files[0]);
                }
            });
        }
    }

    async handleFileSelect(event) {
        const file = event.target.files[0];
        if (file) {
            await this.uploadFile(file);
        }
        event.target.value = ""; // Reset input
    }

    async uploadFile(file) {
        const uploadToast = document.getElementById("uploadToast");
        if (uploadToast) {
            uploadToast.classList.remove("hidden");
            uploadToast.textContent = `Uploading ${file.name}...`;
        }

        const formData = new FormData();
        formData.append("file", file);

        try {
            const res = await fetch("/api/upload", {
                method: "POST",
                body: formData
            });

            if (!res.ok) throw new Error("Upload failed");
            const data = await res.json();
            
            this.setActiveDocument(data.document);
            if (uploadToast) {
                uploadToast.textContent = `Attached ${file.name} successfully!`;
                setTimeout(() => uploadToast.classList.add("hidden"), 3000);
            }
        } catch (err) {
            console.error("Upload error:", err);
            if (uploadToast) {
                uploadToast.textContent = `Upload failed: ${err.message}`;
                setTimeout(() => uploadToast.classList.add("hidden"), 4000);
            }
        }
    }

    setActiveDocument(doc) {
        this.activeDocument = doc;
        const badge = document.getElementById("activeDocBadge");
        const nameEl = document.getElementById("activeDocName");
        const previewEl = document.getElementById("activeDocChars");

        if (badge && nameEl) {
            nameEl.textContent = doc.filename;
            if (previewEl) previewEl.textContent = `${(doc.size / 1024).toFixed(1)} KB • ${doc.char_count} chars`;
            badge.classList.remove("hidden");
        }

        // Switch active mode to Document Assistance
        if (window.chatApp) {
            window.chatApp.setMode("document");
        }
    }

    clearActiveDocument() {
        this.activeDocument = null;
        const badge = document.getElementById("activeDocBadge");
        if (badge) badge.classList.add("hidden");
    }

    showDocumentPreview() {
        if (!this.activeDocument) return;
        const modal = document.getElementById("docPreviewModal");
        const title = document.getElementById("docModalTitle");
        const body = document.getElementById("docModalBody");

        if (modal && title && body) {
            title.textContent = this.activeDocument.filename;
            body.textContent = this.activeDocument.content || this.activeDocument.preview;
            modal.classList.remove("hidden");
        }
    }

    hideDocumentPreview() {
        const modal = document.getElementById("docPreviewModal");
        if (modal) modal.classList.add("hidden");
    }
}

const documentManager = new DocumentManager();
