FROM python:3.10
WORKDIR /app
RUN apt-get update && apt-get install -y ffmpeg fonts-dejavu
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY . .
CMD ["python", "main.py"]
