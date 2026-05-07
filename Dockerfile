FROM python:3.11-slim

# Set up user to run without root privileges (Required for Hugging Face Spaces)
RUN useradd -m -u 1000 user
ENV HOME=/home/user \
    PATH=/home/user/.local/bin:$PATH

# Install system dependencies (Tesseract OCR for image parsing)
RUN apt-get update && apt-get install -y \
    tesseract-ocr \
    libgl1-mesa-glx \
    && rm -rf /var/lib/apt/lists/*

# Set working directory
WORKDIR $HOME/app
RUN chown user:user $HOME/app

# Switch to the non-root user
USER user

# Copy requirements and install
COPY --chown=user:user backend/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy the backend code
COPY --chown=user:user backend/ .

# Expose port 7860 (Required by Hugging Face)
EXPOSE 7860

# Run FastAPI server
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "7860"]
