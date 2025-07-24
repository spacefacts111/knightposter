import os
import json
import datetime
import random
import shutil
from moviepy.editor import ImageClip, AudioFileClip, CompositeVideoClip, TextClip
import soundfile as sf
from instagrapi import Client

# ====== CONFIG ======
GENERATED_DIR = "generated"
FALLBACK_DIR = "fallbacks"
LAST_POST_FILE = "last_post.json"
VIDEO_DURATION = 15  # seconds
RESOLUTION = (1080, 1920)
FONT_SIZE = 80
FONT_COLOR = "white"

# Instagram login
USERNAME = "YOUR_IG_USERNAME"
PASSWORD = "YOUR_IG_PASSWORD"

# ====== UTILITIES ======
def cleanup_old_files():
    if os.path.exists(GENERATED_DIR):
        shutil.rmtree(GENERATED_DIR)
    os.makedirs(GENERATED_DIR, exist_ok=True)

def validate_audio(audio_path):
    try:
        data, _ = sf.read(audio_path)
        if len(data) < 1000:
            raise Exception("Audio too short or invalid")
        return True
    except:
        return False

def get_fallback_image():
    return os.path.join(FALLBACK_DIR, random.choice([
        "fallback_rain.jpg",
        "fallback_city.jpg",
        "fallback_clouds.jpg"
    ]))

def get_fallback_audio():
    return os.path.join(FALLBACK_DIR, "fallback_ambient.wav")

# ====== SCHEDULER ======
def create_new_schedule(today, first_run=False):
    posts_today = random.randint(1, 3)
    times = sorted([random.randint(9*60, 23*60) for _ in range(posts_today)])
    schedule = [f"{t//60:02d}:{t%60:02d}" for t in times]

    if first_run:
        immediate_time = datetime.datetime.now().strftime("%H:%M")
        data = {"date": today, "schedule": schedule, "done": [immediate_time]}
        print(f"✅ First run: Posting immediately, rest scheduled for today: {schedule}")
    else:
        data = {"date": today, "schedule": schedule, "done": []}
        print(f"✅ New schedule for today: {schedule}")

    with open(LAST_POST_FILE, "w") as f:
        json.dump(data, f)
    return data

def load_schedule():
    today = datetime.date.today().isoformat()
    if not os.path.exists(LAST_POST_FILE):
        return create_new_schedule(today, first_run=True)
    with open(LAST_POST_FILE, "r") as f:
        data = json.load(f)
    if data.get("date") != today:
        return create_new_schedule(today, first_run=True)
    return data

def save_done_time(time_str):
    with open(LAST_POST_FILE, "r") as f:
        data = json.load(f)
    data["done"].append(time_str)
    with open(LAST_POST_FILE, "w") as f:
        json.dump(data, f)

def should_post_now():
    now = datetime.datetime.now().strftime("%H:%M")
    schedule = load_schedule()
    if now in schedule["schedule"] and now not in schedule["done"]:
        save_done_time(now)
        return True
    return False

# ====== GENERATION (Replace with your AI functions) ======
def generate_image():
    try:
        # <<< Your AI image generation code >>>
        return "generated/ai_image.jpg"  # replace with actual generated image
    except:
        return None

def generate_music():
    try:
        # <<< Your AI music generation code >>>
        return "generated/ai_music.wav"  # replace with actual generated audio
    except:
        return None

def generate_caption():
    return random.choice([
        "Some nights feel heavier than others.",
        "You ever miss people who were never really yours?",
        "Love is just a promise we’re all scared to keep."
    ])

# ====== VIDEO CREATION ======
def create_video(image_path, audio_path, caption):
    video_path = os.path.join(GENERATED_DIR, "final_video.mp4")

    img_clip = ImageClip(image_path).set_duration(VIDEO_DURATION).resize(RESOLUTION)
    txt_clip = TextClip(caption, fontsize=FONT_SIZE, color=FONT_COLOR, method='caption',
                        size=(900, None)).set_duration(VIDEO_DURATION).set_position(("center", "bottom"))

    audio_clip = AudioFileClip(audio_path).subclip(0, VIDEO_DURATION)
    final = CompositeVideoClip([img_clip, txt_clip])
    final = final.set_audio(audio_clip)
    final.write_videofile(video_path, fps=24, codec="libx264", audio_codec="aac")

    return video_path

# ====== INSTAGRAM POSTING ======
def upload_instagram_reel(video_path, caption):
    cl = Client()
    cl.login(USERNAME, PASSWORD)
    cl.video_upload(video_path, caption)

# ====== BOT RUN ======
def run_bot():
    cleanup_old_files()

    img = generate_image()
    if not img or not os.path.exists(img):
        img = get_fallback_image()

    music = generate_music()
    if not music or not os.path.exists(music) or not validate_audio(music):
        music = get_fallback_audio()

    caption = generate_caption()

    print(f"✅ Using image: {img}")
    print(f"✅ Using music: {music}")
    print(f"✅ Caption: {caption}")

    video = create_video(img, music, caption)
    upload_instagram_reel(video, caption)
    print("✅ Posted successfully!")

# ====== MAIN ======
if __name__ == "__main__":
    schedule = load_schedule()
    now = datetime.datetime.now().strftime("%H:%M")

    # Immediate test post if first run of the day
    if schedule["done"] == [now]:
        print("✅ First run today – posting test post now!")
        run_bot()
    elif should_post_now():
        run_bot()
    else:
        print("✅ Not time yet. Waiting for next scheduled slot.")
