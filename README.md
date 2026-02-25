# xAI ComfyUI Node

This is a custom node for ComfyUI that allows you to generate images using xAI's Grok Imagine model.

## Installation

1. Navigate to your ComfyUI `custom_nodes` directory.
2. Clone this repository:
   ```bash
   git clone https://github.com/yourusername/xAI_ComfyUI.git
   ```
   (Or just copy the folder `xAI_ComfyUI` into `custom_nodes`)
3. Install the requirements:
   ```bash
   pip install -r requirements.txt
   ```

## Configuration

You can provide your xAI API Key in two ways:
1. **Environment Variable**: Set `XAI_API_KEY` in your environment variables before starting ComfyUI.
2. **Node Input**: Enter the API Key directly in the node's `api_key` field.

To get an API key, visit the [xAI Console](https://console.x.ai/).

## Usage

1. **Grok Imagine (Image)**:
   - Find under `xAI/Grok` -> `Grok Imagine (xAI)`.
   - Connect `IMAGE` output to save/preview.
   - Optional: Connect `image_optional` for editing.

2. **Grok Video (Video)**:
   - Find under `xAI/Grok` -> `Grok Video (xAI)`.
   - Generates video from prompt or image.
   - Returns a path to the saved video file (use with VHS nodes or similar).
   - **Parameters**:
     - `duration`: Length of video in seconds (default 5.0, max 10.0).
     - `resolution`: 720p or 480p.
     - `aspect_ratio`: 16:9, 1:1, etc.
     - `image_start`: (Optional) Start video from an image.
     - `dry_run`: Enable to check estimated cost without generating.

## Cost Estimation

Both nodes include a `dry_run` option. When enabled:
1. The API is **not** called (no cost incurred).
2. The node outputs an estimated cost string (e.g., "Estimated Cost: $0.35 USD").
3. Check the ComfyUI Console/Log for the cost details.
4. Returns dummy output to keep the workflow valid.

**Estimated Pricing (Subject to Change):**
- **Image**: ~$0.07 per image.
- **Video (720p)**: ~$0.07 per second.
- **Video (480p)**: ~$0.05 per second.

## Parameters

### Image Node
- **prompt**: The text description of the image you want to generate.
- **api_key**: Your xAI API key (optional if set in env vars).
- **model**: The model to use (default: `grok-imagine-image`).
- **aspect_ratio**: Aspect ratio of the generated image (e.g., `1:1`, `16:9`).
- **num_images**: Number of images to generate in one batch (1-4).
- **seed**: Seed for randomization.
- **image_optional**: (Optional) Input image for editing or style transfer.
- **dry_run**: Toggle to preview cost without spending credits.

### Video Node
- **prompt**: Description of the video or animation.
- **duration**: Duration in seconds (1.0 - 10.0).
- **resolution**: Video quality (720p recommended).
- **aspect_ratio**: Video dimensions.
- **image_start**: (Optional) Image to animate.
- **dry_run**: Toggle to preview cost.

## License

MIT
