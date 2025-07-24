import os
import random
import json
import requests
from PIL import Image
from io import BytesIO
from moviepy.editor import ImageClip, AudioFileClip, CompositeVideoClip, TextClip
from instagrapi import Client
from gpt4all import GPT4All
import ffmpeg
import time

IMAGE_SAVE_PATH = "generated_image.jpg"
MUSIC_SAVE_PATH = "generated_music.mp3"
VIDEO_SAVE_PATH = "final_video.mp4"
QUOTES_FILE = "quotes.json"
SESSION_FILE = "session.json"
VIDEO_DURATION = 15
RESOLUTION = (1080, 1920)
CAPTIONS_MODEL = "gpt4all-falcon-newbpe-q4_0.gguf"
FONT_PATH = "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"

def generate_image():
    print("🎨 Generating image...")
    img_url = "https://picsum.photos/1080/1920"
    response = requests.get(img_url)
    if response.status_code == 200:
        img = Image.open(BytesIO(response.content)).convert("RGB")
        img.save(IMAGE_SAVE_PATH, "JPEG")
        print(f"✅ Image saved at {IMAGE_SAVE_PATH}")
    else:
        raise Exception("❌ Failed to generate image.")

def generate_music():
    print("🎵 Generating music...")
    music_url = "https://cdn.pixabay.com/download/audio/2023/01/30/audio_example.mp3"
    r = requests.get(music_url)
    with open(MUSIC_SAVE_PATH, "wb") as f:
        f.write(r.content)
    print(f"✅ Music saved at {MUSIC_SAVE_PATH}")

def generate_caption():
    print("✍️ Generating caption...")
    try:
        model = GPT4All(CAPTIONS_MODEL)
        prompt = "Give me a short sad relatable poetic quote for Instagram."
        caption = model.generate(prompt, max_tokens=50).strip()
        if not caption or len(caption) < 5:
            raise ValueError
        print(f"✅ Generated caption: {caption}")
        return caption
    except:
        print("⚠️ Using backup quotes.json")
        if os.path.exists(QUOTES_FILE):
            with open(QUOTES_FILE, "r") as f:
                quotes = json.load(f)
            return random.choice(quotes)
        else:
            return "Some things hurt more in silence."

def create_video(image_path, music_path, caption):
    print("🎬 Creating video...")
    try:
        img = Image.open(image_path)
        img.verify()
    except:
        raise Exception("❌ Image invalid or corrupted.")

    img_clip = ImageClip(image_path).set_duration(VIDEO_DURATION).resize(RESOLUTION)
    audio_clip = AudioFileClip(music_path).volumex(0.5)

    text_clip = TextClip(
        caption,
        fontsize=60,
        font=FONT_PATH,
        color="white",
        size=(900, None),
        method="caption",
    ).set_position(("center", "bottom")).set_duration(VIDEO_DURATION)

    final_clip = CompositeVideoClip([img_clip, text_clip]).set_audio(audio_clip)
    final_clip.write_videofile(
        VIDEO_SAVE_PATH, fps=30, codec="libx264", audio_codec="aac"
    )
    print(f"✅ Video saved at {VIDEO_SAVE_PATH}")
    return VIDEO_SAVE_PATH

def upload_instagram_reel(video_path, caption):
    print("📤 Uploading to Instagram...")
    cl = Client()
    if os.path.exists(SESSION_FILE):
        cl.load_settings(SESSION_FILE)
        try:
            cl.get_timeline_feed()
            print("✅ Logged in with saved session.")
        except:
            os.remove(SESSION_FILE)
    if not os.path.exists(SESSION_FILE):
        cl.login("YOUR_USERNAME", "YOUR_PASSWORD")
        cl.dump_settings(SESSION_FILE)
    try:
        cl.clip_upload(video_path, caption)
        print("✅ Reel uploaded successfully!")
    except Exception as e:
        print(f"❌ Upload failed: {e}")

def run_bot():
    try:
        generate_image()
        generate_music()
        caption = generate_caption()
        video = create_video(IMAGE_SAVE_PATH, MUSIC_SAVE_PATH, caption)
        upload_instagram_reel(video, caption)
        print("🎉 Bot run complete!")
    except Exception as e:
        print(f"❌ Bot crashed: {e}")

if __name__ == "__main__":
    run_bot()
