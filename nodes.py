import requests
import json
import base64
import io
import os
import torch
import numpy as np
from PIL import Image

class GrokImagine:
    def __init__(self):
        pass

    @classmethod
    def INPUT_TYPES(s):
        return {
            "required": {
                "prompt": ("STRING", {"multiline": True}),
                "api_key": ("STRING", {"multiline": False, "default": ""}),
                "model": ("STRING", {"default": "grok-imagine-image"}),
                "aspect_ratio": (["1:1", "16:9", "4:3", "3:2", "2:3", "3:4", "9:16"], {"default": "1:1"}),
                "num_images": ("INT", {"default": 1, "min": 1, "max": 4}),
                "seed": ("INT", {"default": 0, "min": 0, "max": 0xffffffffffffffff}),
                "dry_run": ("BOOLEAN", {"default": False, "label_on": "Enable Dry Run (Cost Estimate)", "label_off": "Disable Dry Run"}),
            },
            "optional": {
                "image_optional": ("IMAGE",),
            }
        }

    RETURN_TYPES = ("IMAGE", "STRING")
    RETURN_NAMES = ("image", "cost_info")
    FUNCTION = "generate"
    CATEGORY = "xAI/Grok"

    def generate(self, prompt, api_key, model, aspect_ratio, num_images, seed, dry_run, image_optional=None):
        # Cost Calculation
        price_per_image = 0.07 # Estimated price
        estimated_cost = num_images * price_per_image
        cost_info = f"Estimated Cost: ${estimated_cost:.2f} USD ({num_images} images @ ${price_per_image}/img)"

        if dry_run:
            print(f"\n[GrokImagine] {cost_info}")
            # Return dummy image (black 512x512)
            dummy_tensor = torch.zeros((1, 512, 512, 3), dtype=torch.float32)
            return (dummy_tensor, cost_info)

        if not api_key:
            api_key = os.environ.get("XAI_API_KEY")
        
        if not api_key:
            raise ValueError("API Key is required. Please provide it in the node or set XAI_API_KEY environment variable.")

        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {api_key}"
        }

        # Based on documentation, xAI supports aspect_ratio parameter
        payload = {
            "model": model,
            "prompt": prompt,
            "n": num_images,
            "response_format": "b64_json", # Use base64 to avoid downloading
            "aspect_ratio": aspect_ratio,
        }
        
        # Handle optional image input (Image-to-Image / Style Transfer)
        if image_optional is not None:
            # ComfyUI passes image as tensor [B, H, W, C], float32, 0-1
            # We take the first image in the batch
            img_tensor = image_optional[0]
            
            # Convert tensor to PIL Image
            # Ensure it's in 0-255 range and uint8
            i = 255. * img_tensor.cpu().numpy()
            img = Image.fromarray(np.clip(i, 0, 255).astype(np.uint8))
            
            # Convert PIL Image to base64
            buffered = io.BytesIO()
            img.save(buffered, format="JPEG")
            img_str = base64.b64encode(buffered.getvalue()).decode("utf-8")
            
            # Add to payload
            payload["image_url"] = f"data:image/jpeg;base64,{img_str}"
            
            # Note: documentation says aspect_ratio follows input image when editing
            # but we leave aspect_ratio in payload as it might be required or ignored safely.
  
 
        try:
            response = requests.post("https://api.x.ai/v1/images/generations", headers=headers, json=payload, timeout=60)
            response.raise_for_status()
            data = response.json()
            
            images = []
            if "data" in data:
                for item in data["data"]:
                    if "b64_json" in item:
                        image_data = base64.b64decode(item["b64_json"])
                        img = Image.open(io.BytesIO(image_data))
                        images.append(img)
                    elif "url" in item:
                        image_url = item["url"]
                        img_response = requests.get(image_url)
                        img = Image.open(io.BytesIO(img_response.content))
                        images.append(img)
            
            if not images:
                raise ValueError("No images returned from API")

            # Convert to Tensor
            image_tensors = []
            for img in images:
                img = img.convert("RGB")
                img_np = np.array(img).astype(np.float32) / 255.0
                image_tensors.append(torch.from_numpy(img_np))
            
            # Stack images into a batch [B, H, W, C]
            if len(image_tensors) > 1:
                batch_tensor = torch.stack(image_tensors)
            else:
                batch_tensor = image_tensors[0].unsqueeze(0)
            
            return (batch_tensor, cost_info)

        except Exception as e:
            raise RuntimeError(f"Error generating image: {str(e)}")

# Node class mappings
NODE_CLASS_MAPPINGS = {
    "GrokImagine": GrokImagine
}

# Node display name mappings
NODE_DISPLAY_NAME_MAPPINGS = {
    "GrokImagine": "Grok Imagine (xAI)"
}
