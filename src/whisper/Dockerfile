FROM python:3.11-slim

WORKDIR /app
RUN apt-get update && apt-get install -y ffmpeg
RUN pip install faster-whisper flask

COPY app.py .

CMD ["python", "app.py"]
