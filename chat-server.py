import time
import os
import httpx
import asyncio
from googleapiclient.discovery import build


class Bot(commands.Bot):
    aHolding = False
    dHolding = False
    rHolding = False

    def __init__(self):
        super().__init__(
            apikey=os.environ['API_KEY'],
            liveid=os.environ['LIVE_ID'],
        )
        self.client = httpx.AsyncClient()

    async def sendInput(self, inputValue, hold):
        if hold:
            inputValue = "hold" + inputValue
            response = await self.client.post(path + ":8084/input", json={"command": inputValue})
            response.raise_for_status()

    async def loopInput(self, inputArray, hold):
        for char in list(inputArray):
            match char:
                case "y":
                    await self.sendInput("enter", hold)
                case "a":
                    if self.dHolding:
                        await self.sendInput("d", False)
                        self.dHolding = False
                        self.aHolding = hold
                    await self.sendInput(char, hold)
                case "d":
                    if self.aHolding:
                        await self.sendInput("a", False)
                        self.aHolding = False
                        self.dHolding = hold
                    await self.sendInput(char, hold)
                case "w" | "s" | "e" | "c" | "x" | "f" | "z" | "q" | "l" | "p" | "j" | "l" | "o":
                    await self.sendInput(char, False)

    async def clear_holds(self):
        if self.dHolding:
            await self.sendInput("d", False)
            self.dHolding = False

        if self.aHolding:
            await self.sendInput("a", False)
            self.aHolding = False

        if self.rHolding:
            await self.sendInput("r", False)
            self.rHolding = False

    async def event_message(self, message):
        if message.echo:
            return

        print(f"{message.author.name}: {message.content}")

        modCommandPrio = False
        if message.author.is_mod:
            match message.content:
                case "esc":
                    await self.clear_holds()
                    modCommandPrio = True
                    await self.sendInput(message.content, False)


        holdIncluded = False
        if message.content.find('h') == 0:
            holdIncluded = True
            message.content = message.content.replace('hold', '')
            message.content = message.content.replace('h', '')

        if modCommandPrio == False and len(message.content.split()) == 1:
            match message.content:
                case "a":
                    if self.dHolding:
                        await self.sendInput("d", False)
                        self.dHolding = False
                        self.aHolding = holdIncluded
                    await self.sendInput(message.content, holdIncluded)
                case "d":
                    if self.aHolding:
                        await self.sendInput("a", False)
                        self.aHolding = False
                        self.dHolding = holdIncluded
                    await self.sendInput(message.content, holdIncluded)
                case "w" | "s" | "e" | "c" | "x" | "f" | "z" | "q" | "l" | "p" | "j" | "l" | "o":
                    await self.sendInput(message.content, False)
                case "tab":
                    await self.clear_holds()
                    await self.sendInput("tab", False)
                case "left":
                    await self.sendInput("a", False)
                case "click" | "lclick" | "leftclick":
                    await self.sendInput("lclick", False)
                case "rclick" | "rightclick":
                    await self.sendInput("rclick", False)
                case "right": 
                    await self.sendInput("d", False)
                case "up": 
                    await self.sendInput("w", False)
                case "down": 
                    await self.sendInput("s", False)
                case "enter" | "y": 
                    await self.clear_holds()
                    await self.sendInput("enter", False)
                case "space" | "jump":
                    await self.sendInput("j", False)
                case "r" | "block":
                    self.rHolding = holdIncluded
                    await self.sendInput("r", holdIncluded)
                #case "walk" | "run" | "w":
                    #self.sendInput("w", holdIncluded)
                case "map":
                    await self.sendInput("m", False)
                case _:
                    await self.loopInput(message.content, False)

                await self.handle_commands(message)




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

