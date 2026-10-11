import os
import re
import json
import random
import subprocess
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload

CLIENT_ID = os.environ.get("CLIENT_ID")
CLIENT_SECRET = os.environ.get("CLIENT_SECRET")
REFRESH_TOKEN = os.environ.get("REFRESH_TOKEN")
TRACKER_FILE = "uploaded.json"
FOLDER_ID = "1nbXalCCa3umvQmrhzRogjvnSz-zMYfHj"

creds = Credentials(
    None,
    refresh_token=REFRESH_TOKEN,
    token_uri="https://oauth2.googleapis.com/token",
    client_id=CLIENT_ID,
    client_secret=CLIENT_SECRET
)

youtube_service = build('youtube', 'v3', credentials=creds)

if os.path.exists(TRACKER_FILE):
    try:
        with open(TRACKER_FILE, "r") as f:
            uploaded_files = set(json.load(f))
    except Exception:
        uploaded_files = set()
else:
    uploaded_files = set()

# Download directory setup
os.makedirs("downloads", exist_ok=True)

# Google Drive public folder se files download karne ke liye gdown direct call
print("Checking and downloading Google Drive files...")
subprocess.run([
    "gdown",
    f"https://drive.google.com/drive/folders/{FOLDER_ID}",
    "-O", "downloads/",
    "--folder",
    "--remaining-ok"
], check=False)

ignored_patterns = ["1m $ earning", "400  free reels bundle", "4000 free courses"]

def extract_number(filename):
    nums = re.findall(r'\d+', filename)
    return int(nums[0]) if nums else 999999

all_found = []
for root, _, files in os.walk("downloads"):
    for f in files:
        if not f.lower().endswith(".mp4"):
            continue
        lower_name = f.lower()
        if any(ign in lower_name for ign in ignored_patterns):
            continue
        all_found.append((f, os.path.join(root, f)))

all_found.sort(key=lambda x: extract_number(x[0]))
pending = [item for item in all_found if item[0] not in uploaded_files]

print(f"Total milne wale videos: {len(all_found)}")
print(f"Baqi bache hue videos: {len(pending)}")

if not pending:
    print("Koi nayi video upload ke liye nahi mili!")
    exit(0)

target_name, target_path = pending[0]
print(f"Abhi upload ho rahi hai: {target_name}")

roblox_titles = [
    "Most Insane Roblox Moment! 😱 #roblox #shorts",
    "Only 1% Can Beat This Roblox Obby! 🔥 #roblox #shorts",
    "Roblox Funniest Gameplay Ever 😂 #roblox #shorts",
    "You Won't Believe What Happened in Roblox! 🤯 #roblox #shorts",
    "Crazy Roblox Glitch You Must Try! 🎮 #roblox #shorts",
    "Roblox Pro vs Noob Moment 💀 #roblox #shorts",
    "Top Secret Roblox Trick Revealed! ⚡ #roblox #shorts",
    "Roblox Impossible Challenge Cleared! 🏆 #roblox #shorts",
    "Best Roblox Avatar & Animation! ✨ #roblox #shorts",
    "Roblox Chaos at its Peak! 🚀 #roblox #shorts"
]

description_text = """Check out this epic Roblox gameplay! 🎮
Subscribe for more daily Roblox Shorts and gaming moments.

#roblox #robloxshorts #gaming #robloxtrend #shorts #viral"""

tags_list = ["roblox", "roblox shorts", "roblox funny moments", "gaming", "shorts", "roblox gameplay", "trending"]

title = random.choice(roblox_titles)
body = {
    'snippet': {
        'title': title,
        'description': description_text,
        'tags': tags_list,
        'categoryId': '20'
    },
    'status': {
        'privacyStatus': 'public'
    }
}

print(f"YouTube par upload jaari hai: {title}")
media = MediaFileUpload(target_path, chunksize=-1, resumable=True, mimetype='video/mp4')
response = youtube_service.videos().insert(
    part=','.join(body.keys()),
    body=body,
    media_body=media
).execute()

print(f"Success! Video upload ho chuki hai. Video ID: {response.get('id')}")

# Tracker file update
uploaded_files.add(target_name)
with open(TRACKER_FILE, "w") as f:
    json.dump(list(uploaded_files), f, indent=2)

# File delete karein taaki storage clean rahe
if os.path.exists(target_path):
    os.remove(target_path)
