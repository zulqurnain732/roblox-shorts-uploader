import os
import re
import json
import random
import requests
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload
import gdown

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
    with open(TRACKER_FILE, "r") as f:
        uploaded_files = set(json.load(f))
else:
    uploaded_files = set()

# Public folder se items list karna
folder_url = f"https://drive.google.com/drive/folders/{FOLDER_ID}"
res = requests.get(folder_url)
html = res.text

# Extract files info from public drive folder
matches = re.findall(r'\["([-\w]{25,})",\["([^"]+\.mp4)"', html)
if not matches:
    matches = re.findall(r'\["([-\w]{25,})",\["(Copy of \d+\.mp4)"', html)

files_map = {}
for file_id, name in matches:
    if name not in files_map:
        files_map[name] = file_id

def extract_number(filename):
    nums = re.findall(r'\d+', filename)
    return int(nums[0]) if nums else 999999

# Sort files sequentially: Copy of 1.mp4, Copy of 2.mp4...
sorted_items = sorted(files_map.items(), key=lambda x: extract_number(x[0]))
pending_items = [item for item in sorted_items if item[0] not in uploaded_files]

if not pending_items:
    print("Koi nayi video pending nahi hai ya saari upload ho chuki hain.")
    exit(0)

target_name, target_id = pending_items[0]
print(f"Target Video mil gayi: {target_name} (ID: {target_id})")

# Sirf ye single video download karein
temp_video_path = "current_video.mp4"
download_url = f"https://drive.google.com/uc?id={target_id}"
print("Video download ho rahi hai...")
gdown.download(download_url, temp_video_path, quiet=False)

if not os.path.exists(temp_video_path) or os.path.getsize(temp_video_path) == 0:
    print("Download fail ho gaya, Google Drive link check karein.")
    exit(1)

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

print(f"YouTube par upload shuru: {title}")
media = MediaFileUpload(temp_video_path, chunksize=-1, resumable=True, mimetype='video/mp4')
response = youtube_service.videos().insert(
    part=','.join(body.keys()),
    body=body,
    media_body=media
).execute()

print(f"Upload complete! Video ID: {response.get('id')}")

# Clean up
if os.path.exists(temp_video_path):
    os.remove(temp_video_path)

# Tracker update
uploaded_files.add(target_name)
with open(TRACKER_FILE, "w") as f:
    json.dump(list(uploaded_files), f, indent=2)
    
