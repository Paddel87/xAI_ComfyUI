import requests
import json
import base64
import io
import os
import torch
import numpy as np
from PIL import Image

class GrokVision:
    def __init__(self):
        pass

    @classmethod
    def INPUT_TYPES(s):
        return {
            "required": {
                "image": ("IMAGE",),
                "prompt": ("STRING", {"multiline": True, "default": "Describe this image"}),
                "api_key": ("STRING", {"multiline": False, "default": ""}),
                "model": ("STRING", {"default": "grok-2-vision-1212"}),
            }
        }

    RETURN_TYPES = ("STRING",)
    RETURN_NAMES = ("text",)
    FUNCTION = "chat_with_image"
    CATEGORY = "xAI/Grok"

    def chat_with_image(self, image, prompt, api_key, model):
        if not api_key:
            api_key = os.environ.get("XAI_API_KEY")
        
        if not api_key:
            raise ValueError("API Key is required.")

        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {api_key}"
        }

        # Prepare message content
        content = []
        
        # Add images
        # image is a batch tensor [B, H, W, C]
        for img_tensor in image:
            # Convert tensor to PIL Image
            i = 255. * img_tensor.cpu().numpy()
            img = Image.fromarray(np.clip(i, 0, 255).astype(np.uint8))
            
            # Convert to base64
            buffered = io.BytesIO()
            img.save(buffered, format="JPEG")
            img_str = base64.b64encode(buffered.getvalue()).decode("utf-8")
            
            content.append({
                "type": "image_url",
                "image_url": {
                    "url": f"data:image/jpeg;base64,{img_str}",
                    "detail": "high"
                }
            })

        # Add text prompt
        content.append({
            "type": "text",
            "text": prompt
        })

        payload = {
            "model": model,
            "messages": [
                {
                    "role": "user",
                    "content": content
                }
            ],
            "stream": False,
            "temperature": 0.01
        }

        try:
            response = requests.post("https://api.x.ai/v1/chat/completions", headers=headers, json=payload, timeout=60)
            response.raise_for_status()
            data = response.json()
            
            if "choices" in data and len(data["choices"]) > 0:
                result_text = data["choices"][0]["message"]["content"]
                return (result_text,)
            else:
                raise ValueError("No response content from API")

        except Exception as e:
            raise RuntimeError(f"Error calling Vision API: {str(e)}")

NODE_CLASS_MAPPINGS = {
    "GrokVision": GrokVision
}

NODE_DISPLAY_NAME_MAPPINGS = {
    "GrokVision": "Grok Vision (xAI)"
}
