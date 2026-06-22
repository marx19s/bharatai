import os
import logging
from app.config import settings

logger = logging.getLogger(__name__)

class AIRouter:
    def __init__(self):
        # API Keys
        self.openrouter_key = os.environ.get("OPENROUTER_API_KEY") or os.environ.get("DEEPSEEK_API_KEY")
        
        # Available models order for fallback
        self.model_fallback_chain = [
            {"provider": "gemini", "model": "gemini-2.5-flash"},
            {"provider": "openrouter", "model": "deepseek/deepseek-chat"},
            {"provider": "openrouter", "model": "qwen/qwen-2.5-72b-instruct"},
            {"provider": "openrouter", "model": "meta-llama/llama-3.1-70b-instruct"},
        ]

    def generate_chat_response(self, messages: list[dict], system_instruction: str = None) -> dict:
        """Route generation request to primary model, falling back sequentially if error occurs."""
        errors = []
        for index, config in enumerate(self.model_fallback_chain):
            provider = config["provider"]
            model_name = config["model"]
            
            try:
                logger.info(f"Attempting response generation using {provider} - {model_name}")
                if provider == "gemini":
                    response_text = self._call_gemini(messages, model_name, system_instruction)
                elif provider == "openrouter":
                    response_text = self._call_openrouter(messages, model_name, system_instruction)
                else:
                    raise ValueError(f"Unknown provider {provider}")
                
                return {
                    "text": response_text,
                    "model_used": model_name,
                    "provider_used": provider,
                    "fallback_index": index,
                    "status": "success"
                }
            except Exception as e:
                err_msg = f"Provider {provider} ({model_name}) failed: {str(e)}"
                logger.warning(err_msg)
                errors.append(err_msg)

        # Ultimate fallback (local mock offline response)
        logger.error("All AI providers in chain failed. Invoking local offline fallback.")
        return {
            "text": self._local_fallback_response(messages),
            "model_used": "local-fallback-engine",
            "provider_used": "offline-static",
            "fallback_index": -1,
            "status": "local_fallback",
            "errors": errors
        }

    def _call_gemini(self, messages: list[dict], model_name: str, system_instruction: str) -> str:
        gemini_key = settings.GEMINI_API_KEY or os.environ.get("GEMINI_API_KEY")
        if not gemini_key:
            raise ValueError("Gemini API key is not configured.")
        
        from google import genai
        from google.genai import types
        
        client = genai.Client(api_key=gemini_key)
        contents = []
        for msg in messages:
            role = "user" if msg["role"] == "user" else "model"
            contents.append(types.Content(
                role=role,
                parts=[types.Part.from_text(text=msg["content"])]
            ))
        
        config = types.GenerateContentConfig()
        if system_instruction:
            config.system_instruction = system_instruction
            
        response = client.models.generate_content(
            model=model_name,
            contents=contents,
            config=config
        )
        if response.text:
            return response.text
        raise ValueError("Empty response from Gemini model.")

    def _call_openrouter(self, messages: list[dict], model_name: str, system_instruction: str) -> str:
        if not self.openrouter_key:
            raise ValueError("OpenRouter / DeepSeek API key is not configured.")
        
        import httpx
        headers = {
            "Authorization": f"Bearer {self.openrouter_key}",
            "Content-Type": "application/json",
            "HTTP-Referer": "https://bharatai.dev",
            "X-Title": "BharatAI Sovereign Workspace"
        }
        
        formatted_messages = []
        if system_instruction:
            formatted_messages.append({"role": "system", "content": system_instruction})
            
        for msg in messages:
            formatted_messages.append({"role": msg["role"], "content": msg["content"]})
            
        payload = {
            "model": model_name,
            "messages": formatted_messages,
            "temperature": 0.3
        }
        
        with httpx.Client(timeout=30.0) as client:
            r = client.post("https://openrouter.ai/api/v1/chat/completions", json=payload, headers=headers)
            if r.status_code == 200:
                data = r.json()
                return data["choices"][0]["message"]["content"]
            raise ValueError(f"OpenRouter API error: {r.status_code} - {r.text}")

    def _local_fallback_response(self, messages: list[dict]) -> str:
        last_user_query = ""
        for m in reversed(messages):
            if m["role"] == "user":
                last_user_query = m["content"].lower()
                break
                
        if "translate" in last_user_query:
            return "नमस्ते! (Translation service offline: rate limits exceeded. Please retry in a few seconds.)"
        elif "summarize" in last_user_query or "pdf" in last_user_query:
            return "Summary processing offline. I detected your document upload, but all AI endpoints are currently busy. Please try again shortly."
        return "I am currently running in offline recovery mode. The Sovereign AI endpoints are rate-limited or offline. How can I assist you with offline capabilities?"

ai_router = AIRouter()
