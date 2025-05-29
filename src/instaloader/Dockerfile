FROM python:3.11-slim
ENV PYTHONUNBUFFERED=1

WORKDIR /app
RUN apt-get update \
    && apt-get install -y --no-install-recommends ffmpeg \
    && pip install instaloader flask gunicorn \
    && rm -rf /var/lib/apt/lists/*

COPY app.py .

USER 1000

CMD ["gunicorn","--bind","0.0.0.0:5633","--access-logfile","-","--error-logfile","-","app:app"]
