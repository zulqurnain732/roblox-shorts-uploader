import os
import re
import json
import random
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload
import gdown

CLIENT_ID = os.environ.get("CLIENT_ID")
CLIENT_SECRET = os.environ.get("CLIENT_SECRET")
REFRESH_TOKEN = os.environ.get("REFRESH_TOKEN")
TRACKER_FILE = "uploaded.json"
FOLDER_URL = "https://drive.google.com/drive/folders/1nbXalCCa3umvQmrhzRogjvnSz-zMYfHj"

creds = Credentials(
    None,
    refresh_token=REFRESH_TOKEN,
    token_uri="https://oauth2.googleapis.com/token",
    client_id=CLIENT_ID,
    client_secret=CLIENT_SECRET
)

youtube_service = build('youtube', 'v3', credentials=creds)

if os.path.exists(TRACKER_FILE):
    with open(TRACKER_FILE, "r") as f:
        uploaded_files = set(json.load(f))
else:
    uploaded_files = set()

download_dir = "downloaded_videos"
os.makedirs(download_dir, exist_ok=True)
print("Google Drive se folder fetch kiya ja raha hai...")
gdown.download_folder(FOLDER_URL, output=download_dir, quiet=True, use_cookies=False)

ignored_patterns = ["1m $ earning", "400  free reels bundle", "4000 free courses"]

def extract_number(filename):
    nums = re.findall(r'\d+', filename)
    return int(nums[0]) if nums else 999999

all_files = []
for root, _, files in os.walk(download_dir):
    for f in files:
        if not f.lower().endswith(".mp4"):
            continue
        lower_name = f.lower()
        if any(ign in lower_name for ign in ignored_patterns):
            continue
        all_files.append((f, os.path.join(root, f)))

all_files.sort(key=lambda x: extract_number(x[0]))

pending_files = [item for item in all_files if item[0] not in uploaded_files]

if not pending_files:
    print("Saari videos upload ho chuki hain! Koi nayi video baki nahi hai.")
    exit(0)

# Har run me sirf 1 video
target_file_name, target_file_path = pending_files[0]
print(f"Baqi bache videos: {len(pending_files)}")
print(f"Abhi upload ho raha hai: {target_file_name}")

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

print(f"Uploading to YouTube: {title}")
media = MediaFileUpload(target_file_path, chunksize=-1, resumable=True, mimetype='video/mp4')
response = youtube_service.videos().insert(
    part=','.join(body.keys()),
    body=body,
    media_body=media
).execute()

print(f"Direct Public Upload Successful! Video ID: {response.get('id')}")

# Tracker update karein
uploaded_files.add(target_file_name)
with open(TRACKER_FILE, "w") as f:
    json.dump(list(uploaded_files), f, indent=2)
    
