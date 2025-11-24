FROM runpod/pytorch:2.4.0-py3.11-cuda12.4.1-devel-ubuntu22.04

WORKDIR /app

# Install Python dependencies
COPY requirements-server.txt .
RUN pip install --no-cache-dir -r requirements-server.txt

# Copy handler
COPY handler.py .

# Set entrypoint
CMD ["python3", "-u", "handler.py"]
