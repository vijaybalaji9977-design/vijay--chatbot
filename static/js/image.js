class ImageManager {
    constructor() {
        this.activeImage = null; // { data_url, filename, size, width, height }
        this.initEventListeners();
    }

    initEventListeners() {
        const imageInput = document.getElementById("imageInput");
        if (imageInput) {
            imageInput.addEventListener("change", (e) => this.handleImageSelect(e));
        }

        // Global clipboard paste support (Ctrl+V)
        window.addEventListener("paste", (e) => {
            const items = (e.clipboardData || e.originalEvent.clipboardData).items;
            for (let item of items) {
                if (item.type.indexOf("image") !== -1) {
                    const blob = item.getAsFile();
                    this.processImageFile(blob, `pasted_${Date.now()}.png`);
                    break;
                }
            }
        });

        // Drag and drop for images
        const dropZone = document.getElementById("chatContainer");
        if (dropZone) {
            dropZone.addEventListener("dragover", (e) => {
                e.preventDefault();
            });

            dropZone.addEventListener("drop", (e) => {
                e.preventDefault();
                if (e.dataTransfer.files && e.dataTransfer.files.length > 0) {
                    const file = e.dataTransfer.files[0];
                    if (file.type.startsWith("image/")) {
                        this.processImageFile(file, file.name);
                    }
                }
            });
        }
    }

    handleImageSelect(event) {
        const file = event.target.files[0];
        if (file) {
            this.processImageFile(file, file.name);
        }
        event.target.value = ""; // Reset file input
    }

    processImageFile(file, filename) {
        const reader = new FileReader();
        reader.onload = (e) => {
            const dataUrl = e.target.result;
            const img = new Image();
            img.onload = () => {
                this.setActiveImage({
                    data_url: dataUrl,
                    filename: filename || file.name || "image.png",
                    size: file.size,
                    width: img.width,
                    height: img.height
                });
            };
            img.src = dataUrl;
        };
        reader.readAsDataURL(file);
    }

    setActiveImage(imageData) {
        this.activeImage = imageData;
        const badge = document.getElementById("activeImageBadge");
        const nameEl = document.getElementById("activeImageName");
        const sizeEl = document.getElementById("activeImageSize");
        const thumbEl = document.getElementById("activeImageThumb");

        if (badge && nameEl && thumbEl) {
            nameEl.textContent = imageData.filename;
            if (sizeEl) {
                const sizeKb = (imageData.size / 1024).toFixed(1);
                sizeEl.textContent = `${imageData.width}×${imageData.height} • ${sizeKb} KB`;
            }
            thumbEl.src = imageData.data_url;
            badge.classList.remove("hidden");
            badge.classList.add("flex");
        }

        // Automatically switch mode to Image Understanding
        if (window.chatApp) {
            window.chatApp.setMode("vision");
        }
    }

    clearActiveImage() {
        this.activeImage = null;
        const badge = document.getElementById("activeImageBadge");
        if (badge) {
            badge.classList.add("hidden");
            badge.classList.remove("flex");
        }
    }

    getActiveImage() {
        return this.activeImage;
    }

    showImageModal(src, title = "Image Preview") {
        let modal = document.getElementById("imageModal");
        if (!modal) {
            modal = document.createElement("div");
            modal.id = "imageModal";
            modal.className = "fixed inset-0 z-50 flex items-center justify-center p-4 bg-black/80 backdrop-blur-sm";
            modal.innerHTML = `
                <div class="relative max-w-4xl max-h-[90vh] bg-gray-900 border border-gray-800 rounded-2xl overflow-hidden shadow-2xl flex flex-col">
                    <div class="p-3 bg-gray-950 border-b border-gray-800 flex items-center justify-between">
                        <span id="imageModalTitle" class="text-xs font-semibold text-gray-300"></span>
                        <button onclick="document.getElementById('imageModal').classList.add('hidden')" class="text-gray-400 hover:text-white px-2 py-1">
                            <i class="fa-solid fa-xmark"></i>
                        </button>
                    </div>
                    <div class="p-2 overflow-auto flex items-center justify-center">
                        <img id="imageModalImg" class="max-h-[80vh] max-w-full rounded-lg object-contain" src="" alt="Expanded View">
                    </div>
                </div>
            `;
            document.body.appendChild(modal);
            modal.addEventListener("click", (e) => {
                if (e.target === modal) modal.classList.add("hidden");
            });
        }
        document.getElementById("imageModalTitle").textContent = title;
        document.getElementById("imageModalImg").src = src;
        modal.classList.remove("hidden");
    }
}

const imageManager = new ImageManager();
