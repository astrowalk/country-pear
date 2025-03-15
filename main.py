import json
import time
import os
import requests
import isodate
from datetime import datetime, timedelta, timezone
from colorama import Fore, Style, init, Back

# initialize colorama
init(autoreset=True)

os.system("cls")
# load api key and requested data fields from config.json
CONFIG_FILE = "config.json"
CHANNELS_FILE = "channels.json"
RESULTS_FILE = "results.json"
PRINTED_VIDEOS = set()
LATEST_VIDEO_TRACKER = {}

def log(message, color=Fore.WHITE):
    timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    print(f"{color}[{timestamp}] {message}")

def load_config():
    if os.path.exists(CONFIG_FILE):
        with open(CONFIG_FILE, "r", encoding="utf-8") as f:
            config = json.load(f)
            return (
                config.get("API_KEY", ""),
                config.get("DATA_FIELDS", []),
                config.get("INCLUDE_SHORTS", True),
                config.get("CHECK_DELAY", 5),  # Default to 5 hours
                config.get("CHANNEL_DELAY", 12)  # Default to 12 hours before rechecking a channel
            )
    log("error: config.json not found or missing api_key", Fore.RED)
    return "", [], True, 5, 12

API_KEY, DATA_FIELDS, INCLUDE_SHORTS, CHECK_DELAY, CHANNEL_DELAY = load_config()

# Ensure results.json exists
def ensure_results_file():
    if not os.path.exists(RESULTS_FILE):
        with open(RESULTS_FILE, "w", encoding="utf-8") as f:
            json.dump([], f)  # Initialize with an empty list
    
ensure_results_file()

# Load existing results to enforce channel delay
def load_existing_results():
    existing_videos = set()
    if os.path.exists(RESULTS_FILE) and os.stat(RESULTS_FILE).st_size != 0:
        try:
            with open(RESULTS_FILE, "r", encoding="utf-8") as f:
                data = json.load(f)
                for video in data:
                    existing_videos.add(video.get("video_link", ""))
                    LATEST_VIDEO_TRACKER[video.get("channel_id", "")] = {
                        "video_link": video.get("video_link", ""),
                        "upload_date": video.get("upload_date", "")
                    }
        except (json.JSONDecodeError, FileNotFoundError):
            pass
    log(f"Indexed {len(existing_videos)} previously saved videos to enforce channel delay.", Fore.GREEN)
    return existing_videos

PRINTED_VIDEOS = load_existing_results()

# Function to get the latest video from a single channel
def get_latest_video(channel_id):
    #DEBUG log(f"Checking {channel_id}", Fore.YELLOW)
    
    # If results.json was empty, do not skip any channels
    if len(LATEST_VIDEO_TRACKER) == 0:
        log("results.json is empty. Fetching new videos normally.", Fore.YELLOW)
    else:
        # Skip channels where the last video was checked too recently
        last_video_data = LATEST_VIDEO_TRACKER.get(channel_id, {})
        last_upload_date = last_video_data.get("upload_date", "")
        if last_upload_date:
            last_upload_datetime = datetime.fromisoformat(last_upload_date[:-1]).replace(tzinfo=timezone.utc)  # Remove 'Z'
            time_since_last_upload = datetime.now(timezone.utc) - last_upload_datetime
            if time_since_last_upload < timedelta(hours=CHANNEL_DELAY):
                hours_remaining = CHANNEL_DELAY - (time_since_last_upload.total_seconds() / 3600)
                log(f"Skipping {channel_id}, will check again in {hours_remaining:.1f} hours.", Back.YELLOW + Fore.BLACK)
                return None
    
    url = f"https://www.googleapis.com/youtube/v3/search?part=snippet&channelId={channel_id}&maxResults=1&order=date&type=video&key={API_KEY}"
    response = requests.get(url)
    log(f"Checking {channel_id} - Status Code: {response.status_code}", Fore.YELLOW)
    
    if response.status_code == 200:
        data = response.json()
        
        if "items" in data and len(data["items"]) > 0:
            video = data["items"][0]
            video_id = video["id"]["videoId"]
            video_link = f"https://www.youtube.com/watch?v={video_id}"
            upload_date = video["snippet"].get("publishedAt", "")
            
            if channel_id in LATEST_VIDEO_TRACKER and LATEST_VIDEO_TRACKER[channel_id]["video_link"] == video_link:
                log(f"Skipping {channel_id} - Already checked this video.", Fore.YELLOW)
                return None
            
            log(f"New video found for channel {channel_id}!", Back.GREEN + Fore.BLACK)
            return {
                "channel_id": channel_id,
                "video_link": video_link,
                "upload_date": upload_date
            }
    return None

# Main function to run the script
def main():
    while True:
        try:
            if not os.path.exists(CHANNELS_FILE):
                log(f"error: {CHANNELS_FILE} not found.", Fore.RED)
                time.sleep(CHECK_DELAY * 3600)
                continue
            
            with open(CHANNELS_FILE, "r", encoding="utf-8") as f:
                data = json.load(f)
                channels = data.get("channels", [])
            
            new_videos = []
            for channel_id in channels:
                video_data = get_latest_video(channel_id)
                if video_data:
                    new_videos.append(video_data)
            
            if new_videos:
                with open(RESULTS_FILE, "r", encoding="utf-8") as f:
                    try:
                        results_data = json.load(f)
                    except json.JSONDecodeError:
                        results_data = []
                
                results_data.extend(new_videos)
                with open(RESULTS_FILE, "w", encoding="utf-8") as f:
                    json.dump(results_data, f, indent=4)
                log(f"Saved {len(new_videos)} new videos.", Fore.CYAN)
            else:
                log("No new videos found in this check.", Fore.MAGENTA)
        except Exception as e:
            log(f"error reading {CHANNELS_FILE}: {str(e)}", Fore.RED)
        
        log(f"waiting {CHECK_DELAY} hours before next check...", Fore.BLUE)
        time.sleep(CHECK_DELAY * 3600)

if __name__ == "__main__":
    main()
