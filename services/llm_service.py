import json
import httpx
import time
from typing import AsyncGenerator, Dict, Any, List, Optional
from core.config import GEMINI_API_KEY, OPENAI_API_KEY, GROQ_API_KEY
from services.offline_engine import offline_engine

class LLMService:
    """
    Unified multi-provider LLM service supporting Google Gemini (Multimodal),
    OpenAI (GPT-4o Multimodal), Groq, OpenRouter, and built-in offline engine.
    """

    async def generate_response(
        self,
        messages: List[Dict[str, str]],
        system_prompt: str,
        mode: str = "general",
        provider: Optional[str] = None,
        api_key: Optional[str] = None,
        model: Optional[str] = None,
        temperature: float = 0.7,
        metadata: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """Non-streaming response generator."""
        start_time = time.time()
        
        # Determine provider and key
        active_provider, active_key, active_model = self._resolve_credentials(provider, api_key, model)
        
        # If no key available or provider is offline, use built-in offline engine
        if not active_key or active_provider == "offline":
            last_user_msg = next((m["content"] for m in reversed(messages) if m["role"] == "user"), "")
            response_text = offline_engine.process_query(last_user_msg, mode=mode, metadata=metadata)
            latency = (time.time() - start_time) * 1000
            return {
                "text": response_text,
                "model": "offline-intelligent-engine",
                "provider": "offline",
                "latency_ms": round(latency, 2)
            }

        try:
            if active_provider == "gemini":
                text = await self._call_gemini(messages, system_prompt, active_key, active_model, temperature, metadata)
            elif active_provider in ["openai", "groq", "openrouter"]:
                text = await self._call_openai_compatible(messages, system_prompt, active_provider, active_key, active_model, temperature, metadata)
            else:
                last_user_msg = next((m["content"] for m in reversed(messages) if m["role"] == "user"), "")
                text = offline_engine.process_query(last_user_msg, mode=mode, metadata=metadata)

            latency = (time.time() - start_time) * 1000
            return {
                "text": text,
                "model": active_model,
                "provider": active_provider,
                "latency_ms": round(latency, 2)
            }
        except Exception as e:
            # Graceful fallback to offline engine on API failure
            last_user_msg = next((m["content"] for m in reversed(messages) if m["role"] == "user"), "")
            fallback_text = offline_engine.process_query(last_user_msg, mode=mode, metadata=metadata)
            latency = (time.time() - start_time) * 1000
            return {
                "text": f"{fallback_text}\n\n> *(Notice: Online provider returned an error: `{str(e)}`. Answer generated using built-in intelligent engine.)*",
                "model": "offline-fallback",
                "provider": "offline",
                "latency_ms": round(latency, 2)
            }

    async def stream_response(
        self,
        messages: List[Dict[str, str]],
        system_prompt: str,
        mode: str = "general",
        provider: Optional[str] = None,
        api_key: Optional[str] = None,
        model: Optional[str] = None,
        temperature: float = 0.7,
        metadata: Optional[Dict[str, Any]] = None
    ) -> AsyncGenerator[str, None]:
        """Streaming generator for Server-Sent Events."""
        active_provider, active_key, active_model = self._resolve_credentials(provider, api_key, model)

        if not active_key or active_provider == "offline":
            last_user_msg = next((m["content"] for m in reversed(messages) if m["role"] == "user"), "")
            full_response = offline_engine.process_query(last_user_msg, mode=mode, metadata=metadata)
            
            # Simulate streaming chunks for offline engine
            chunk_size = 20
            for i in range(0, len(full_response), chunk_size):
                chunk = full_response[i:i + chunk_size]
                yield f"data: {json.dumps({'chunk': chunk, 'done': False})}\n\n"
            yield f"data: {json.dumps({'chunk': '', 'done': True, 'model': 'offline-intelligent-engine'})}\n\n"
            return

        try:
            if active_provider == "gemini":
                async for chunk in self._stream_gemini(messages, system_prompt, active_key, active_model, temperature, metadata):
                    yield f"data: {json.dumps({'chunk': chunk, 'done': False})}\n\n"
                yield f"data: {json.dumps({'chunk': '', 'done': True, 'model': active_model})}\n\n"
            else:
                async for chunk in self._stream_openai_compatible(messages, system_prompt, active_provider, active_key, active_model, temperature, metadata):
                    yield f"data: {json.dumps({'chunk': chunk, 'done': False})}\n\n"
                yield f"data: {json.dumps({'chunk': '', 'done': True, 'model': active_model})}\n\n"
        except Exception as e:
            # Stream error with fallback
            last_user_msg = next((m["content"] for m in reversed(messages) if m["role"] == "user"), "")
            fallback_text = offline_engine.process_query(last_user_msg, mode=mode, metadata=metadata)
            err_msg = f"\n\n> *(API stream error: {str(e)}. Fallback to offline engine)*\n\n" + fallback_text
            yield f"data: {json.dumps({'chunk': err_msg, 'done': False})}\n\n"
            yield f"data: {json.dumps({'chunk': '', 'done': True, 'model': 'offline-fallback'})}\n\n"

    def _resolve_credentials(self, provider: Optional[str], api_key: Optional[str], model: Optional[str]):
        p = provider.lower() if provider else ("gemini" if GEMINI_API_KEY else ("openai" if OPENAI_API_KEY else ("groq" if GROQ_API_KEY else "offline")))
        
        k = api_key or ""
        if not k:
            if p == "gemini":
                k = GEMINI_API_KEY
            elif p == "openai":
                k = OPENAI_API_KEY
            elif p == "groq":
                k = GROQ_API_KEY

        m = model
        if not m:
            if p == "gemini":
                m = "gemini-1.5-flash"
            elif p == "openai":
                m = "gpt-4o-mini"
            elif p == "groq":
                m = "llama-3.1-70b-versatile"
            else:
                m = "offline-intelligent-engine"

        return p, k, m

    def _prepare_gemini_contents(self, messages: List[Dict], metadata: Optional[Dict[str, Any]] = None):
        """Constructs Gemini contents payload with multimodal image support."""
        contents = []
        for i, m in enumerate(messages):
            role = "user" if m["role"] == "user" else "model"
            parts = [{"text": m["content"]}]
            
            # If this is the last user message and image metadata is provided
            if i == len(messages) - 1 and role == "user" and metadata and metadata.get("image_base64"):
                mime_type = metadata.get("image_mime", "image/png")
                b64_data = metadata.get("image_base64")
                parts.append({
                    "inline_data": {
                        "mime_type": mime_type,
                        "data": b64_data
                    }
                })
            
            contents.append({"role": role, "parts": parts})
        return contents

    # GEMINI IMPLEMENTATION
    async def _call_gemini(self, messages: List[Dict], system_prompt: str, api_key: str, model: str, temperature: float, metadata: Optional[Dict] = None) -> str:
        url = f"https://generativelanguage.googleapis.com/v1beta/models/{model}:generateContent?key={api_key}"
        contents = self._prepare_gemini_contents(messages, metadata)

        payload = {
            "contents": contents,
            "systemInstruction": {"parts": [{"text": system_prompt}]},
            "generationConfig": {"temperature": temperature}
        }

        async with httpx.AsyncClient(timeout=60.0) as client:
            resp = await client.post(url, json=payload)
            resp.raise_for_status()
            data = resp.json()
            candidates = data.get("candidates", [])
            if candidates and "content" in candidates[0]:
                parts = candidates[0]["content"].get("parts", [])
                return "".join([p.get("text", "") for p in parts])
            return "No response received from Gemini."

    async def _stream_gemini(self, messages: List[Dict], system_prompt: str, api_key: str, model: str, temperature: float, metadata: Optional[Dict] = None) -> AsyncGenerator[str, None]:
        url = f"https://generativelanguage.googleapis.com/v1beta/models/{model}:streamGenerateContent?alt=sse&key={api_key}"
        contents = self._prepare_gemini_contents(messages, metadata)

        payload = {
            "contents": contents,
            "systemInstruction": {"parts": [{"text": system_prompt}]},
            "generationConfig": {"temperature": temperature}
        }

        async with httpx.AsyncClient(timeout=60.0) as client:
            async with client.stream("POST", url, json=payload) as response:
                response.raise_for_status()
                async for line in response.aiter_lines():
                    if line.startswith("data: "):
                        data_str = line[6:].strip()
                        if not data_str:
                            continue
                        try:
                            json_obj = json.loads(data_str)
                            candidates = json_obj.get("candidates", [])
                            if candidates and "content" in candidates[0]:
                                for part in candidates[0]["content"].get("parts", []):
                                    text = part.get("text", "")
                                    if text:
                                        yield text
                        except Exception:
                            continue

    def _prepare_openai_messages(self, messages: List[Dict], system_prompt: str, metadata: Optional[Dict] = None):
        """Constructs OpenAI messages payload with multimodal image support."""
        formatted_messages = [{"role": "system", "content": system_prompt}]
        for i, m in enumerate(messages):
            if i == len(messages) - 1 and m["role"] == "user" and metadata and metadata.get("image_data_url"):
                formatted_messages.append({
                    "role": "user",
                    "content": [
                        {"type": "text", "text": m["content"]},
                        {"type": "image_url", "image_url": {"url": metadata["image_data_url"]}}
                    ]
                })
            else:
                formatted_messages.append({"role": m["role"], "content": m["content"]})
        return formatted_messages

    # OPENAI / GROQ COMPATIBLE IMPLEMENTATION
    async def _call_openai_compatible(self, messages: List[Dict], system_prompt: str, provider: str, api_key: str, model: str, temperature: float, metadata: Optional[Dict] = None) -> str:
        base_url = "https://api.openai.com/v1/chat/completions"
        if provider == "groq":
            base_url = "https://api.groq.com/openai/v1/chat/completions"
        elif provider == "openrouter":
            base_url = "https://openrouter.ai/api/v1/chat/completions"

        headers = {
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json"
        }

        formatted_messages = self._prepare_openai_messages(messages, system_prompt, metadata)

        payload = {
            "model": model,
            "messages": formatted_messages,
            "temperature": temperature
        }

        async with httpx.AsyncClient(timeout=60.0) as client:
            resp = await client.post(base_url, headers=headers, json=payload)
            resp.raise_for_status()
            data = resp.json()
            return data["choices"][0]["message"]["content"]

    async def _stream_openai_compatible(self, messages: List[Dict], system_prompt: str, provider: str, api_key: str, model: str, temperature: float, metadata: Optional[Dict] = None) -> AsyncGenerator[str, None]:
        base_url = "https://api.openai.com/v1/chat/completions"
        if provider == "groq":
            base_url = "https://api.groq.com/openai/v1/chat/completions"
        elif provider == "openrouter":
            base_url = "https://openrouter.ai/api/v1/chat/completions"

        headers = {
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json"
        }

        formatted_messages = self._prepare_openai_messages(messages, system_prompt, metadata)

        payload = {
            "model": model,
            "messages": formatted_messages,
            "temperature": temperature,
            "stream": True
        }

        async with httpx.AsyncClient(timeout=60.0) as client:
            async with client.stream("POST", base_url, headers=headers, json=payload) as response:
                response.raise_for_status()
                async for line in response.aiter_lines():
                    if line.startswith("data: "):
                        data_str = line[6:].strip()
                        if data_str == "[DONE]":
                            break
                        try:
                            json_obj = json.loads(data_str)
                            delta = json_obj["choices"][0].get("delta", {})
                            content = delta.get("content", "")
                            if content:
                                yield content
                        except Exception:
                            continue

# Singleton instance
llm_service = LLMService()
