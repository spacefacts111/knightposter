import os
import random
import json
import subprocess
from PIL import Image, ImageDraw, ImageFont
from gpt4all import GPT4All

# ===== CONFIG =====
SESSION_FILE = "session.json"  # Must contain {"sessionid": "YOUR_SESSION_ID"}
CAPTIONS_MODEL = "ggml-gpt4all-j-v1.3-groovy.bin"
QUOTES_FILE = "quotes.json"
VIDEO_OUTPUT = "final_video.mp4"
IMAGE_FILE = "temp_image.jpg"
AUDIO_FILE = "temp_audio.mp3"

# ===== IMAGE GENERATION =====
def generate_image():
    img = Image.new("RGB", (1080, 1350), color=(0, 0, 0))
    draw = ImageDraw.Draw(img)
    font = ImageFont.load_default()
    quote = get_caption_text()
    wrapped_text = "\n".join([quote[i:i+40] for i in range(0, len(quote), 40)])
    draw.text((50, 400), wrapped_text, fill=(255, 255, 255), font=font)
    img.save(IMAGE_FILE, "JPEG")
    print("✅ Image generated successfully.")

# ===== AI MUSIC GENERATION =====
def generate_music():
    freq = random.choice([220, 440, 880])
    subprocess.run([
        "ffmpeg", "-y", "-f", "lavfi",
        "-i", f"sine=frequency={freq}:duration=15",
        AUDIO_FILE
    ])
    print("✅ Music generated successfully.")

# ===== CAPTIONS & HASHTAGS =====
def get_caption_text():
    try:
        if os.path.exists(CAPTIONS_MODEL):
            model = GPT4All(CAPTIONS_MODEL)
            prompt = "Write a short sad relatable quote for Instagram:"
            output = model.generate(prompt, max_tokens=30)
            return output.strip()
        else:
            return random.choice(load_quotes())
    except:
        return random.choice(load_quotes())

def load_quotes():
    with open(QUOTES_FILE, "r") as f:
        return json.load(f)

def generate_hashtags():
    return "#sad #relatable #poetry #darkquotes #emo"

# ===== VIDEO CREATION =====
def create_video():
    subprocess.run([
        "ffmpeg", "-y",
        "-loop", "1", "-i", IMAGE_FILE,
        "-i", AUDIO_FILE,
        "-vf", "scale=1080:1920,format=yuv420p,eq=contrast=1.2:saturation=0.8",
        "-c:v", "libx264", "-tune", "film",
        "-c:a", "aac",
        "-shortest", VIDEO_OUTPUT
    ])
    print("✅ Video created successfully.")

# ===== INSTAGRAM POSTING (COOKIES METHOD) =====
def upload_instagram_reel(video_path, caption):
    try:
        from instagrapi import Client

        # Load session ID from session.json
        with open(SESSION_FILE, "r") as f:
            session_data = json.load(f)

        sessionid = session_data.get("sessionid")
        if not sessionid:
            raise Exception("No sessionid found in session.json!")

        cl = Client()
        cl.login_by_sessionid(sessionid)
        cl.clip_upload(video_path, caption)
        print("✅ Posted to Instagram successfully!")
    except Exception as e:
        raise Exception(f"❌ Instagram post failed: {e}")

# ===== RUN BOT =====
def run_once():
    print("\n=== 🚀 Starting Bot Run ===")
    generate_image()
    generate_music()
    create_video()
    caption = f"{get_caption_text()}\n\n{generate_hashtags()}"
    upload_instagram_reel(VIDEO_OUTPUT, caption)
    print("✅ All done.")

if __name__ == "__main__":
    run_once()
