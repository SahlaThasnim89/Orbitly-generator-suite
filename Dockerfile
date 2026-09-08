FROM python:3.11-slim

# Install ffmpeg for pydub audio processing
RUN apt-get update && apt-get install -y ffmpeg

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy all your files
COPY . .

# Expose port 8000 for Koyeb/Render
EXPOSE 8000

# Run the server on port 8000
CMD ["uvicorn", "app:app", "--host", "0.0.0.0", "--port", "8000"]