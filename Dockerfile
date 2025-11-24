FROM runpod/pytorch:2.4.0-py3.11-cuda12.4.1-devel-ubuntu22.04

WORKDIR /app

# Install Python dependencies
COPY requirements-server.txt .
RUN pip install --no-cache-dir -r requirements-server.txt

# Pre-download the JoyCaption model during build (download files only, don't load into memory)
RUN huggingface-cli download fancyfeast/llama-joycaption-alpha-two-hf-llava

# Copy handler
COPY handler.py .

# Set entrypoint
CMD ["python3", "-u", "handler.py"]
