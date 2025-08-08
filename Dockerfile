FROM python:3.11-slim

WORKDIR /app

# Install system dependencies first
RUN apt-get update && \
    apt-get install -y swig ffmpeg flac && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/*

COPY requirements.txt .

RUN pip install --no-cache-dir -r requirements.txt

COPY . .

EXPOSE 5000

CMD ["python", "app.py"]
