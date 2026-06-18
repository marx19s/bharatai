from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
import httpx
import uuid
import os
import urllib.parse
from app.config import settings
from app.services.ai_service import ai_service

router = APIRouter(prefix="/tools", tags=["Tools"])

class TranslateRequest(BaseModel):
    text: str
    target_language: str = "Punjabi"

class TranslateResponse(BaseModel):
    translated_text: str
    target_language: str

class GrammarRequest(BaseModel):
    text: str

class GrammarResponse(BaseModel):
    corrected_text: str

class ImageRequest(BaseModel):
    prompt: str

class ImageResponse(BaseModel):
    image_url: str
    prompt: str

class VideoRequest(BaseModel):
    prompt: str

class StoryboardScene(BaseModel):
    scene_number: int
    narration: str
    visual_prompt: str
    image_url: str
    duration: int = 5

class VideoResponse(BaseModel):
    prompt: str
    title: str
    storyboard: list[StoryboardScene]

@router.post("/translate", response_model=TranslateResponse)
def translate_endpoint(request: TranslateRequest):
    """Direct text translation endpoint."""
    if not request.text.strip():
        raise HTTPException(status_code=400, detail="Text cannot be empty")
        
    try:
        translated = ai_service.translate_text(request.text, request.target_language)
        return TranslateResponse(
            translated_text=translated,
            target_language=request.target_language
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/grammar-fix", response_model=GrammarResponse)
def grammar_fix_endpoint(request: GrammarRequest):
    """Direct grammar correction endpoint."""
    if not request.text.strip():
        raise HTTPException(status_code=400, detail="Text cannot be empty")
        
    try:
        corrected = ai_service.fix_grammar(request.text)
        return GrammarResponse(corrected_text=corrected)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/generate-image", response_model=ImageResponse)
async def generate_image_endpoint(request: ImageRequest):
    """Generates an image using Pollinations AI, saves it, and returns the URL."""
    if not request.prompt.strip():
        raise HTTPException(status_code=400, detail="Prompt cannot be empty")

    try:
        # URL-encode the prompt
        encoded_prompt = urllib.parse.quote(request.prompt)
        pollinations_url = f"https://image.pollinations.ai/prompt/{encoded_prompt}?width=1024&height=1024&nologo=true&private=true"
        
        # Save image locally
        filename = f"gen_{uuid.uuid4().hex[:8]}.jpg"
        filepath = os.path.join(settings.STORAGE_DIR, filename)

        async with httpx.AsyncClient() as client:
            response = await client.get(pollinations_url, timeout=30.0)
            if response.status_code == 200:
                with open(filepath, "wb") as f:
                    f.write(response.content)
            else:
                raise HTTPException(status_code=500, detail="Failed to fetch image from generator")

        # Return static url
        local_url = f"http://localhost:8000/storage/{filename}"
        return ImageResponse(image_url=local_url, prompt=request.prompt)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Image generation failed: {str(e)}")

@router.post("/generate-video", response_model=VideoResponse)
async def generate_video_endpoint(request: VideoRequest):
    """Generates a 3-scene storyboard containing custom images and scripts."""
    if not request.prompt.strip():
        raise HTTPException(status_code=400, detail="Prompt cannot be empty")

    try:
        # Use AI to plan 3 scenes
        planning_prompt = (
            f"You are an AI Video Producer. Create a short 3-scene video script based on the prompt: '{request.prompt}'.\n"
            "Format the output exactly as a JSON list of scenes (do not include markdown wrapping), where each scene has 'scene_number' (integer), "
            "'narration' (voiceover text), and 'visual_prompt' (a detailed description of what should be shown visually in the scene, max 20 words).\n"
            "Example format:\n"
            "[\n"
            "  {\"scene_number\": 1, \"narration\": \"Narration 1\", \"visual_prompt\": \"visual description 1\"},\n"
            "  {\"scene_number\": 2, \"narration\": \"Narration 2\", \"visual_prompt\": \"visual description 2\"},\n"
            "  {\"scene_number\": 3, \"narration\": \"Narration 3\", \"visual_prompt\": \"visual description 3\"}\n"
            "]"
        )
        
        # Generate text storyboard structure
        import json
        storyboard_json = None
        
        # Call Gemini or fallback mock
        if ai_service.use_mock:
            storyboard_json = [
                {
                    "scene_number": 1, 
                    "narration": f"Welcome to this visual story about {request.prompt}. We begin by looking at the core concept.",
                    "visual_prompt": f"Dramatic cinematic shot representing {request.prompt}"
                },
                {
                    "scene_number": 2, 
                    "narration": "As we dive deeper, the details unfold showing dynamic changes and innovation.",
                    "visual_prompt": f"Close up high-tech glowing interface showing data of {request.prompt}"
                },
                {
                    "scene_number": 3, 
                    "narration": "Finally, we see the future vision—bringing global connectivity and smart technology to life.",
                    "visual_prompt": f"Futuristic city landscape with warm sunrise representing {request.prompt}"
                }
            ]
        else:
            try:
                raw_response = ai_service.generate_chat_response(
                    messages=[{"role": "user", "content": planning_prompt}]
                )
                # Parse JSON out of response
                # Clean up markdown formatting if the model output it
                clean_response = raw_response.strip()
                if clean_response.startswith("```json"):
                    clean_response = clean_response[7:]
                if clean_response.endswith("```"):
                    clean_response = clean_response[:-3]
                clean_response = clean_response.strip()
                storyboard_json = json.loads(clean_response)
            except Exception as e:
                print(f"Failed to parse AI storyboard JSON: {e}, falling back to mock")
                storyboard_json = [
                    {"scene_number": 1, "narration": f"Scene 1: Introducing {request.prompt}", "visual_prompt": f"Concept shot of {request.prompt}"},
                    {"scene_number": 2, "narration": "Scene 2: Exploring the key mechanisms.", "visual_prompt": f"Detailed diagram of {request.prompt}"},
                    {"scene_number": 3, "narration": f"Scene 3: The ultimate impact of {request.prompt}.", "visual_prompt": f"Panoramic futuristic view of {request.prompt}"}
                ]

        # Fetch images for each scene asynchronously
        storyboard_scenes = []
        async with httpx.AsyncClient() as client:
            for scene in storyboard_json:
                visual_prompt = scene.get("visual_prompt", f"Scene representing {request.prompt}")
                encoded_prompt = urllib.parse.quote(visual_prompt)
                pollinations_url = f"https://image.pollinations.ai/prompt/{encoded_prompt}?width=1024&height=576&nologo=true&private=true"
                
                filename = f"vid_{uuid.uuid4().hex[:8]}_s{scene.get('scene_number')}.jpg"
                filepath = os.path.join(settings.STORAGE_DIR, filename)
                
                try:
                    response = await client.get(pollinations_url, timeout=30.0)
                    if response.status_code == 200:
                        with open(filepath, "wb") as f:
                            f.write(response.content)
                        image_url = f"http://localhost:8000/storage/{filename}"
                    else:
                        image_url = "https://images.unsplash.com/photo-1618005182384-a83a8bd57fbe"
                except Exception as e:
                    print(f"Failed to fetch image for scene: {e}")
                    image_url = "https://images.unsplash.com/photo-1618005182384-a83a8bd57fbe"

                storyboard_scenes.append(
                    StoryboardScene(
                        scene_number=scene.get("scene_number", 1),
                        narration=scene.get("narration", ""),
                        visual_prompt=visual_prompt,
                        image_url=image_url,
                        duration=5
                    )
                )

        video_title = f"Story of {request.prompt[:30]}"
        return VideoResponse(
            prompt=request.prompt,
            title=video_title,
            storyboard=storyboard_scenes
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Video generation failed: {str(e)}")
