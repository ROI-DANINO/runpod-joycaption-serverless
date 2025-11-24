FROM runpod/pytorch:2.1.0-py3.10-cuda11.8.0-devel-ubuntu22.04

WORKDIR /app

# Install Python dependencies
COPY requirements-server.txt .
RUN pip install --no-cache-dir -r requirements-server.txt

# Pre-download the JoyCaption model during build
RUN python3 -c "from transformers import AutoProcessor, LlavaForConditionalGeneration; \
    AutoProcessor.from_pretrained('fancyfeast/llama-joycaption-alpha-two-hf-llava'); \
    LlavaForConditionalGeneration.from_pretrained('fancyfeast/llama-joycaption-alpha-two-hf-llava')"

# Copy handler
COPY handler.py .

# Set entrypoint
CMD ["python3", "-u", "handler.py"]
