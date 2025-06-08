import time
from googleapiclient.discovery import build

API_KEY = 'YOUR_YOUTUBE_API_KEY'
LIVE_VIDEO_ID = 'YOUR_LIVE_VIDEO_ID'

def get_live_chat_id(youtube, video_id):
    response = youtube.videos().list(part='liveStreamingDetails', id=video_id).execute()

    live_details = response.get('items', [])[0].get('liveStreamingDetails', {})
    return live_details.get('activeLiveChatId')

def listen_to_chat(youtube, live_chat_id):
    next_page_token = None

while True:
    response = youtube.liveChatMessages().list(
            liveChatId=live_chat_id,
            part='snippet,authorDetails',
            pageToken=next_page_token
            ).execute()

for message in response.get('items', []):
    user = message['authorDetails']['displayName']
    text = message['snippet']['displayMessage']
    print(f"{user}: {text}")

# 💡 Example "Chat Plays" logic
if 'left' in text.lower():
    print("🎮 Move left")
elif 'right' in text.lower():
    print("🎮 Move right")
elif 'jump' in text.lower():
    print("🎮 Jump!")

next_page_token = response.get('nextPageToken')
time.sleep(2)

def main():
    youtube = build('youtube', 'v3', developerKey=API_KEY)
    chat_id = get_live_chat_id(youtube, LIVE_VIDEO_ID)

    if not chat_id:
        print("❌ Live chat not found. Make sure the stream is live.")
        return

    print(f"✅ Connected to live chat ID: {chat_id}")
    listen_to_chat(youtube, chat_id)

    if __name__ == '__main__':
        main()

