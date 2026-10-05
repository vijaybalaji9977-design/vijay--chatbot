import io
import base64
import uuid
from pathlib import Path
from typing import Dict, Any, Optional, Tuple
from PIL import Image, ImageStat
from core.config import IMAGES_DIR, ALLOWED_IMAGE_EXTENSIONS

class ImageService:
    """
    Handles image validation, processing, metadata extraction, base64 encoding,
    and offline visual analysis for multimodal interactions.
    """

    def __init__(self):
        IMAGES_DIR.mkdir(parents=True, exist_ok=True)

    def process_image_bytes(self, filename: str, content_bytes: bytes) -> Dict[str, Any]:
        """Processes raw image bytes, saves image file, and generates base64 data URL & metadata."""
        ext = Path(filename).suffix.lower()
        if ext not in ALLOWED_IMAGE_EXTENSIONS:
            ext = ".png"

        image_id = str(uuid.uuid4())
        safe_filename = f"{image_id}{ext}"
        file_path = IMAGES_DIR / safe_filename

        with open(file_path, "wb") as f:
            f.write(content_bytes)

        # Open with PIL for validation & metadata
        try:
            with Image.open(io.BytesIO(content_bytes)) as img:
                width, height = img.size
                format_name = img.format or ext.lstrip(".").upper()
                mode = img.mode

                # Determine MIME type
                mime_map = {
                    "PNG": "image/png",
                    "JPEG": "image/jpeg",
                    "JPG": "image/jpeg",
                    "WEBP": "image/webp",
                    "GIF": "image/gif",
                    "BMP": "image/bmp"
                }
                mime_type = mime_map.get(format_name.upper(), "image/png")

                # Generate base64 data URL
                b64_str = base64.b64encode(content_bytes).decode("utf-8")
                data_url = f"data:{mime_type};base64,{b64_str}"

                # Generate offline visual analysis
                offline_analysis = self._generate_offline_analysis(img, filename, len(content_bytes))

                return {
                    "id": image_id,
                    "filename": filename,
                    "file_type": ext.lstrip("."),
                    "mime_type": mime_type,
                    "width": width,
                    "height": height,
                    "size": len(content_bytes),
                    "file_path": str(file_path),
                    "data_url": data_url,
                    "base64_data": b64_str,
                    "offline_analysis": offline_analysis
                }
        except Exception as e:
            # Fallback if image parsing fails
            b64_str = base64.b64encode(content_bytes).decode("utf-8")
            return {
                "id": image_id,
                "filename": filename,
                "file_type": ext.lstrip("."),
                "mime_type": "image/png",
                "width": 0,
                "height": 0,
                "size": len(content_bytes),
                "file_path": str(file_path),
                "data_url": f"data:image/png;base64,{b64_str}",
                "base64_data": b64_str,
                "offline_analysis": f"Image uploaded ({filename}, {len(content_bytes)} bytes). Parsing warning: {str(e)}"
            }

    def process_base64_image(self, data_url_or_b64: str, filename: str = "pasted_image.png") -> Dict[str, Any]:
        """Processes an image provided as a base64 string or data URL."""
        if "," in data_url_or_b64:
            header, b64_part = data_url_or_b64.split(",", 1)
        else:
            b64_part = data_url_or_b64

        try:
            content_bytes = base64.b64decode(b64_part)
            return self.process_image_bytes(filename, content_bytes)
        except Exception as e:
            return {
                "id": str(uuid.uuid4()),
                "filename": filename,
                "file_type": "png",
                "mime_type": "image/png",
                "width": 0,
                "height": 0,
                "size": 0,
                "data_url": data_url_or_b64 if data_url_or_b64.startswith("data:") else f"data:image/png;base64,{data_url_or_b64}",
                "base64_data": b64_part,
                "offline_analysis": f"Error decoding base64 image: {str(e)}"
            }

    def _generate_offline_analysis(self, img: Image.Image, filename: str, file_size: int) -> str:
        """Generates a structured offline analysis of image dimensions, color composition, and aspect ratio."""
        width, height = img.size
        aspect_ratio = round(width / max(height, 1), 2)
        orientation = "Square" if aspect_ratio == 1.0 else ("Landscape" if aspect_ratio > 1.0 else "Portrait")

        # Compute brightness and color statistics if image can be converted to RGB
        try:
            rgb_img = img.convert("RGB")
            stat = ImageStat.Stat(rgb_img)
            avg_r, avg_g, avg_b = stat.mean[:3]
            brightness = (0.299 * avg_r + 0.587 * avg_g + 0.114 * avg_b)
            brightness_pct = round((brightness / 255.0) * 100, 1)

            # Palette tone
            if avg_r > avg_g and avg_r > avg_b:
                primary_tone = "Warm (Reddish/Orange dominant)"
            elif avg_b > avg_r and avg_b > avg_g:
                primary_tone = "Cool (Bluish dominant)"
            elif avg_g > avg_r and avg_g > avg_b:
                primary_tone = "Nature / Lush (Greenish dominant)"
            else:
                primary_tone = "Balanced / Neutral tones"
        except Exception:
            brightness_pct = 50.0
            primary_tone = "Standard RGB spectrum"

        size_kb = round(file_size / 1024, 1)

        return (
            f"### 🖼️ Image Vision & Inspection Analysis\n\n"
            f"**File Details:**\n"
            f"- **Filename:** `{filename}`\n"
            f"- **Resolution:** `{width} × {height} px` ({orientation}, aspect ratio `{aspect_ratio}:1`)\n"
            f"- **Color Mode:** `{img.mode}` | **Size:** `{size_kb} KB`\n"
            f"- **Average Brightness:** `{brightness_pct}%`\n"
            f"- **Color Composition:** {primary_tone}\n\n"
            f"**Visual Understanding Summary:**\n"
            f"> The image has been successfully inspected and indexed. "
            f"When using online models (Google Gemini or OpenAI GPT-4o), full multimodal reasoning, OCR, "
            f"object detection, chart analysis, and diagram problem-solving are directly active.\n"
        )

image_service = ImageService()
