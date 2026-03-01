# xAI ComfyUI Nodes

This repository provides a set of custom nodes for ComfyUI that integrate xAI's powerful Grok API capabilities. It supports Image Generation, Image Editing, Video Generation, Video Editing, and Image Understanding (Vision).

## Features

- **Grok Imagine**: 
  - Generate high-quality images from text prompts (Text-to-Image).
  - Edit existing images using up to 3 reference images (Image-to-Image / Style Transfer / Editing).
- **Grok Video**: 
  - Generate videos from text prompts (Text-to-Video).
  - Animate static images (Image-to-Video).
  - Edit existing videos via file path (Video-to-Video).
- **Grok Vision**: 
  - Analyze images and have conversations about them (Image Understanding).

## Installation

1. Navigate to your ComfyUI `custom_nodes` directory.
2. Clone this repository:
   ```bash
   git clone https://github.com/yourusername/xAI_ComfyUI.git
   ```
3. Install the required dependencies:
   ```bash
   pip install -r requirements.txt
   ```

## Configuration

You need an xAI API Key to use these nodes. You can get one from the [xAI Console](https://console.x.ai/).

Provide your API Key in one of two ways:
1. **Environment Variable**: Set `XAI_API_KEY` in your system environment variables before starting ComfyUI.
2. **Node Input**: Enter the API Key directly in the `api_key` widget on each node.

## Usage

### 1. Grok Imagine (Image Generation & Editing)
Located under `xAI/Grok` -> `Grok Imagine (xAI)`.

- **Text-to-Image**: Simply connect the node, enter a prompt, and execute.
- **Image Editing / Style Transfer**: Connect images to the optional inputs `image_1`, `image_2`, or `image_3`. The model will use these as references for editing or style transfer based on your prompt.
- **Parameters**:
  - `prompt`: Description of the image.
  - `model`: `grok-imagine-image`.
  - `aspect_ratio`: e.g., `1:1`, `16:9`, `4:3`.
  - `num_images`: Batch size (1-4).
  - `dry_run`: Enable to estimate cost without generating.

### 2. Grok Video (Video Generation & Editing)
Located under `xAI/Grok` -> `Grok Video (xAI)`.

- **Text-to-Video**: Enter a prompt and set parameters.
- **Image-to-Video**: Connect an image to `image_start` to animate it.
- **Video-to-Video (Editing)**: Provide a local file path to an `.mp4` video in the `video_path` input. The model will edit the video based on your prompt (e.g., "Give the woman a silver necklace").
- **Parameters**:
  - `duration`: Video length in seconds (1.0 - 10.0).
  - `resolution`: `720p` or `480p`.
  - `aspect_ratio`: Video dimensions.
  - `video_path`: Absolute path to a local .mp4 file for editing.

### 3. Grok Vision (Image Understanding)
Located under `xAI/Grok` -> `Grok Vision (xAI)`.

- **Chat with Image**: Connect an image and ask a question in the `prompt`. The node returns a text description or answer.
- **Parameters**:
  - `image`: Input image to analyze.
  - `prompt`: Question or instruction (e.g., "Describe this image", "What is in the background?").
  - `model`: `grok-2-vision-1212`.

## Cost Estimation

All generation nodes include a `dry_run` option. When enabled:
1. The API is **not** called (no cost incurred).
2. The node returns a dummy output and a text string with the estimated cost (e.g., "Estimated Cost: $0.35 USD").
3. This is useful for checking pricing before running large batches.

**Estimated Pricing (Subject to Change):**
- **Image**: ~$0.07 per image.
- **Video (720p)**: ~$0.07 per second.
- **Video (480p)**: ~$0.05 per second.

## License

MIT
