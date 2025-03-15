import json
import time
import os
import requests
from colorama import Fore, Style, init

# initialize colorama
init(autoreset=True)

os.system("cls")
# load api key from config.json
CONFIG_FILE = "config.json"
CHANNELS_FILE = "channels.json"
RESULTS_FILE = "results.json"
PRINTED_VIDEOS = set()

# load api key from config file
def load_config():
    if os.path.exists(CONFIG_FILE):
        with open(CONFIG_FILE, "r", encoding="utf-8") as f:
            return json.load(f).get("API_KEY", "")
    print(Fore.RED + "error: config.json not found or missing api_key")
    return ""

API_KEY = load_config()

# function to get channel id from a youtube url
def get_channel_id(channel_url):
    if "/channel/" in channel_url:
        return channel_url.split("/channel/")[-1]
    
    if "/@" in channel_url:
        username = channel_url.split("/@")[-1]
        url = f"https://www.googleapis.com/youtube/v3/channels?part=id&forHandle=@{username}&key={API_KEY}"
    else:
        print(Fore.RED + f"error: unsupported channel url format: {channel_url}")
        return None
    
    response = requests.get(url)
    if response.status_code == 200:
        data = response.json()
        if "items" in data and len(data["items"]) > 0:
            return data["items"][0]["id"]
    print(Fore.RED + f"error: could not retrieve channel id for {channel_url}")
    return None

# function to get latest video details
def get_latest_video(channel_url):
    channel_id = get_channel_id(channel_url)
    if not channel_id:
        return None
    
    url = f"https://www.googleapis.com/youtube/v3/search?part=snippet&channelId={channel_id}&maxResults=1&order=date&type=video&key={API_KEY}"
    response = requests.get(url)
    if response.status_code == 200:
        data = response.json()
        if "items" in data and len(data["items"]) > 0:
            video = data["items"][0]
            video_id = video["id"]["videoId"]
            video_title = video["snippet"]["title"]
            upload_date = video["snippet"]["publishedAt"]
            video_link = f"https://www.youtube.com/watch?v={video_id}"
            
            # avoid printing duplicate videos
            if video_link in PRINTED_VIDEOS:
                return None
            PRINTED_VIDEOS.add(video_link)
            
            # get video stats
            stats_url = f"https://www.googleapis.com/youtube/v3/videos?part=statistics&id={video_id}&key={API_KEY}"
            stats_response = requests.get(stats_url)
            views = "unknown"
            if stats_response.status_code == 200:
                stats_data = stats_response.json()
                if "items" in stats_data and len(stats_data["items"]) > 0:
                    views = stats_data["items"][0]["statistics"].get("viewCount", "unknown")
            
            # get video tags
            tags_url = f"https://www.googleapis.com/youtube/v3/videos?part=snippet&id={video_id}&key={API_KEY}"
            tags_response = requests.get(tags_url)
            tags = []
            if tags_response.status_code == 200:
                tags_data = tags_response.json()
                if "items" in tags_data and len(tags_data["items"]) > 0:
                    tags = tags_data["items"][0]["snippet"].get("tags", [])
            
            print(Fore.GREEN + f"latest video from {channel_url} retrieved successfully")
            return {
                "channel_url": channel_url,
                "video_title": video_title,
                "video_link": video_link,
                "upload_date": upload_date,
                "views": views,
                "tags": tags
            }
    print(Fore.RED + f"error: could not retrieve video for {channel_url}")
    return None

# function to load existing results
def load_results():
    if os.path.exists(RESULTS_FILE):
        with open(RESULTS_FILE, "r", encoding="utf-8") as f:
            try:
                return json.load(f)
            except json.JSONDecodeError:
                return []
    return []

# function to save new results
def save_results(new_data):
    existing_data = load_results()
    
    if new_data and all(video["video_link"] != new_data["video_link"] for video in existing_data):
        existing_data.append(new_data)
        with open(RESULTS_FILE, "w", encoding="utf-8") as f:
            json.dump(existing_data, f, indent=4)
        print(Fore.CYAN + f"saved new video from {new_data['channel_url']}")
    else:
        print(Fore.YELLOW + f"no new video for {new_data['channel_url']}")

# main loop
def main():
    while True:
        try:
            with open(CHANNELS_FILE, "r", encoding="utf-8") as f:
                data = json.load(f)
                channels = data.get("channels", [])
            
            for channel in channels:
                video_data = get_latest_video(channel)
                if video_data:
                    print(Fore.MAGENTA + json.dumps(video_data, indent=4))
                    save_results(video_data)
        except Exception as e:
            print(Fore.RED + f"error reading {CHANNELS_FILE}: {str(e)}")
        
        print(Fore.BLUE + "waiting 5 minutes before next check...")
        time.sleep(300)

if __name__ == "__main__":
    main()