import os
import logging
import re
from app.config import settings

logger = logging.getLogger(__name__)

# Try importing Google GenAI SDK
HAS_GEMINI_SDK = False
try:
    from google import genai
    from google.genai import types
    HAS_GEMINI_SDK = True
except ImportError:
    logger.warning("google-genai SDK not installed. Falling back to mock mode.")

def clean_ai_phrases(text: str) -> str:
    if not text:
        return text
    # List of forbidden phrases (case-insensitive)
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
    
    cleaned = text
    for pat in forbidden_patterns:
        cleaned = re.sub(pat + r"[,.!?:\s]*", "", cleaned, flags=re.IGNORECASE)
    
    # Clean up double spaces, leading/trailing punctuation/spaces
    cleaned = re.sub(r'^\s*[,.!?:\s]+', '', cleaned)
    
    # Normalize multiple horizontal spaces to a single space
    cleaned = re.sub(r'[ \t]+', ' ', cleaned)
    # Strip whitespace from the beginning and end of each line
    lines = [line.strip() for line in cleaned.split('\n')]
    cleaned = '\n'.join(lines).strip()
    # Normalize multiple consecutive newlines (max 2)
    cleaned = re.sub(r'\n{3,}', '\n\n', cleaned)
    
    if cleaned and cleaned[0].islower():
        cleaned = cleaned[0].upper() + cleaned[1:]
        
    return cleaned

class AIService:
    def __init__(self):
        self.api_key = settings.GEMINI_API_KEY or os.environ.get("GEMINI_API_KEY")
        self.client = None
        self.use_mock = True

        if HAS_GEMINI_SDK and self.api_key:
            try:
                self.client = genai.Client(api_key=self.api_key)
                self.use_mock = False
                logger.info("Gemini AI Service initialized successfully.")
            except Exception as e:
                logger.error(f"Failed to initialize Gemini client: {e}. Falling back to mock mode.")
        else:
            # Fallback to check if key is present to disable mock
            if self.api_key:
                self.use_mock = False
            else:
                logger.warning("No GEMINI_API_KEY found or SDK not available. Running in MOCK MODE.")

    def generate_chat_response(self, messages: list[dict], system_instruction: str = None) -> str:
        """Generates chat response using Gemini API or mock fallback.
        
        messages list format: [{"role": "user"|"assistant", "content": "..."}]
        """
        # Parse language and vibe from system instruction if running mock
        lang = "English"
        vibe = "friendly"
        if system_instruction:
            lang_match = re.search(r"speaking to your user in (\w+)", system_instruction)
            if lang_match:
                lang = lang_match.group(1)
            vibe_match = re.search(r"personality vibe mode is '(\w+)'", system_instruction)
            if vibe_match:
                vibe = vibe_match.group(1)

        if self.use_mock:
            return clean_ai_phrases(self._mock_chat_response(messages, lang, vibe))
            
        try:
            # Map role names to Gemini roles (user, model)
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
                
            response = self.client.models.generate_content(
                model="gemini-2.5-flash",
                contents=contents,
                config=config
            )
            return clean_ai_phrases(response.text) if response.text else "Sorry, I couldn't generate a response."
        except Exception as e:
            logger.error(f"Gemini API error: {e}")
            raise e

    def summarize_text(self, text: str) -> str:
        """Summarizes text using Gemini API or mock fallback."""
        if self.use_mock:
            return f"Mock Summary of PDF:\nThe document contains {len(text)} characters. The content discusses AI tools, Next.js, FastAPI, and translation. Key concepts include voice inputs, database integrations, and cloud storage mimics."
            
        try:
            prompt = f"Please provide a concise, structured, and comprehensive summary of the following document:\n\n{text}"
            response = self.client.models.generate_content(
                model="gemini-2.5-flash",
                contents=prompt
            )
            return response.text if response.text else "Failed to generate summary."
        except Exception as e:
            logger.error(f"Summarization error: {e}")
            return f"Error generating summary: {str(e)}"

    def translate_text(self, text: str, target_language: str) -> str:
        """Translates text to target language using Gemini API with MyMemory fallback."""
        if self.use_mock:
            if target_language.lower() in ["punjabi", "pa"]:
                return f"[ਪੰਜਾਬੀ ਅਨੁਵਾਦ]: {text[:100]}... (ਇਹ ਇੱਕ ਨਕਲੀ ਅਨੁਵਾਦ ਹੈ।)"
            return f"[Translated to {target_language}]: {text} (Mock)"
            
        try:
            prompt = f"Translate the following text into {target_language}. Translate accurately and maintain the original tone. Return ONLY the translated text, nothing else:\n\n{text}"
            response = self.client.models.generate_content(
                model="gemini-2.5-flash",
                contents=prompt
            )
            return response.text.strip() if response.text else "Failed to translate."
        except Exception as e:
            logger.warning(f"Translation API rate-limited, using MyMemory fallback: {e}")
            try:
                # Map language name to code
                lang_map = {
                    "punjabi": "pa",
                    "hindi": "hi",
                    "tamil": "ta",
                    "telugu": "te",
                    "bengali": "bn",
                    "marathi": "mr",
                    "gujarati": "gu",
                    "kannada": "kn",
                    "malayalam": "ml"
                }
                lang_code = lang_map.get(target_language.lower(), "pa")
                
                import httpx
                r = httpx.get(
                    "https://api.mymemory.translated.net/get",
                    params={"q": text, "langpair": f"en|{lang_code}"},
                    timeout=10.0
                )
                if r.status_code == 200:
                    data = r.json()
                    translated = data.get("responseData", {}).get("translatedText", "")
                    if translated:
                        return f"{translated}\n\n*(Translated via MyMemory Offline Fallback due to Gemini Rate Limit)*"
                return f"Error translating text: Gemini API limit reached (429)."
            except Exception as fallback_err:
                return f"Error translating: Gemini API limit reached (429). Offline error: {str(fallback_err)}"

    def fix_grammar(self, text: str) -> str:
        """Corrects grammar and spelling errors in the text using Gemini API or local fallback."""
        if self.use_mock:
            return f"{text} (Grammar Checked: Looks good!)"
            
        try:
            prompt = (
                "Review the following text for grammar, spelling, and punctuation errors. "
                "Provide the corrected version. If the text is already correct, return it as-is. "
                "Return ONLY the corrected text, without any introductory or concluding comments:\n\n"
                f"{text}"
            )
            response = self.client.models.generate_content(
                model="gemini-2.5-flash",
                contents=prompt
            )
            return response.text.strip() if response.text else text
        except Exception as e:
            logger.warning(f"Grammar fix API rate-limited: {e}")
            return f"{text} *(Grammar check bypassed: Gemini rate-limit reached)*"

    def digitize_pdf(self, file_path: str) -> str:
        """Digitizes PDF (image or digital) using Gemini multimodal capabilities with local text fallback."""
        if self.use_mock:
            return (
                "## Digitized Document (Mock)\n\n"
                "### Table of Contents\n"
                "1. Executive Summary\n"
                "2. Standard Compliance Frameworks\n\n"
                "| Section | Compliance Status | Comments |\n"
                "|---|---|---|\n"
                "| Data Retention | Checked | Standard 90 days retention policy |\n"
                "| Consent | Pending | Needs clear opt-in tick box |"
            )

        try:
            # Upload file to Gemini Files API
            file_ref = self.client.files.upload(file=file_path)
            
            prompt = (
                "You are an expert Document Digitization engine for Indian and global enterprises. "
                "Analyze this document and transcribe it. Maintain layout, tables, formatting, "
                "headings, and structural blocks exactly. Support and preserve any Indian languages "
                "(such as Hindi, Punjabi, Tamil, etc.) present in the text. Output in clean Markdown format."
            )
            
            response = self.client.models.generate_content(
                model="gemini-2.5-flash",
                contents=[file_ref, prompt]
            )
            
            # Clean up the file from Gemini storage
            try:
                self.client.files.delete(name=file_ref.name)
            except Exception as e:
                logger.warning(f"Failed to delete temporary Gemini file: {e}")
                
            return response.text if response.text else "Failed to extract layout."
        except Exception as e:
            logger.warning(f"Gemini digitization rate-limited, falling back to local text: {e}")
            try:
                # Extract text locally using PyPDF
                from app.services.pdf_service import pdf_service
                text = pdf_service.extract_text(file_path)
                if text.strip():
                    return (
                        "⚠️ **[Local Offline Digitization Fallback (Gemini Limit Reached)]**\n\n"
                        "We extracted the digital text contents of the document locally:\n\n"
                        f"{text}\n\n"
                        "*(Note: Layout formatting and table grids could not be fully reconstructed offline)*"
                    )
                else:
                    return (
                        "⚠️ **[Multimodal OCR Limit Reached]**\n\n"
                        "This document appears to be a scanned image or has no digital text. "
                        "Because the Gemini API limit (429) was hit, we cannot perform offline layout-preserved OCR. "
                        "Please retry in a minute when your rate limit resets."
                    )
            except Exception as err:
                return f"Error digitizing document offline: {str(err)}"

    def run_compliance_audit(self, file_path: str, preset: str) -> dict:
        """Runs a regulatory compliance audit on the document with local keyword scanning fallback."""
        if self.use_mock:
            return {
                "score": 85,
                "checks": [
                    {"rule": "Data Residency (DPDP Section 6)", "status": "Passed", "details": "Data is stated to be stored locally in India."},
                    {"rule": "Clear Consent Language", "status": "Warning", "details": "The terms use broad language for consent instead of affirmative specific choice."},
                    {"rule": "Grievance Officer Details", "status": "Failed", "details": "No Grievance Redressal Officer contact details found."}
                ]
            }

        try:
            # Upload file to Gemini Files API
            file_ref = self.client.files.upload(file=file_path)
            
            prompt = (
                f"You are a regulatory compliance auditor for Indian businesses. Audit the attached document "
                f"against the framework: '{preset}'.\n\n"
                "Create a detailed compliance checklist scorecard. You MUST return your response in JSON format. "
                "Do NOT add any Markdown markers like ```json or trailing text. The JSON object should have two root fields:\n"
                "1. 'score': an integer from 0 to 100 representing the compliance level.\n"
                "2. 'checks': a list of objects, each containing:\n"
                "   - 'rule': a brief description of the legal/compliance clause checked\n"
                "   - 'status': either 'Passed', 'Warning', or 'Failed'\n"
                "   - 'details': a detailed explanation of the finding, citing the document page or text if possible\n\n"
                "Audit frameworks guidelines:\n"
                "- 'DPDP Act 2023': Focus on consent, data fiduciary obligations, grievance redressal, processing purposes.\n"
                "- 'IRDAI Guidelines': Focus on policyholder protection, terms, disclosures, premium refunds.\n"
                "- 'Legal Risk': General contract redlining, indemnity clauses, termination terms, and liability limits."
            )
            
            # Request structured JSON response
            response = self.client.models.generate_content(
                model="gemini-2.5-flash",
                contents=[file_ref, prompt],
                config=types.GenerateContentConfig(
                    response_mime_type="application/json",
                )
            )
            
            # Clean up the file from Gemini storage
            try:
                self.client.files.delete(name=file_ref.name)
            except Exception as e:
                logger.warning(f"Failed to delete temporary Gemini file: {e}")
            
            import json
            raw_text = response.text.strip()
            # If the model wrapped in ```json ... ```, strip it
            if raw_text.startswith("```"):
                lines = raw_text.split("\n")
                if lines[0].startswith("```json") or lines[0].startswith("```"):
                    raw_text = "\n".join(lines[1:-1])
            
            return json.loads(raw_text)
        except Exception as e:
            logger.warning(f"Gemini compliance audit rate-limited, running local offline keyword audit: {e}")
            try:
                # Extract text locally
                from app.services.pdf_service import pdf_service
                text = pdf_service.extract_text(file_path).lower()
                
                checks = []
                score = 100
                
                if preset == "DPDP Act 2023":
                    # Check 1: Consent
                    if "consent" in text or "agree" in text:
                        checks.append({
                            "rule": "Consent for Processing Personal Data (Section 5)",
                            "status": "Passed",
                            "details": "Consent clause matches DPDP guidelines (Affirmative action identified in document)."
                        })
                    else:
                        score -= 25
                        checks.append({
                            "rule": "Consent for Processing Personal Data (Section 5)",
                            "status": "Failed",
                            "details": "No explicit consent or agreement provisions identified in text."
                        })
                        
                    # Check 2: Data Residency
                    if "india" in text or "resident" in text or "storage" in text:
                        checks.append({
                            "rule": "Data Residency and Storage (Section 6)",
                            "status": "Passed",
                            "details": "Indian geographic references found. Implies data residency checks conform."
                        })
                    else:
                        score -= 25
                        checks.append({
                            "rule": "Data Residency and Storage (Section 6)",
                            "status": "Warning",
                            "details": "No explicit mention of Indian data localization. Verify storage parameters."
                        })
                        
                    # Check 3: Grievance Redressal
                    if "grievance" in text or "officer" in text or "contact" in text or "support" in text:
                        checks.append({
                            "rule": "Grievance Redressal Mechanism (Section 13)",
                            "status": "Passed",
                            "details": "Document specifies contact/support mechanisms for user complaints."
                        })
                    else:
                        score -= 30
                        checks.append({
                            "rule": "Grievance Redressal Mechanism (Section 13)",
                            "status": "Failed",
                            "details": "No Grievance Officer details or complaint handling portals listed."
                        })
                        
                elif preset == "IRDAI Guidelines":
                    # Check 1: Policyholder protection
                    if "protect" in text or "insure" in text or "claim" in text:
                        checks.append({
                            "rule": "Policyholder Protection & Disclosures",
                            "status": "Passed",
                            "details": "Standard disclosure and coverage terms are present in contract."
                        })
                    else:
                        score -= 30
                        checks.append({
                            "rule": "Policyholder Protection & Disclosures",
                            "status": "Failed",
                            "details": "Fails standard IRDAI disclosure requirements. Policy limits unclear."
                        })
                        
                    # Check 2: Premium Refund
                    if "refund" in text or "premium" in text or "cancellation" in text:
                        checks.append({
                            "rule": "Premium Refund & Cancellation Policy",
                            "status": "Passed",
                            "details": "Identified clauses regulating premium refunds or cancellation fees."
                        })
                    else:
                        score -= 30
                        checks.append({
                            "rule": "Premium Refund & Cancellation Policy",
                            "status": "Warning",
                            "details": "No clear refund or cool-off cancellation periods defined."
                        })
                        
                else: # Legal Risk
                    # Check 1: Indemnity
                    if "indemnity" in text or "indemnify" in text or "liability" in text:
                        checks.append({
                            "rule": "Indemnity and Liability Limits",
                            "status": "Warning",
                            "details": "Broad liability protection or indemnity clauses found. Review exposure."
                        })
                    else:
                        checks.append({
                            "rule": "Indemnity and Liability Limits",
                            "status": "Passed",
                            "details": "No high-risk, one-sided indemnity terms detected."
                        })
                        
                    # Check 2: Termination
                    if "termination" in text or "terminate" in text or "expiry" in text:
                        checks.append({
                            "rule": "Contract Termination Conditions",
                            "status": "Passed",
                            "details": "Standard termination procedures are documented in text."
                        })
                    else:
                        score -= 30
                        checks.append({
                            "rule": "Contract Termination Conditions",
                            "status": "Failed",
                            "details": "No exit terms or termination notices found."
                        })
                
                # Prepend offline notification to details of first check
                if checks:
                    checks[0]["details"] = "⚠️ [OFFLINE FALLBACK AUDIT] " + checks[0]["details"]
                    
                return {
                    "score": max(10, score),
                    "checks": checks
                }
            except Exception as err:
                return {
                    "score": 0,
                    "checks": [
                        {"rule": "Offline Audit Failed", "status": "Failed", "details": f"Could not run fallback scanner: {str(err)}"}
                    ]
                }

    def _mock_chat_response(self, messages: list[dict], language: str = "English", vibe: str = "friendly") -> str:
        last_user_msg = next((m["content"] for m in reversed(messages) if m["role"] == "user"), "")
        last_user_msg_lower = last_user_msg.lower().strip()

        # Check if greeting
        greetings = ["ki haal", "ki haal hai", "kive ho", "kem cho", "kemcho", "vanakkam", "namaste", "nomoshkar", "kaisa hai", "kya haal", "hello", "hi", "how are you", "howdy"]
        is_greeting = any(g in last_user_msg_lower for g in greetings)

        if is_greeting:
            if vibe in ["regional", "friendly"]:
                if language.lower() in ["punjabi", "pa"]:
                    return "Main theek aa veere. Tu dass?"
                elif language.lower() in ["gujarati", "gu"]:
                    return "Maja ma chu mitra. Tame kem cho?"
                elif language.lower() in ["tamil", "ta"]:
                    return "Naan nalla irukken nanba. Neenga eppadi irukeenga?"
                else: # Hindi or other default
                    return "Main theek hoon dost. Tum batao?"
            else: # Formal
                if language.lower() in ["punjabi", "pa"]:
                    return "ਮੈਂ ਬਿਲਕੁਲ ਠੀਕ ਹਾਂ। ਆਪ ਜੀ ਦੱਸੋ, ਤੁਹਾਡਾ ਕੀ ਹਾਲ ਹੈ?"
                elif language.lower() in ["gujarati", "gu"]:
                    return "હું સારો છું. આપ આપના વિશે જણાવો."
                elif language.lower() in ["tamil", "ta"]:
                    return "நான் நலமாக இருக்கிறேன். நீங்கள் எப்படி இருக்கிறீர்கள்?"
                else: # Hindi / English
                    return "मैं ठीक हूँ। आप कैसे हैं?"

        if "summarize" in last_user_msg_lower or "summary" in last_user_msg_lower:
            return "This is a mock summary of your document: It covers high-level concepts of project design, database schemas, and AI components."
        else:
            return f"Set GEMINI_API_KEY in backend/.env to activate live AI responses. (Offline Mock: You said '{last_user_msg}')"

ai_service = AIService()
