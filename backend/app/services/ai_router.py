import os
import logging
import re
from app.config import settings

logger = logging.getLogger(__name__)

def clean_ai_phrases(text: str) -> str:
    if not text:
        return text
    
    # List of forbidden patterns that we want to clean from beginning of response
    forbidden_at_start = [
        r"^[Ss]ure[,.!?:\s]*",
        r"^[Cc]ertainly[,.!?:\s]*",
        r"^[Aa]bsolutely[,.!?:\s]*",
        r"^[Gg]reat\s+[Qq]uestion[,.!?:\s]*",
        r"^[Ee]xcellent\s+[Qq]uestion[,.!?:\s]*",
        r"^[Yy]ou're\s+asking\s+about[,.!?:\s]*",
        r"^[Ii]'d\s+be\s+happy\s+to\s+help[,.!?:\s]*",
        r"^[Oo]f\s+[Cc]ourse[,.!?:\s]*",
        r"^[Tt]hat's\s+a\s+fantastic\s+question[,.!?:\s]*",
        r"^[Oo]h\s+[Yy]aar[,.!?:\s]*",
    ]
    
    cleaned = text.strip()
    # Loop to clear nested/stacked starters like "Sure! Absolutely, "
    changed = True
    while changed:
        changed = False
        for pat in forbidden_at_start:
            new_cleaned = re.sub(pat, "", cleaned, flags=re.IGNORECASE).strip()
            if new_cleaned != cleaned:
                cleaned = new_cleaned
                changed = True

    # List of forbidden phrases to clean anywhere
    forbidden_patterns = [
        r"\b[Gg]reat\s+[Qq]uestion\b",
        r"\b[Ee]xcellent\s+[Qq]uestion\b",
        r"\b[Yy]ou're\s+asking\s+about\b",
        r"\b[Ii]'d\s+be\s+happy\s+to\s+help\b",
        r"\b[Aa]bsolutely\b",
        r"\b[Cc]ertainly\b",
        r"\b[Oo]f\s+[Cc]ourse\b",
        r"\b[Tt]hat's\s+a\s+fantastic\s+question\b",
        r"\b[Oo]h\s+[Yy]aar\b"
    ]
    
    for pat in forbidden_patterns:
        cleaned = re.sub(pat + r"[,.!?:\s]*", "", cleaned, flags=re.IGNORECASE)
    
    # Limit emojis to at most 1 per response.
    emoji_pattern = re.compile(
        r"[\U00010000-\U0010ffff\u2600-\u27ff]",
        re.UNICODE
    )
    
    matches = list(emoji_pattern.finditer(cleaned))
    if len(matches) > 1:
        # Keep only the first match, discard the rest
        for match in reversed(matches[1:]):
            start, end = match.span()
            cleaned = cleaned[:start] + cleaned[end:]

    # Clean up double spaces, leading/trailing punctuation/spaces
    cleaned = re.sub(r'^\s*[,.!?:\s]+', '', cleaned)
    cleaned = re.sub(r'[ \t]+', ' ', cleaned)
    lines = [line.strip() for line in cleaned.split('\n')]
    cleaned = '\n'.join(lines).strip()
    cleaned = re.sub(r'\n{3,}', '\n\n', cleaned)
    
    if cleaned and cleaned[0].islower():
        cleaned = cleaned[0].upper() + cleaned[1:]
        
    return cleaned

class AIRouter:
    def __init__(self):
        self.openrouter_key = os.environ.get("OPENROUTER_API_KEY") or os.environ.get("DEEPSEEK_API_KEY")
        self.generation_provider = os.environ.get("YAAR_AI_PROVIDER", "gemini").strip().lower()
        self.generation_model = os.environ.get("YAAR_AI_MODEL", "").strip()
        if not self.generation_model and self.generation_provider == "gemini":
            self.generation_model = "gemini-2.5-flash"

    def generate_chat_response(self, messages: list[dict], system_instruction: str = None) -> dict:
        """Route generation request to the configured provider with automatic retries and fallbacks."""
        max_retries = 3
        last_exception = None
        for attempt in range(max_retries):
            try:
                logger.info(f"Attempting response generation using configured provider (attempt {attempt + 1}/{max_retries}).")
                if self.generation_provider == "gemini":
                    response_text = self._call_gemini(messages, system_instruction)
                elif self.generation_provider == "openrouter":
                    response_text = self._call_openrouter(messages, system_instruction)
                else:
                    raise ValueError("Configured AI provider is not supported.")

                return {
                    "text": clean_ai_phrases(response_text),
                    "model_used": "configured-default",
                    "provider_used": self.generation_provider,
                    "fallback_index": 0,
                    "status": "success"
                }
            except Exception as e:
                logger.warning(f"Attempt {attempt + 1} failed: {str(e)}")
                last_exception = e
                if attempt < max_retries - 1:
                    import time
                    time.sleep(0.5 * (attempt + 1))
        
        logger.error("Configured AI provider failed after all retries. Invoking local offline fallback.")
        return {
            "text": clean_ai_phrases(self._local_fallback_response(messages)),
            "model_used": "local-fallback-engine",
            "provider_used": "offline-static",
            "fallback_index": -1,
            "status": "local_fallback",
            "errors": [str(last_exception)]
        }

    def _call_gemini(self, messages: list[dict], system_instruction: str) -> str:
        gemini_key = settings.GEMINI_API_KEY or os.environ.get("GEMINI_API_KEY")
        if not gemini_key:
            raise ValueError("Gemini API key is not configured.")
        if not self.generation_model:
            raise ValueError("YAAR_AI_MODEL is not configured.")
        
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
            model=self.generation_model,
            contents=contents,
            config=config
        )
        if response.text:
            return response.text
        raise ValueError("Empty response from Gemini model.")

    def _call_openrouter(self, messages: list[dict], system_instruction: str) -> str:
        if not self.openrouter_key:
            raise ValueError("OpenRouter / DeepSeek API key is not configured.")
        if not self.generation_model:
            raise ValueError("YAAR_AI_MODEL is not configured.")
        
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
            "model": self.generation_model,
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
            return "I am having trouble connecting to the translation service right now. Please try again in a moment."
        elif "summarize" in last_user_query or "pdf" in last_user_query:
            return "I am currently unable to summarize the document due to a connection issue. Please try again in a moment."
        return "I am having trouble connecting right now. How can I help you offline?"

ai_router = AIRouter()
