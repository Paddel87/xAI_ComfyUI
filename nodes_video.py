import requests
import time
import os
import io
import base64
import numpy as np
import torch
import folder_paths
import random

class GrokVideo:
    def __init__(self):
        pass

    @classmethod
    def INPUT_TYPES(s):
        return {
            "required": {
                "prompt": ("STRING", {"multiline": True}),
                "api_key": ("STRING", {"multiline": False, "default": ""}),
                "model": ("STRING", {"default": "grok-imagine-video"}),
                "duration": ("FLOAT", {"default": 5.0, "min": 1.0, "max": 10.0, "step": 0.1}),
                "aspect_ratio": (["16:9", "1:1", "9:16", "4:3", "3:4"], {"default": "16:9"}),
                "resolution": (["720p", "480p"], {"default": "720p"}),
                "polling_interval": ("FLOAT", {"default": 2.0, "min": 0.5, "max": 10.0, "step": 0.5}),
                "timeout": ("INT", {"default": 300, "min": 60, "max": 1200}),
                "dry_run": ("BOOLEAN", {"default": False, "label_on": "Enable Dry Run (Cost Estimate)", "label_off": "Disable Dry Run"}),
            },
            "optional": {
                "image_start": ("IMAGE",),
                "image_end": ("IMAGE",), # For future support or if API supports it
            }
        }

    RETURN_TYPES = ("STRING", "STRING")
    RETURN_NAMES = ("video_path", "cost_info")
    FUNCTION = "generate_video"
    CATEGORY = "xAI/Grok"

    def generate_video(self, prompt, api_key, model, duration, aspect_ratio, resolution, polling_interval, timeout, dry_run, image_start=None, image_end=None):
        # Cost Calculation
        # Assuming pricing: 480p=$0.05/sec, 720p=$0.07/sec
        price_per_sec = 0.07 if resolution == "720p" else 0.05
        estimated_cost = duration * price_per_sec
        cost_info = f"Estimated Cost: ${estimated_cost:.2f} USD ({duration}s @ ${price_per_sec}/sec)"

        if dry_run:
            print(f"\n[GrokVideo] {cost_info}")
            return ("dry_run.mp4", cost_info)

        if not api_key:
            api_key = os.environ.get("XAI_API_KEY")
        
        if not api_key:
            raise ValueError("API Key is required.")

        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {api_key}"
        }

        # Prepare payload
        payload = {
            "model": model,
            "prompt": prompt,
            "duration": duration,
            "aspect_ratio": aspect_ratio,
            "resolution": resolution,
        }

        # Handle start image (Image-to-Video)
        if image_start is not None:
            # Take first image from batch
            img_tensor = image_start[0]
            # Convert to PIL -> Base64
            from PIL import Image
            i = 255. * img_tensor.cpu().numpy()
            img = Image.fromarray(np.clip(i, 0, 255).astype(np.uint8))
            
            buffered = io.BytesIO()
            img.save(buffered, format="JPEG")
            img_str = base64.b64encode(buffered.getvalue()).decode("utf-8")
            
            payload["image_url"] = f"data:image/jpeg;base64,{img_str}"

        # Step 1: Start Generation
        try:
            response = requests.post("https://api.x.ai/v1/videos/generations", headers=headers, json=payload, timeout=60)
            response.raise_for_status()
            data = response.json()
            request_id = data.get("request_id")
            
            if not request_id:
                raise ValueError("No request_id received from API")

        except Exception as e:
            raise RuntimeError(f"Error starting video generation: {str(e)}")

        # Step 2: Poll for Result
        start_time = time.time()
        video_url = None
        
        while time.time() - start_time < timeout:
            try:
                status_response = requests.get(f"https://api.x.ai/v1/videos/{request_id}", headers=headers, timeout=30)
                status_response.raise_for_status()
                status_data = status_response.json()
                
                status = status_data.get("status")
                
                if status == "done":
                    video_url = status_data.get("video", {}).get("url")
                    break
                elif status == "failed":
                    raise RuntimeError(f"Video generation failed: {status_data.get('error')}")
                elif status == "expired":
                     raise RuntimeError("Video generation request expired")
                
                time.sleep(polling_interval)
                
            except Exception as e:
                # If it's a transient network error, maybe continue, but for now raise
                if "404" in str(e): # Sometimes 404 means not ready yet? No, usually 200 with status=pending
                     pass
                # raise RuntimeError(f"Error polling status: {str(e)}")
        
        if not video_url:
            raise RuntimeError("Timeout waiting for video generation")

        # Step 3: Download and Save Video
        try:
            video_response = requests.get(video_url)
            video_response.raise_for_status()
            
            # Save to ComfyUI output directory
            output_dir = folder_paths.get_output_directory()
            filename = f"grok_video_{request_id}.mp4"
            file_path = os.path.join(output_dir, filename)
            
            with open(file_path, "wb") as f:
                f.write(video_response.content)
                
            return (filename, cost_info) # Return filename relative to output dir for VHS nodes or preview

        except Exception as e:
            raise RuntimeError(f"Error downloading video: {str(e)}")

# Node class mappings
NODE_CLASS_MAPPINGS = {
    "GrokVideo": GrokVideo
}

# Node display name mappings
NODE_DISPLAY_NAME_MAPPINGS = {
    "GrokVideo": "Grok Video (xAI)"
}
