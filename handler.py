import runpod
import torch
import base64
from io import BytesIO
from PIL import Image
from transformers import AutoProcessor, LlavaForConditionalGeneration

# Model configuration
MODEL_NAME = "fancyfeast/llama-joycaption-alpha-two-hf-llava"

# Load model and processor at container init (cached across requests)
print("Loading JoyCaption model...")
processor = AutoProcessor.from_pretrained(MODEL_NAME)
model = LlavaForConditionalGeneration.from_pretrained(
    MODEL_NAME,
    torch_dtype=torch.bfloat16,
    device_map="auto"
)
model.eval()
print("Model loaded successfully!")


def handler(job):
    """
    RunPod serverless handler for JoyCaption image captioning.

    Input:
        job["input"]["image"]: Base64 encoded image string
        job["input"]["prompt"]: (optional) Custom prompt for captioning

    Returns:
        {"caption": str}
    """
    job_input = job["input"]

    # Decode base64 image
    image_data = job_input.get("image")
    if not image_data:
        return {"error": "No image provided in input"}

    try:
        image_bytes = base64.b64decode(image_data)
        image = Image.open(BytesIO(image_bytes)).convert("RGB")
    except Exception as e:
        return {"error": f"Failed to decode image: {str(e)}"}

    # Get prompt (default to detailed description for LoRA training)
    prompt = job_input.get(
        "prompt",
        "Write a long descriptive caption for this image in a formal tone. "
        "Describe the subject, their appearance, clothing, pose, expression, "
        "and any relevant background details."
    )

    # Build conversation with chat template
    convo = [
        {"role": "system", "content": "You are a helpful image captioner."},
        {"role": "user", "content": prompt},
    ]

    # Apply chat template
    convo_string = processor.apply_chat_template(
        convo,
        tokenize=False,
        add_generation_prompt=True
    )

    # Process inputs
    inputs = processor(
        text=[convo_string],
        images=[image],
        return_tensors="pt"
    ).to(model.device)

    # Ensure pixel values are in correct dtype
    inputs['pixel_values'] = inputs['pixel_values'].to(torch.bfloat16)

    # Generate caption
    with torch.no_grad():
        generate_ids = model.generate(
            **inputs,
            max_new_tokens=300,
            do_sample=True,
            temperature=0.5,
            top_p=0.9,
        )[0]

    # Decode output (remove input tokens)
    generate_ids = generate_ids[inputs['input_ids'].shape[1]:]
    caption = processor.tokenizer.decode(generate_ids, skip_special_tokens=True)

    return {"caption": caption.strip()}


# Start the serverless handler
runpod.serverless.start({"handler": handler})
