## Prerequisites

- **Python 3.x** (Download from [python.org](https://www.python.org/))
- Required Python libraries:
  ```bash
  pip install requests colorama isodate
  ```
- A Google Cloud account with **YouTube Data API v3** enabled.

## Setting Up the API Key

1. **Go to [Google Cloud Console](https://console.cloud.google.com/)**.
2. Create a new project (or select an existing one).
3. Enable the **YouTube Data API v3**.
4. Navigate to **APIs & Services > Credentials**.
5. Click **"Create Credentials"** > **"API Key"**.
6. Copy the generated API key.
7. Create a file named `config.json` in the project directory and add the following:
   ```json
   {
       "API_KEY": "YOUR_YOUTUBE_API_KEY"
   }
   ```
   Replace `YOUR_YOUTUBE_API_KEY` with your actual API key.

## Adding YouTube Channels

1. Create a file named `channels.json` in the project directory.
2. Add the YouTube channels you want to track in the following format:
   ```json
   {
    "channels": [
        "UCX6OQ3DkcsbYNE6H8uQQuVA",
        "UCnQC_G5Xsjhp9fEJKuIcrSw",
        "UCXIJgqnII2ZOINSWNOGFThA",
        "UCdFcGPb4xQ6X4QOoRU6ROYw",
        "UCL_f53ZEJxp8TtlOkHwMV9Q"
    ]
    }
   ```
   You can get the channel ID by going to a creator's homepage, viewing the page source (Ctrl+U), then Ctrl+F for the following string: ```property="og:url"``` 
   Following that, you will see the channel's URL. The ID is after the /channel/ part.

## Running the Script

Run the script in a terminal or command prompt:
```bash
python main.py
```

## Understanding the Output

- **Successful Fetch:**
  - The script prints the latest video details in color-coded text.
  - The data is also saved in `results.json`.
- **Errors:**
  - If the API key is incorrect, the script will display an error in red.
  - If the channel ID cannot be retrieved, the script will indicate an issue.

## Storing and Viewing Results

- The script automatically saves all retrieved videos in `results.json`.
- Example output in `results.json`:
  ```json
  [
      {
          "channel_url": "https://www.youtube.com/@MrBeast",
          "video_title": "New Video Title",
          "video_link": "https://www.youtube.com/watch?v=XXXXXXXXXXX",
          "upload_date": "2024-03-14T12:00:00Z",
          "views": "5000000",
          "tags": ["challenge", "fun", "MrBeast"]
      }
  ]
  ```

## Automating the Script

Since the script runs continuously and checks every **5 minutes**, you can:
- **Run it on a server** (e.g., AWS, DigitalOcean, or a Raspberry Pi)
- **Use a task scheduler** to restart it in case of failure (e.g., `cron` on Linux, Task Scheduler on Windows)

## Troubleshooting

- **API Key Not Working:**
  - Ensure the key is correctly placed inside `config.json`.
  - Check if your **YouTube Data API quota** is exceeded.
- **No Video Found:**
  - Verify the **channel URL format** in `channels.json`.
  - Some channels may have **no public videos available**.
- **Script Stops Running:**
  - Restart the script manually or set up a monitoring tool.
