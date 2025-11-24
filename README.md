# RunPod JoyCaption Serverless Handler

Serverless endpoint for image captioning using JoyCaption Alpha Two model.

## Requirements

- Docker
- RunPod account
- GPU with 24GB+ VRAM (model uses ~17GB)

## Build

```bash
cd ~/runpod-captioner
docker build -t joycaption-runpod .
```

## Push to Registry

```bash
# Docker Hub
docker tag joycaption-runpod YOUR_USERNAME/joycaption-runpod:latest
docker push YOUR_USERNAME/joycaption-runpod:latest

# Or GitHub Container Registry
docker tag joycaption-runpod ghcr.io/YOUR_USERNAME/joycaption-runpod:latest
docker push ghcr.io/YOUR_USERNAME/joycaption-runpod:latest
```

## Deploy on RunPod

1. Go to RunPod Serverless console
2. Create new endpoint
3. Set container image to your pushed image
4. Select GPU with 24GB+ VRAM (e.g., RTX 3090, RTX 4090, A5000)
5. Deploy

## API Usage

### Request

```bash
curl -X POST https://api.runpod.ai/v2/YOUR_ENDPOINT_ID/runsync \
  -H "Authorization: Bearer YOUR_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{
    "input": {
      "image": "BASE64_ENCODED_IMAGE"
    }
  }'
```

### With Custom Prompt

```bash
curl -X POST https://api.runpod.ai/v2/YOUR_ENDPOINT_ID/runsync \
  -H "Authorization: Bearer YOUR_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{
    "input": {
      "image": "BASE64_ENCODED_IMAGE",
      "prompt": "Describe this image in detail for Stable Diffusion training."
    }
  }'
```

### Response

```json
{
  "id": "sync-xxxxx",
  "status": "COMPLETED",
  "output": {
    "caption": "A detailed description of the image..."
  }
}
```

### Python Example

```python
import runpod
import base64

runpod.api_key = "YOUR_API_KEY"

# Read and encode image
with open("image.jpg", "rb") as f:
    image_b64 = base64.b64encode(f.read()).decode()

# Run inference
result = runpod.run_sync(
    "YOUR_ENDPOINT_ID",
    {"image": image_b64}
)

print(result["output"]["caption"])
```

## Model Info

- **Model**: JoyCaption Alpha Two
- **Architecture**: LLaVA (SigLIP + Llama 3.1 8B)
- **HuggingFace**: `fancyfeast/llama-joycaption-alpha-two-hf-llava`
- **Output**: Detailed captions suitable for LoRA/fine-tuning datasets
